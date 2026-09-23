"""Acquisition layer: the only part of the package that needs the network.

Everything else runs on arrays and local rasters and is covered by the test
suite. This module is deliberately thin, it is excluded from continuous
integration, and it is the piece to run on a machine with open egress.

Two sources are wired up. Sentinel-2 Level-2A surface reflectance comes from
the public STAC catalogue that Element84 hosts over the AWS open data bucket,
which needs no account. CHIRPS daily rainfall comes from the Climate Hazards
Center at Santa Barbara over plain HTTP.
"""

from __future__ import annotations

import datetime as _dt
import pathlib
import urllib.request

STAC_URL = "https://earth-search.aws.element84.com/v1"
SENTINEL2_COLLECTION = "sentinel-2-l2a"
CHIRPS_DAILY = (
    "https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_daily/tifs/p05/"
    "{year}/chirps-v2.0.{year}.{month:02d}.{day:02d}.tif"
)

#: Bands read from Sentinel-2, with the index each one serves.
BANDS = {
    "green": "green",   # B03, NDWI
    "red": "red",       # B04, NDVI
    "nir": "nir",       # B08, NDVI, NDWI, NDMI
    "swir16": "swir16", # B11, NDMI
    "swir22": "swir22", # B12, NBR
    "scl": "scl",       # scene classification, cloud masking
}


def search_sentinel2(bbox, start, end, max_cloud=60, limit=200, stac_url=STAC_URL):
    """List Sentinel-2 Level-2A scenes over `bbox` between two dates.

    Parameters
    ----------
    bbox : tuple
        (west, south, east, north) in degrees.
    start, end : str or datetime.date
        Inclusive bounds, ISO format.
    max_cloud : int
        Scene-level cloud cover ceiling, in per cent. The per-pixel mask in
        `masking` does the real filtering; this only avoids downloading scenes
        that are almost entirely cloud.

    Returns
    -------
    list of dict
        One entry per scene with its identifier, date and asset URLs.

    Notes
    -----
    Needs network access to `stac_url`. Raises whatever `pystac_client` raises
    when the host is unreachable, which is the honest behaviour here: the
    caller should see that the catalogue could not be read rather than get an
    empty list that looks like a legitimate absence of scenes.
    """
    from pystac_client import Client  # imported lazily, so the package loads offline

    client = Client.open(stac_url)
    search = client.search(
        collections=[SENTINEL2_COLLECTION],
        bbox=list(bbox),
        datetime=f"{start}/{end}",
        query={"eo:cloud_cover": {"lt": max_cloud}},
        limit=limit,
    )
    scenes = []
    for item in search.items():
        assets = {
            name: item.assets[key].href
            for name, key in BANDS.items()
            if key in item.assets
        }
        if "scl" not in assets:
            continue
        scenes.append(
            {
                "id": item.id,
                "date": item.datetime.date().isoformat() if item.datetime else None,
                "cloud_cover": item.properties.get("eo:cloud_cover"),
                "assets": assets,
            }
        )
    scenes.sort(key=lambda s: (s["date"] or "", s["id"]))
    return scenes


def chirps_daily_urls(start, end):
    """URLs of the CHIRPS daily Africa rasters covering a date range."""
    if isinstance(start, str):
        start = _dt.date.fromisoformat(start)
    if isinstance(end, str):
        end = _dt.date.fromisoformat(end)
    if end < start:
        raise ValueError("end must not precede start")
    urls, day = [], start
    while day <= end:
        urls.append(
            CHIRPS_DAILY.format(year=day.year, month=day.month, day=day.day)
        )
        day += _dt.timedelta(days=1)
    return urls


def download(url, dest, overwrite=False, timeout=120):
    """Fetch one file, skipping it when a non-empty copy is already there."""
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0 and not overwrite:
        return dest
    with urllib.request.urlopen(url, timeout=timeout) as response:
        payload = response.read()
    if not payload:
        raise OSError(f"empty response from {url}")
    dest.write_bytes(payload)
    return dest
