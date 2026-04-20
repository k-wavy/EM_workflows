import argparse
import re
from pathlib import Path


def parse_idoc(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    pixel_spacing = None
    image_size = None
    tiles = []
    current_image = None

    for line in lines:
        line = line.strip()

        # Global values
        if line.startswith("PixelSpacing") and pixel_spacing is None:
            pixel_spacing = float(line.split("=")[1].strip())

        elif line.startswith("ImageSize"):
            parts = line.split("=")[1].strip().split()
            image_size = (int(parts[0]), int(parts[1]))

        # Image block start
        elif line.startswith("[Image"):
            match = re.search(r"\[Image\s*=\s*(.+)\]", line)
            if match:
                current_image = {
                    "name": match.group(1),
                    "coords": (0, 0)
                }
                tiles.append(current_image)

        # Coordinates inside image block
        elif line.startswith("PieceCoordinates") and current_image:
            parts = line.split("=")[1].strip().split()
            x, y = int(parts[0]), int(parts[1])
            current_image["coords"] = (x, y)

    return pixel_spacing, image_size, tiles


def write_output(idoc_path, output_dir, root_dir):
    match = re.match(r"(\d+)_", idoc_path.stem)
    if not match:
        print(f"Skipping file (unexpected name): {idoc_path.name}")
        return

    layer_num = match.group(1)
    out_name = f"{int(layer_num):04d}.txt"
    out_path = output_dir / out_name

    pixel_spacing, image_size, tiles = parse_idoc(idoc_path)

    if pixel_spacing is None or image_size is None:
        print(f"Skipping file (missing data): {idoc_path.name}")
        return

    resolution = pixel_spacing / 10

    with open(out_path, "w") as f:
        f.write(f"{{ROOT_DIR}}\t{root_dir}\n")
        f.write(f"{{RESOLUTION}}\t{resolution:.3f}\n")
        f.write(f"{{TILE_SIZE}}\t{image_size[0]}\t{image_size[1]}\n")

        for tile in tiles:
            x, y = tile["coords"]
            f.write(f"{tile['name']}\t{x}\t{y}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Convert .idoc files to layer .txt files"
    )
    parser.add_argument("input_folder", help="Folder containing .idoc files")
    parser.add_argument("output_folder", help="Folder to save .txt files")

    args = parser.parse_args()

    input_folder = Path(args.input_folder).resolve()
    output_folder = Path(args.output_folder).resolve()

    if not input_folder.exists():
        print("Input folder does not exist.")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    for idoc_file in input_folder.glob("*.idoc"):
        write_output(idoc_file, output_folder, input_folder)


if __name__ == "__main__":
    main()
