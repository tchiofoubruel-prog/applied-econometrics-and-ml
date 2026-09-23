"""Band layout of the multi-source cubes used for smallholder work.

The layout follows the convention NASA Harvest established for CropHarvest and
reused in Presto: one GeoTIFF per location, holding a monthly time series of
dynamic bands followed by the static terrain bands. Four sources are stacked,
which is what makes a cube multi-modal in the sense the fellowship call uses.

Sentinel-1 carries the radar backscatter, which sees through cloud and responds
to canopy structure and surface moisture. Sentinel-2 carries the optical and
short-wave infrared reflectance behind the vegetation and water indices. ERA5
carries thermal stress and rainfall. SRTM carries the terrain.
"""

from __future__ import annotations

S1_BANDS = ["VV", "VH"]
S2_BANDS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B10", "B11", "B12"]
ERA5_BANDS = ["temperature_2m", "total_precipitation"]
SRTM_BANDS = ["elevation", "slope"]

DYNAMIC_BANDS = S1_BANDS + S2_BANDS + ERA5_BANDS
STATIC_BANDS = SRTM_BANDS
RAW_BANDS = DYNAMIC_BANDS + STATIC_BANDS

#: Which source each band belongs to, for grouped feature importance.
SOURCE_OF = {
    **{b: "sentinel1" for b in S1_BANDS},
    **{b: "sentinel2" for b in S2_BANDS},
    **{b: "era5" for b in ERA5_BANDS},
    **{b: "srtm" for b in SRTM_BANDS},
}

#: Bands named by the fellowship call, grouped by the signal they carry.
SIGNAL_GROUPS = {
    "water_dynamics": ["B3", "B8", "B11", "total_precipitation", "VV", "VH"],
    "thermal_stress": ["temperature_2m", "B12"],
    "landscape_structure": ["elevation", "slope", "VH"],
}


#: Bands dropped from the processed feature vectors: B1 is the aerosol band
#: and B10 the cirrus band, neither of which carries surface information.
REMOVED_BANDS = ["B1", "B10"]

#: Layout of one row of a processed CropHarvest array: the dynamic bands that
#: survive the removal above, then the two static terrain bands repeated at
#: every time step, then the precomputed NDVI.
PROCESSED_BANDS = (
    [b for b in DYNAMIC_BANDS if b not in REMOVED_BANDS] + STATIC_BANDS + ["NDVI"]
)


def processed_index(name):
    """Position of a band inside one row of a processed array."""
    try:
        return PROCESSED_BANDS.index(name)
    except ValueError as exc:
        raise KeyError(f"{name!r} is not a processed band") from exc


def band_index(name):
    """Position of a dynamic band inside one time step."""
    try:
        return DYNAMIC_BANDS.index(name)
    except ValueError as exc:
        raise KeyError(f"{name!r} is not a dynamic band") from exc


def static_index(name):
    """Position of a static band inside the trailing block."""
    try:
        return STATIC_BANDS.index(name)
    except ValueError as exc:
        raise KeyError(f"{name!r} is not a static band") from exc


def expected_band_count(n_timesteps):
    """How many raster bands a cube of `n_timesteps` months should hold."""
    if n_timesteps < 1:
        raise ValueError("a cube needs at least one time step")
    return n_timesteps * len(DYNAMIC_BANDS) + len(STATIC_BANDS)


def infer_timesteps(n_raster_bands):
    """Recover the number of months from the band count of a cube."""
    dyn, sta = len(DYNAMIC_BANDS), len(STATIC_BANDS)
    if n_raster_bands < dyn + sta:
        raise ValueError(f"{n_raster_bands} bands is too few for one time step")
    if (n_raster_bands - sta) % dyn:
        raise ValueError(
            f"{n_raster_bands} bands do not divide into {dyn} dynamic bands "
            f"plus {sta} static ones"
        )
    return (n_raster_bands - sta) // dyn
