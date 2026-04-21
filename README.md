Image Processing & Stitching Pipeline Toolkit
=============================================

This toolkit contains a collection of Python scripts designed to manage, sort, stitch, evaluate, and optimize large sets of electron microscopy (or similar) scan images.

These scripts map to a standard Volume Electron Microscopy (vEM) pipeline, transforming unorganized raw microscope data into fully aligned 3D volumes ready for web-based exploration (like CATMAID or Neuroglancer/OME-Zarr).

🗺️ Pipeline Workflow & Use Cases
---------------------------------

A typical workflow using this toolkit involves the following stages:

1.  **Pre-processing & Sorting:** Organize raw instrument dumps into sequential layer folders and (if necessary) downcast 16-bit data to 8-bit for broader compatibility.

2.  **Coordinate Extraction:** Generate `feabas` or similar stitch-coordinate `.txt` files defining how tiles overlap, either by parsing file names, FIBICS metadata, or SerialEM `.idoc` files.

3.  **Stitching & Alignment:** Run the orchestrated `feabas` pipeline to match, optimize, and render the stitched layers and align the 3D volume.

4.  **Quality Assurance (QA) & Previews:** Generate montages, downsampled previews, and cyan/magenta overlay checks to quickly assess the quality of the alignments.

5.  **Export & Distribution:** Compress and re-chunk the final volumes into web-friendly formats (CATMAID zoom-pyramids or OME-Zarr).

Stage 1: Pre-processing & Sorting
---------------------------------

### `sort.py`

**Description:** Analyzes unorganized raw scans (e.g., `Tile_r1-c1_S_002_12345.tif`), figures out consecutive sequence numbering while automatically compensating for gaps (lost/damaged sections), pads with leading zeros, and reorganizes them safely into sequential `<layer>` sub-folders. Also generates a `.tsv` map mapping raw names to new logical names.

-   **Inputs:** Command-line arguments `<input_directory>` and `<output_directory>`.

-   **Outputs:** Files copied into sequential layer folders and a `renaming_map.tsv` file.

-   **Example Usage:**

    ```
    python3 sort.py ./raw_dump ./sorted_layers

    ```

### `int16_to_unint32.py`

**Description:** Despite the filename, this script downcasts 16-bit TIFFs to normalized 8-bit (`uint8`) TIFFs. This is often required because many visualization and alignment tools struggle with signed/unsigned 16-bit data. It can normalize per-image or use a global min/max across the dataset.

-   **Inputs:** Command-line arguments for `<input_dir>`, `<output_dir>`, and optionally `<global_min>` and `<global_max>`.

-   **Outputs:** 8-bit normalized `.tif` files.

-   **Example Usage:**

    ```
    python3 int16_to_unint32.py ./raw_16bit ./processed_8bit 0 65535

    ```

Stage 2: Coordinate Extraction
------------------------------

To stitch tiles together, the alignment engine needs to know roughly where each tile is located. Choose **one** of the following extraction scripts based on your microscope's metadata format.

### `stitch_coord_extraction.py`

**Description:** Generates stitch coordinates based strictly on filename grid patterns (e.g., `_rX-cY_`). It assumes tiles are laid out in a perfect grid and calculates physical coordinates by multiplying the tile size by a user-provided overlap percentage.

-   **Inputs:** `--input` (directory of sorted layers), `--output`, `--resolution` (nm/px), and `--overlap` (decimal, e.g., 0.1 for 10%).

-   **Outputs:** `{section_name}.txt` coordinate files.

-   **Example Usage:**

    ```
    python3 stitch_coord_extraction.py --input ./sorted_layers --output ./stitch_coord --resolution 4.0 --overlap 0.1

    ```

### `stitch_coord_from_metadata.py`

**Description:** Generates stitch coordinates by extracting FIBICS metadata (Tag 51023) embedded directly inside the TIFF headers. It calculates highly accurate origin-relative pixel offsets based on the stage coordinates (`MosaicInfo/X` and `Y`).

-   **Inputs:** `-i` (Input directory containing numbered subfolders), `-o` (Output directory).

-   **Outputs:** `{folder_name}.txt` coordinate files containing `{RESOLUTION}` and `{TILE_SIZE}` headers.

-   **Example Usage:**

    ```
    python3 stitch_coord_from_metadata.py -i ./sorted_layers -o ./stitch_coord

    ```

### `stitch_coord_TEM.py`

**Description:** Generates stitch coordinates by parsing SerialEM `.idoc` files. It extracts global `PixelSpacing` and `ImageSize` values, as well as individual `PieceCoordinates` for each tile.

