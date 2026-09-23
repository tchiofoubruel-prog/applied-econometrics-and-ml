"""Download the Sentinel-2 scenes and CHIRPS rasters for one study area.

Run this where the machine has open network access. Everything downstream
works from the files it leaves on disk.

    python scripts/01_fetch_scenes.py --bbox 34.0 -15.5 35.5 -14.0 \
        --start 2023-11-01 --end 2024-04-30 --out data/raw
"""

from __future__ import annotations

import argparse
import json
import pathlib

from eo_resilience import fetch


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bbox", nargs=4, type=float, required=True,
                        metavar=("WEST", "SOUTH", "EAST", "NORTH"))
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("data/raw"))
    parser.add_argument("--max-cloud", type=int, default=60)
    parser.add_argument("--skip-chirps", action="store_true")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    scenes = fetch.search_sentinel2(
        args.bbox, args.start, args.end, max_cloud=args.max_cloud
    )
    manifest = args.out / "sentinel2_scenes.json"
    manifest.write_text(json.dumps(scenes, indent=1))
    print(f"{len(scenes)} Sentinel-2 scenes listed in {manifest}")

    for scene in scenes:
        for band, href in scene["assets"].items():
            dest = args.out / "sentinel2" / scene["id"] / f"{band}.tif"
            fetch.download(href, dest)
        print(f"  downloaded {scene['id']} ({scene['date']})")

    if not args.skip_chirps:
        urls = fetch.chirps_daily_urls(args.start, args.end)
        for url in urls:
            fetch.download(url, args.out / "chirps" / url.rsplit("/", 1)[-1])
        print(f"{len(urls)} CHIRPS daily rasters downloaded")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
