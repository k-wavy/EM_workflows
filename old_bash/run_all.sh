#!/bin/bash

usage="plase give location of feabas"

[[ "$#" -eq 1 ]] || { echo $usage; exit 1 ; }

feabas="$1"

echo "stitch matching" && \
python "$feabas"/scripts/stitch_main.py --mode matching && \
echo "stitch optimizazion" && \
python "$feabas"/scripts/stitch_main.py --mode optimization && \
echo "stitch rendering" && \
python "$feabas"/scripts/stitch_main.py --mode rendering && \
echo "thumbnail downsample" && \
python "$feabas"/scripts/thumbnail_main.py --mode downsample && \
echo "thumbnail match" && \
python "$feabas"/scripts/thumbnail_main.py --mode match && \
echo "thumbnail optimization" && \
python "$feabas"/scripts/thumbnail_main.py --mode optimization && \
echo "thumbnail render" && \
python "$feabas"/scripts/thumbnail_main.py --mode render && \
echo "align meshing" && \
python "$feabas"/scripts/align_main.py --mode meshing && \
echo "align matching" && \
python "$feabas"/scripts/align_main.py --mode matching && \
echo "align optimization" && \
python "$feabas"/scripts/align_main.py --mode optimization && \
echo "align rendering" && \
python "$feabas"/scripts/align_main.py --mode rendering && \
echo "align downsample" && \
python "$feabas"/scripts/align_main.py --mode downsample
