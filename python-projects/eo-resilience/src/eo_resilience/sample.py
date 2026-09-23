"""One real cube, fetched on demand rather than redistributed.

The sample is a Sentinel-1, Sentinel-2, ERA5 and SRTM cube over a smallholder
plot in Togo, twelve monthly steps from February 2019 to February 2020. It
belongs to the CropHarvest dataset and is licensed CC BY-SA 4.0, which is not
the licence of this repository, so the file is downloaded from its own
repository when a demo or a test asks for it and is never committed here.

    Tseng, G., Zvonkov, I., Nakalembe, C. L. and Kerner, H. (2021).
    CropHarvest: a global dataset for crop-type classification.
    NeurIPS Datasets and Benchmarks Track.
    https://github.com/nasaharvest/cropharvest
"""

from __future__ import annotations

import pathlib
import urllib.request

TOGO_URL = (
    "https://raw.githubusercontent.com/nasaharvest/cropharvest/main/"
    "test/cropharvest/98-togo_2019-02-06_2020-02-01.tif"
)
TOGO_NAME = "98-togo_2019-02-06_2020-02-01.tif"
TOGO_LICENCE = "CC BY-SA 4.0, CropHarvest (Tseng et al. 2021)"

#: Roughly where the plot sits, for a sanity check after download.
TOGO_APPROX_LONLAT = (1.4228, 7.7195)


def cache_dir():
    """Where downloaded samples are kept, outside the repository tree."""
    return pathlib.Path.home() / ".cache" / "eo_resilience"


def togo_cube_path(dest=None, timeout=120):
    """Return a local path to the Togo cube, downloading it once if needed."""
    dest = pathlib.Path(dest) if dest is not None else cache_dir() / TOGO_NAME
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(TOGO_URL, timeout=timeout) as response:
        payload = response.read()
    if len(payload) < 100_000:
        raise OSError(f"the download from {TOGO_URL} looks truncated")
    dest.write_bytes(payload)
    return dest


def togo_cube(dest=None):
    """Read the Togo sample as a :class:`~eo_resilience.cube.Cube`."""
    from . import cube as _cube

    return _cube.read(togo_cube_path(dest))
