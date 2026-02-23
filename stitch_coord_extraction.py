#!/usr/bin/env python3

# script for generating stitch coordinates from the data
# assumes files were already sorted by sort.sh

# written by David Hug and Sanja Jasek

# Import necessary tools
import sys
import os
import re
import argparse
from PIL import Image

# This line is needed to let Python open huge image files without crashing
Image.MAX_IMAGE_PIXELS = None

# --- Functions ---

# Function to go through all image files in a folder and create a coordinate file
def create_stitch_coordinate_file_from_dir(input_dir, output_dir, resolution_nm, overlap_percentage):
    
    # Check if the input folder exists (Basic check)
    if not os.path.isdir(input_dir):
        print(f"Folder '{input_dir}' not found. Skipping.")
        return

    # This is a pattern to find the row (r) and column (c) from the filename
    # e.g., for '_r10-c5_', it finds 10 and 5
    pattern = re.compile(r'_r(\d+)-c(\d+)_')
    
    # Get a list of all files in the folder that end with .tif
    tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]

    # Check if there are any TIFF files
    if not tiff_files:
        print(f"No TIFF files in '{input_dir}'. Skipping.")
        return

    # Open the first image to figure out the size of each tile (tile)
    first_image_path = os.path.join(input_dir, tiff_files[0])
    img = Image.open(first_image_path)
    tile_width_px, tile_height_px = img.size
    img.close()
    print(f"Tile size is: {tile_height_px} x {tile_width_px} pixels.")

    # Calculate how many pixels to step for the next tile
    # This accounts for the overlap percentage
    x_step = int(tile_width_px * (1 - overlap_percentage))
    y_step = int(tile_height_px * (1 - overlap_percentage))

    # A list to store the row, column, and filename for each tile
    tiles_to_write = []
    for filename in tiff_files:
        # Try to find the row and column in the filename
        match = pattern.search(filename)
        if match:
            # Get the row and column numbers and save the info
            row = int(match.group(1))
            col = int(match.group(2))
            tiles_to_write.append((row, col, filename))

    # Sort the tiles by row, then by column (like reading a book)
    tiles_to_write.sort(key=lambda x: (x[0], x[1]))
    
    # Get the name of the folder to use as the name of the output file
    section_name = os.path.basename(os.path.normpath(input_dir))
    output_filename = f"{section_name}.txt"
    output_filepath = os.path.join(output_dir, output_filename)

    # Make the output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open the output file to write the coordinates
    with open(output_filepath, 'w') as f:
        # Write some header info needed for the stitching program
        f.write(f"{{ROOT_DIR}}\t{input_dir}\n")
        f.write(f"{{RESOLUTION}}\t{resolution_nm}\n")
        f.write(f"{{TILE_SIZE}}\t{tile_height_px}\t{tile_width_px}\n")

        # Now write the coordinates for each tile
        for row, col, filename in tiles_to_write:
            # Calculate the X and Y coordinates (in pixels) for the top-left corner
            # Row and column numbers usually start from 1, so we subtract 1
            x_coord = (col - 1) * x_step
            y_coord = (row - 1) * y_step
            
            # Write the filename and its coordinates
            f.write(f"{filename}\t{x_coord}\t{y_coord}\n")

    print(f"Created coordinate file: '{output_filepath}'.")

# --- Main Part of the Script ---

def main():
    # Set up the command-line arguments tool
    parser = argparse.ArgumentParser(description="Makes files with image stitch coordinates.")

    parser.add_argument(
        "--input",
        type=str,
        help="Path to the image data folder. Defaults to './raw_data'. Assumes files are already sorted with sort.sh.",
        default=None
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output folder for stitch coordinates. Defaults to './stitch/stitch_coord'.",
        default=None
    )

    parser.add_argument(
        "--resolution",
        type=float,
        required=True,
        help="Resolution in nm/px. REQUIRED."
    )

    parser.add_argument(
        "--overlap",
        type=float,
        required=True,
        help="Tile overlap as a fraction (e.g., 0.1 for 10% overlap). REQUIRED."
    )

    # Read the arguments given by the user
    args = parser.parse_args()

    # Get the path to where this script is running
    # use this as a default path if path is not given
    MY_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

    # Use the overlap value directly
    OVERLAP = args.overlap

    resolution = args.resolution

    # Validate overlap
    if not (0 <= OVERLAP < 1):
        print("Error: --overlap must be between 0 and 1.")
        sys.exit(1)

    # Determine input/output folders
    raw_data_dir = args.input or os.path.join(MY_PROJECT_DIR, "raw_data")
    output_stitch_dir = args.output or os.path.join(MY_PROJECT_DIR, "stitch", "stitch_coord")

    # Check input folder
    if not os.path.exists(raw_data_dir):
        print(f"Error: The input folder '{raw_data_dir}' doesn't exist.")
        sys.exit(1)
        
    if not os.listdir(raw_data_dir):
        print(f"'{raw_data_dir}' is empty")
        sys.exit(1)

    print(f"Starting to check folders in: {raw_data_dir}")
    print(f"Using overlap: {OVERLAP}")
    print(f"Output directory: {output_stitch_dir}")

    # Loop through section folders
    for section_dir in os.listdir(raw_data_dir):
        full_section_path = os.path.join(raw_data_dir, section_dir)
        
        if os.path.isdir(full_section_path):
            print(f"\nProcessing folder: {section_dir}")
            
            tiff_files = [f for f in os.listdir(full_section_path) if f.endswith('.tif')]
            if not tiff_files:
                print("No TIFF files found. Skipping.")
                continue
            
            first_file = tiff_files[0]
            first_image_path = os.path.join(full_section_path, first_file)
            

            # Create coordinate file
            create_stitch_coordinate_file_from_dir(
                input_dir=full_section_path,
                output_dir=output_stitch_dir,
                resolution_nm=resolution,
                overlap_percentage=OVERLAP
            )



# Run the main function when the script starts
if __name__ == "__main__":
    main()