-   **Inputs:** `input_folder` (containing `.idoc` files) and `output_folder`.

-   **Outputs:** `{layer_num}.txt` coordinate files.

-   **Example Usage:**

    ```
    python3 stitch_coord_TEM.py ./idoc_files ./stitch_coord

    ```

Stage 3: Stitching & Alignment
------------------------------

### `run_all.py`

**Description:** An automation orchestrator wrapper specifically tailored for the `feabas` stitching and alignment tool suite. Executes matching, optimization, rendering, and downsampling sequences linearly across the Stitching, Thumbnail, and Alignment stages.

-   **Inputs:** Command-line argument `<path_to_feabas_repo>`.

-   **Outputs:** Console stream tracking feabas pipeline operations; generates aligned datasets inside the feabas project structure.

-   **Execution Details:** Aborts if any pipeline stage fails.

-   **Example Usage:**

    ```
    python3 run_all.py /path/to/feabas

    ```

Stage 4: Quality Assurance & Visualization
------------------------------------------

### `overlay_layers.py`

**Description:** A QA/alignment checker tool. Takes consecutive rendered layers, converts them to Cyan and Magenta color lookup tables (CLUTs), and blends them at 50% opacity into a single JPEG. Misalignments appear as cyan/magenta fringes, while perfectly aligned structures appear grayscale.

-   **Inputs:** Command-line arguments `<input_directory>` and `<output_directory>`.

-   **Outputs:** `.jpg` blended overlays for consecutive image pairs named `{num1}-{num2}.jpg`.

-   **Execution Tools:** Requires ImageMagick (`convert`) and `cyanCLUT.png` / `magentaCLUT.png` in the runtime directory.

-   **Example Usage:**

    ```
    python3 overlay_layers.py ./aligned_tiles ./overlay_checks

    ```

### `montage.py` & `montage2.py`

**Description:** Combines individual tile pieces of a layer into a single stitched TIFF layer for quick visual review prior to complex alignment. `montage.py` iterates over multiple subfolders, while `montage2.py` operates on a single flat directory and takes custom overlap input.

-   **Inputs:** Interactive standard input (stdin) for directories and overlap limits.

-   **Outputs:** Stitched `.tif` preview files.

-   **Execution Tools:** Requires ImageMagick (`identify`, `montage`).

-   **Example Usage:**

    ```
    python3 montage.py
    # Follow interactive prompts

    ```

### `create_smalls.py` & `create_smalls2.py`

**Description:** Downsamples raw multi-page TIFF images into smaller 512x512 images for rapid thumbnail viewing. `create_smalls2.py` differs by supporting deeply nested, recursive directory structures.

-   **Inputs:** Interactive standard input (stdin) for I/O paths.

-   **Outputs:** Resized 512x512 images preserving input directory structures.

-   **Execution Tools:** Requires ImageMagick (`convert`).

-   **Example Usage:**

    ```
    python3 create_smalls2.py
    # Follow interactive prompts

    ```

Stage 5: Export & Web Viewer Preparation
----------------------------------------

### `tiles_for_catmaid.py`

**Description:** Reorganizes and optimizes images for ingestion into CATMAID. Translates standard tile names into CATMAID's required zoom level directory structure: `<z>/<zoomLevel>/<row>_<col>.png` (decrementing coordinate indices by 1 since CATMAID is 0-indexed).

-   **Inputs:** Command-line arguments `<input_directory>` and `<output_directory>`.

-   **Outputs:** Highly compressed `.png` tiles properly nested for CATMAID ingestion.

-   **Execution Tools:** Requires `optipng`.

-   **Example Usage:**

    ```
    python3 tiles_for_catmaid.py ./mip_renders ./catmaid_stack

    ```

### `convert_to_OME-Zarr.py`

**Description:** Converts a finished Neuroglancer precomputed volume into the modern Next-Generation File Format (NGFF) OME-Zarr. It extracts multiple mip/scale levels, processes the dask arrays (dropping empty channel axes), and writes explicit coordinate transformations and units (nanometers).

-   **Inputs:** Positional arguments `<input_precomputed>` and `<output_zarr>`, with optional `--chunks` sizing.

-   **Outputs:** A standard `.zarr` directory tree viewable in tools like MoBIE or Napari.

-   **Dependencies:** `cloudvolume`, `dask`, `ome_zarr`.

-   **Example Usage:**

    ```
    python3 convert_to_OME-Zarr.py ./my_neuroglancer_volume ./output.zarr --chunks 2048 2048 16

    ```