"""Earth observation features for smallholder resilience modelling.

The package is split in two layers. Everything in `masking`, `indices`,
`compositing`, `extraction`, `validation` and `uncertainty` is pure computation
on arrays and rasters, so it runs and is tested without network access. Network
access is confined to `fetch`, which is excluded from continuous integration.
"""

__version__ = "0.1.0"

from . import (
    bands,
    compositing,
    cube,
    extraction,
    indices,
    masking,
    phenology,
    sample,
    uncertainty,
    validation,
)

__all__ = [
    "bands",
    "compositing",
    "cube",
    "extraction",
    "indices",
    "masking",
    "phenology",
    "sample",
    "uncertainty",
    "validation",
]
