#!/usr/bin/env python3

import os
import re
import sys
import glob
import subprocess

def get_dimensions(filepath):
    """Get width and height using ImageMagick identify."""
    cmd = ["identify", "-format", "%w %h", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    w, h = result.stdout.strip().split()
    return int(w), int(h)

def main():
    print("enter directory with images to montage")
    indir = input().strip()
    
    print("enter output directory")
    outdir = input().strip()
    
    print("enter overlap as decimal, like 0.08")
    overlap_str = input().strip()
    try:
        overlap = float(overlap_str)
    except ValueError:
        print("Invalid overlap value. Please enter a decimal like 0.08")
        sys.exit(1)

    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    rc_pattern = re.compile(r'_r(\d+)-c(\d+)_\d+\.tif')
    tifs = glob.glob(os.path.join(indir, "*_r*-c*_*.tif"))
    if not tifs:
        print("No matching tiff files found in the directory.")
        sys.exit(1)

    max_row, max_col = 0, 0
    for t in tifs:
        match = rc_pattern.search(os.path.basename(t))
        if match:
            max_row = max(max_row, int(match.group(1)))
            max_col = max(max_col, int(match.group(2)))

    firstimg = sorted(glob.glob(os.path.join(indir, "*.tif")))[0]
    width, height = get_dimensions(firstimg)

    overlap_x = int(width * overlap)
    overlap_y = int(height * overlap)
    geometry = f"+-{overlap_x}+-{overlap_y}"

    out_img_name = os.path.basename(firstimg).split("_")[0]

    images = []
    for r in range(1, max_row + 1):
        for c in range(1, max_col + 1):
            pattern = os.path.join(indir, f"*_r{r}-c{c}_*.tif")
            matches = glob.glob(pattern)
            images.extend(matches)

    out_file = os.path.join(outdir, f"{out_img_name}.tif")
    cmd = ["montage"] + images + ["-tile", f"{max_col}x{max_row}", "-geometry", geometry, out_file]
    
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()