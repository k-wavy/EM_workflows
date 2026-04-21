#!/bin/bash

#set -eux

echo  "enter directory with images to montage"
read indir
echo  "enter output directory"
read outdir

overlap=0.08

for insubdir in "$indir"/*
do
	layer="$(basename $insubdir)"
	rows=$(ls $insubdir/*_r*-c*_*.tif | sed -E 's/.*_r([0-9]+)-c[0-9]+_[0-9]+.tif/\1/g' | sort -n -u | tail -n1)
	cols=$(ls $insubdir/*_r*-c*_*.tif | sed -E 's/.*_r[0-9]+-c([0-9]+)_[0-9]+.tif/\1/g' | sort -n -u | tail -n1)

	firstimg=$(ls "$insubdir"/*.tif | head -n1)
    read width height < <(identify -format "%w %h" "$firstimg")

	overlap_x=$(echo "$width * $overlap" | bc | awk '{print int($1)}')
	overlap_y=$(echo "$height * $overlap" | bc | awk '{print int($1)}')
	geometry="+-${overlap_x}+-${overlap_y}"

	images=()
	for r in $(seq $rows)
	do
		for c in $(seq $cols)
		do
			img=$insubdir/*_r${r}-c${c}_*.tif
			images+=($img)
		done
	done
	echo montage ${images[@]} -tile ${cols}x${rows} -geometry $geometry $outdir/${layer}.tif
	montage ${images[@]} -tile ${cols}x${rows} -geometry $geometry $outdir/${layer}.tif
done
