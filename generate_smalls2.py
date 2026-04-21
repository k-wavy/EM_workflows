import os
import re
import sys
import subprocess
from pathlib import Path

def main():
    print("enter directory with images to convert")
    indir = input().strip()
    print(indir)
    
    print("enter output direcory")
    outdir = input().strip()
    print(outdir)

    # Check if paths have spaces or funny characters
    funny_char_pattern = re.compile(r'[^A-Za-z0-9._/:,\-\\]')
    if funny_char_pattern.search(indir) or funny_char_pattern.search(outdir):
        print("Funny characters in path. Please remove them.")
        sys.exit(1)

    # Resolve absolute paths
    indir_path = Path(indir).resolve()
    outdir_path = Path(outdir).resolve()

    if not indir_path.is_dir():
        print("input directory doesn't exist")
        sys.exit(1)

    # Recursively find all .tif files (case-insensitive, includes .tiff)
    # rglob handles the equivalent of `find ... -iname "*.tif*"`
    filepaths = []
    for ext in ["*.tif*", "*.TIF*"]:
        filepaths.extend(indir_path.rglob(ext))
    
    # Deduplicate in case of overlapping patterns
    filepaths = list(set(filepaths))

    for filepath in filepaths:
        filename = filepath.name
        
        # Build output path to replicate input directory structure
        # Find relative path from the input directory root
        try:
            rel_path = filepath.parent.relative_to(indir_path)
        except ValueError:
            # Fallback if not a subpath
            rel_path = Path("")

        outsubdir_full = outdir_path / rel_path
        
        # Create corresponding output directory
        try:
            outsubdir_full.mkdir(parents=True, exist_ok=True)
        except OSError:
            print(f"cannot create {outsubdir_full}")
            sys.exit(1)
            
        out_filepath = outsubdir_full / filename
        
        # Execute ImageMagick convert
        cmd = ["convert", f"{filepath}[1]", "-resize", "512x512", str(out_filepath)]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {filepath}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()