#!/bin/bash

set -eux

echo "enter directory with images to convert"
read indir
echo $indir
echo "enter output direcory"
read outdir
echo $outdir

# check if paths have spaces or funny stuff, and exit if yes
weird_char=$(printf '%s\n' "$indir" "$outdir" | grep -n '[^A-Za-z0-9._/:,-\\]' | wc -l)
if [[ $weird_char -gt 0 ]]
then
    echo "Funny characters in path. Please remove them."
    exit 1
fi

indir=$(realpath "$indir")
outdir=$(realpath -m "$outdir")

[[ -d "$indir" ]] || { echo "input directory doesn't exist"; exit 1; }

# get tiff files
filepaths=$(find "$indir" -type f -iname "*.tif*")

for filepath in ${filepaths[@]}
do
	filename=$(basename "$filepath")
	# build output path to replicate input directory structure
	shared_path="$indir"
	while [[ "$outdir" != "${shared_path}/"* ]]
	do
		shared_path="${shared_path%/*}"
	done
	outsubdir=${outdir#$shared_path}
	[[ -d "$shared_path/$outsubdir" ]] || mkdir "$shared_path/$outsubdir" || { echo "cannot create $outdir/$outsubdir"; exit 1; }
	convert "$filepath[1]" -resize 512x512 "$shared_path/$outsubdir/$filename"
done
