#!/bin/bash

echo  "enter directory with images to montage"
read indir
echo  "enter output directory"
read outdir
echo  "enter overlap as decimal, like 0.08"
read overlap

rows=$(ls $indir/*_r*-c*_*.tif | sed -E 's/.*_r([0-9]+)-c[0-9]+_[0-9]+.tif/\1/g' | sort -n -u | tail -n1)
cols=$(ls $indir/*_r*-c*_*.tif | sed -E 's/.*_r[0-9]+-c([0-9]+)_[0-9]+.tif/\1/g' | sort -n -u | tail -n1)

firstimg=$(ls "$indir"/*.tif | head -n1)
read width height < <(identify -format "%w %h" "$firstimg")

overlap_x=$(echo "$width * $overlap" | bc | awk '{print int($1)}')
overlap_y=$(echo "$height * $overlap" | bc | awk '{print int($1)}')
geometry="+-${overlap_x}+-${overlap_y}"

out_img_name=$(basename $firstimg | cut -d"_" -f1)

images=()
for r in $(seq $rows)
do
	for c in $(seq $cols)
    do
        img=$indir/*_r${r}-c${c}_*.tif
        images+=($img)
    done
done
echo montage ${images[@]} -tile ${cols}x${rows} -geometry $geometry $outdir/${out_img_name}.tif
montage ${images[@]} -tile ${cols}x${rows} -geometry $geometry $outdir/${out_img_name}.tif
