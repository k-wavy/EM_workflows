#!/usr/bin/env python3

import os
import sys
import re
import subprocess
from pathlib import Path
import concurrent.futures

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def process_tile(filepath_str, outdir_path):
    filepath = Path(filepath_str)
    filename = filepath.name

    # Extract zoom level from path: /mip[0-9]/
    zoom_match = re.search(r'/mip([0-9])/.*', filepath_str)
    if not zoom_match:
        return
    zoomlevel = zoom_match.group(1)

    # Extract coordinates from filename
    # E.g. "001_tr2-tc3.png"
    name_match = re.search(r'^([0-9]+)_tr([0-9]+)-tc([0-9]+)\.png$', filename)
    if not name_match:
        return
        
    z_raw, row_raw, col_raw = name_match.groups()
    
    z_num = int(z_raw)
    row = int(row_raw)
    column = int(col_raw)
    
    # decrement all because in catmaid index starts from 0
    # z needs padding
    padding = len(z_raw)
    z_str = f"{(z_num - 1):0{padding}d}"
    row -= 1
    column -= 1

    target_dir = outdir_path / z_str / zoomlevel
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        print(f"Cannot create {target_dir}")
        return

    outpath = target_dir / f"{row}_{column}.png"

    if not outpath.exists():
        import shutil
        shutil.copy2(filepath, outpath)
        try:
            # run optipng to compress image
            subprocess.run(["optipng", str(outpath)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"optipng failed for {outpath}: {e}")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_directory> <output_directory>")
        sys.exit(0)

    indir = Path(sys.argv[1]).resolve()
    outdir = Path(sys.argv[2]).resolve()

    if not indir.is_dir():
        print(f"Input directory {indir} does not exist.")
        sys.exit(1)

    # Find and sort files
    png_files = []
    for ext in ["*.png", "*.PNG"]:
        png_files.extend(indir.rglob(ext))
    
    png_files = sorted([str(p) for p in png_files], key=natural_sort_key)

    # Use multiprocessing to simulate GNU parallel
    max_workers = os.cpu_count() or 4
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_tile, f, outdir) for f in png_files]
        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            future.result() # Raises exceptions if any occurred inside the thread/process

if __name__ == "__main__":
    main()