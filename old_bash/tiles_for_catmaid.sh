#!/bin/bash

set -eux
# run optipng on the files, because a pure white tile reduced size 10x, thouh on images with actual content it's much less than that

# keep tile size for now, but in the future retile to make them smaller

# let's use this catmaid tile source
# 4. File-based image stack with zoom level directories
# <sourceBaseUrl><pixelPosition.z>/<zoomLevel>/<row>_<col>.<fileExtension>

# only process images up to zoom level 5, because after that it's too zoomed out
# TODO: determine the max zoom leve dinamically
# TODO: use GNU parallel

if [[ "$#" -ne 2 ]]
then
	echo "Usage: $0 <input_drectory> <output_directory>"
	exit 0
fi

indir=$(realpath "$1")
outdir=$(realpath "$2")

rename_tile() {
	filepath="$1"
	filename="$(basename $1)"

	zoomlevel=$( sed -E 's#.*/mip([0-9])/.*#\1#' <<< $filepath )

	read z row column < <(	echo "$filename" | sed -E 's/^([0-9]+)_tr([0-9]+)-tc([0-9]+)\.png$/\1 \2 \3/')
	
	# decrement all because in catmaid index starts from 0
  # z needs padding, y and x don't
	padding=${#z}
	z=$( printf "%0${padding}d\n" $((10#$z - 1 )) )
  row=$(( $row - 1 ))
  column=$(( $column - 1 ))

  echo "${outdir}/$z/$zoomlevel/"
	[[ -d ${outdir}/$z/$zoomlevel ]] || mkdir -p ${outdir}/$z/$zoomlevel || { echo "Cannot create ${outdir}/$z/$zoomlevel"; exit 1 ; }

	outpath="${outdir}/$z/$zoomlevel/${row}_${column}.png"

	if [[ ! -f "$outpath" ]]
	then
		cp "$filepath" "$outpath"
		optipng "$outpath"
	fi
}

export -f rename_tile
export outdir

find "$indir" -iname "*.png" | sort -V | parallel rename_tile
