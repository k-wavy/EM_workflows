#!/bin/bash

set -eux

echo  "enter directory with images to convert"
read indir
echo "$indir"
echo  "enter output direcory"
read outdir
echo $outdir

for insubdir in "$indir"/*
do
	layer="$(basename $insubdir)"
	if [[ ! -d "$outdir/$layer" ]]
	then
		mkdir "$outdir/$layer"
	fi
	for imgp in "$insubdir"/*
	do
		imgname="$(basename $imgp)"
		convert "$imgp[1]" -resize 512x512 "${outdir}/$layer/$imgname"
	done
done
