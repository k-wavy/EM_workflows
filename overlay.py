#!/usr/bin/env python3

import os
import sys
import re
import subprocess
from pathlib import Path

def natural_sort_key(s):
    """Key function for natural sorting string with numbers."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_directory> <output_directory>")
        sys.exit(0)

    indir = sys.argv[1]
    outdir = sys.argv[2]

    # Quick and dirty way to assess alignment quality
    # for each folder get tr4-cr4 tile from mip2
    
    # Get file list and sort with version/natural sort
    in_path = Path(indir)
    images = []
    for ext in ["*_tr4-tc4.jpg", "*_tr4-tc4.JPG"]:
        images.extend(in_path.rglob(ext))
    
    images = sorted([str(p) for p in images], key=natural_sort_key)

    if not images:
        print("no images found")
        sys.exit(1)

    # Put everything together into output folder
    os.makedirs(outdir, exist_ok=True)

    num_img = len(images)

    for i in range(num_img - 1):
        img1 = images[i]
        img2 = images[i + 1]
        
        namebase_img1 = os.path.basename(img1)
        namebase_img2 = os.path.basename(img2)

        img1cyan = os.path.join(outdir, f"{namebase_img1}_cyan.jpg")
        img2magenta = os.path.join(outdir, f"{namebase_img2}_magenta.jpg")

        number_img1 = namebase_img1.split("_")[0]
        number_img2 = namebase_img2.split("_")[0]

        overlay_path = os.path.join(outdir, f"{number_img1}-{number_img2}.jpg")

        try:
            # Convert first to cyan LUT and second to magenta LUT
            subprocess.run(["convert", img1, "cyanCLUT.png", "-clut", img1cyan], check=True)
            subprocess.run(["convert", img2, "magentaCLUT.png", "-clut", img2magenta], check=True)

            # Overlay them
            cmd = [
                "convert", img1cyan, img2magenta, 
                "-compose", "blend", 
                "-define", "compose:args=50,50", 
                "-composite", overlay_path
            ]
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Error processing {img1} and {img2}: {e}")
            sys.exit(1)
            
        finally:
            # Don't leave intermediate files laying around
            if os.path.exists(img1cyan):
                os.remove(img1cyan)
            if os.path.exists(img2magenta):
                os.remove(img2magenta)

if __name__ == "__main__":
    main()