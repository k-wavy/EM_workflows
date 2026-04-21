#!/bin/env bash

# sort raw EM scans into folders for feabas or other

# by Sanja Jasek

# assumes that folders are in order, e.g. cs8_bla/r1 comes before cs8_bla/r2
# and cs9/r1 comes before cs10/r1
# assumes file names in format "Tile_r<row>-c<column>_S_<layer_in_session>_<random_number_from_microscope>.tif, like Tile_r1-c1_S_002_1614627106.tif

# sort this way: <layer_number>/<layer_number>_r<row_number>-c<column_number>_<random_number_from_microscope>.tif

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 0
fi


indir="$1"
outdir="$2"


# use find instead of ls, because I don't know how many levels of folders there is - 1 or 2 levels are common
readarray -t images  < <(find "$indir" -iname "*.tif" | sort -V)

# check if paths have spaces or funny stuff, and exit if yes
weird_char=$(printf '%s\n' "$outdir" "${images[@]}" | grep -n '[^A-Za-z0-9._/:,-\\]' | wc -l)
if [[ $weird_char -gt 0 ]]
then
    echo "Funny characters in path. Please remove them."
    exit 1
fi

# I can't just assume all layers are consecutive, because there are sometimes missing sections (set aside for immunolabelling or lost)
# The gaps should be accounted for in case we need to put the stained sections back in, or to keep distances correct for length and
# volume calculations.
# Therefore, missing sections should be accounted for in file names
# so I can't just sort the full path and then sort according to that,
# I have to find the first subfolder, and probably keep the numbering from there, it should be correct for the first one,
# then find the second folder, and give sections layer number that is 1 +  number of layers in first folder, etc


info_file="${outdir}/renaming_map.tsv"

# get number of layers, so it's easier to keep track

num_layers=$(printf "%s\n" "${images[@]}" | grep -oE '.*/Tile_r' | sort -u | wc -l)


for image in ${images[@]}
do
    #  start numbering from number in first layer available
    # for each consecutive layer, check the difference original name of previous layer
    # and the current layer, then add that to the number of renamed layer
    img_name="$(basename $image)"
    read coord layer_filename id_num < <(basename "${img_name}" | sed -E 's/Tile_(r[0-9]+-c[0-9]+)_S_([0-9]+)_([0-9]+).tif/\1 \2 \3/g')
    
    # check if defining variables failed, if the filename doesn't follow the pattern
    if [[ -z $coord || -z $layer_filename || -z $id_num ]]
    then
        echo "$img_name doesn't follow naming convention. Rename failed."
        exit 1
    fi

    # padding numbers is often needed, but also need unpadded version because bash arithmetic and printf have problems
    padding=${#num_layers}
    layer_filename_num=$((10#$layer_filename))
    layer_filename=$(printf "%0${padding}d" $layer_filename_num)
    # prev layer placeholder is to make the first iteration work
    previous_layer_placeholder_num=$(( $layer_filename_num - 1 ))
    previous_layer_placeholder=$(printf "%0${padding}d" $previous_layer_placeholder_num)
    # I need the filename of the previous file to check if there are missing layers
    # but the difference method only works within a folder  
    folder="${image%/*}"
    previous_folder="${previous_folder:-$folder}"

    previous_layer_filename=${previous_layer_filename:-$previous_layer_placeholder}
    previous_layer_filename_num=$((10#$previous_layer_filename))
    if [[ $folder == $previous_folder ]]
    then
        # count up with difference
        difference=$(( $layer_filename_num - $previous_layer_filename_num ))
        # now add the difference to the actual layer number
    else
        # count up by 1
        difference=1

    fi
    previous_layer_actual=${previous_layer_actual:-$previous_layer_filename}
    previous_layer_actual_num=$((10#$previous_layer_actual))
    new_layer_num=$(( $previous_layer_actual_num + $difference ))
    new_layer=$(printf "%0${padding}d" $new_layer_num)
    
    if [[ ! -d ${outdir}/$new_layer ]]
    then
        mkdir ${outdir}/$new_layer || { echo "mkdir ${outdir}/$new_layer failed" ; exit 1 ; }
    fi

    new_img_name=${new_layer}_${coord}_${id_num}.tif
    
    # check if it was already renamed or moved
    if [[ ! -f ${outdir}/${new_layer}/${new_img_name} ]]
    then
        cp $image ${outdir}/${new_layer}/${new_img_name} || { echo "copy $image failed" ; exit 1 ; }
	echo -e "$image\t${outdir}/${new_layer}/${new_img_name}" >> "$info_file"
    fi

    previous_layer_filename=$layer_filename
    previous_layer_actual=$new_layer
    previous_folder="$folder"
done
