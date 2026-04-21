#!/bin/bash

#set -eux

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 0
fi

indir="$1"
outdir="$2"

# quick and dirty way to assess alignment quality

# for each folder get tr4-cr4 tile from mip2
# arbitrary choice for dataset I'm testing

# folder structure:
# mip2/0001_002/002_tr4-cr4.jpg
# get file list
readarray -t images  < <(find "$indir" -iname "*_tr4-tc4.jpg" | sort -V)

# TODO: give find arguments for input

# put everything together into output folder
[[ -d "$outdir" ]] || mkdir -p "$outdir" || { echo "can't create $outdir"; exit 1; }

# don't leave intermediate files laying around if program dies or is killed
function cleanup {
	[[ -f "$img1cyan" ]] && rm "$img1cyan"
	[[ -f "$img2magenta" ]] && rm "$img2magenta"
}

trap cleanup EXIT

num_img=${#images[@]}
if [[ $num_img -eq 0 ]]
then
	echo "no images found"
	exit 1
fi

for i in $(seq $num_img)
do
	j=$(( i + 1 ))
	# don't forget that bash arrays start at 0
	[[ $j -eq $num_img ]] && break
	img1=${images[$i]}
	img2=${images[$j]}
	
	namebase_img1="$(basename $img1)"
	namebase_img2="$(basename $img2)"

	img1cyan=${outdir}/${namebase_img1}_cyan.jpg
	img2magenta=${outdir}/${namebase_img2}_magenta.jpg

	number_img1=$(cut -d"_" -f1 <<< $namebase_img1)
	number_img2=$(cut -d"_" -f1 <<< $namebase_img2)

	overlay_path=${outdir}/${number_img1}-${number_img2}.jpg

	# for each pair, convert first to cyan LUT an second to magenta LUT
	convert $img1 cyanCLUT.png -clut $img1cyan || { echo "can't create $img1cyan";  exit 1; }
	convert $img2 magentaCLUT.png -clut $img2magenta || exit 1

	# overlay them
	convert $img1cyan $img2magenta -compose blend -define compose:args=50,50 -composite $overlay_path

	# remove cyan and magenta
	rm "$img1cyan"
	rm "$img2magenta"
done 
