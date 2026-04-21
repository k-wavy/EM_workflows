import os
import sys
import re
import shutil
from pathlib import Path

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_directory> <output_directory>")
        sys.exit(0)

    indir = sys.argv[1]
    outdir = sys.argv[2]

    in_path = Path(indir)
    out_path = Path(outdir)

    # find all .tif files and sort them naturally
    images = []
    for ext in ["*.tif", "*.TIF"]:
        images.extend(in_path.rglob(ext))
    images = sorted([str(p) for p in images], key=natural_sort_key)

    # check if paths have funny characters
    funny_char_pattern = re.compile(r'[^A-Za-z0-9._/:,\-\\]')
    if funny_char_pattern.search(outdir) or any(funny_char_pattern.search(img) for img in images):
        print("Funny characters in path. Please remove them.")
        sys.exit(1)

    os.makedirs(outdir, exist_ok=True)
    info_file = os.path.join(outdir, "renaming_map.tsv")

    # Get number of layers (equivalent to finding unique directory paths that contain a Tile_r file)
    unique_prefixes = set()
    for img in images:
        match = re.search(r'(.*)/Tile_r', img)
        if match:
            unique_prefixes.add(match.group(1))
    
    num_layers_str = str(len(unique_prefixes))
    padding = len(num_layers_str)

    previous_layer_filename = None
    previous_layer_actual = None
    previous_folder = None

    filename_regex = re.compile(r'Tile_(r[0-9]+-c[0-9]+)_S_([0-9]+)_([0-9]+)\.tif')

    for image in images:
        img_name = os.path.basename(image)
        match = filename_regex.search(img_name)
        
        if not match:
            print(f"{img_name} doesn't follow naming convention. Rename failed.")
            sys.exit(1)
            
        coord, layer_filename_raw, id_num = match.groups()
        layer_filename_num = int(layer_filename_raw)
        
        # Zero-pad the layer filename to match length
        layer_filename = f"{layer_filename_num:0{padding}d}"
        
        folder = os.path.dirname(image)
        if previous_folder is None:
            previous_folder = folder
            
        if previous_layer_filename is None:
            # First iteration setup
            previous_layer_filename_num = layer_filename_num - 1
            previous_layer_filename = f"{previous_layer_filename_num:0{padding}d}"
        else:
            previous_layer_filename_num = int(previous_layer_filename)

        if folder == previous_folder:
            difference = layer_filename_num - previous_layer_filename_num
        else:
            difference = 1

        if previous_layer_actual is None:
            previous_layer_actual = previous_layer_filename
            
        previous_layer_actual_num = int(previous_layer_actual)
        new_layer_num = previous_layer_actual_num + difference
        new_layer = f"{new_layer_num:0{padding}d}"

        new_layer_dir = os.path.join(outdir, new_layer)
        os.makedirs(new_layer_dir, exist_ok=True)

        new_img_name = f"{new_layer}_{coord}_{id_num}.tif"
        out_filepath = os.path.join(new_layer_dir, new_img_name)

        if not os.path.isfile(out_filepath):
            try:
                shutil.copy2(image, out_filepath)
                with open(info_file, 'a') as f:
                    f.write(f"{image}\t{out_filepath}\n")
            except OSError as e:
                print(f"Failed to copy {image}: {e}")
                sys.exit(1)

        previous_layer_filename = layer_filename
        previous_layer_actual = new_layer
        previous_folder = folder

if __name__ == "__main__":
    main()