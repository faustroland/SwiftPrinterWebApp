#!/bin/bash
#set -x
COLORS=120
IMAGE="image.png"

if [ ! -z "$1" ]; then
    IMAGE=$1
fi
if [ ! -z "$2" ]; then
    COLORS=$2
fi

# Check if the file is an image
MIME_TYPE=$(file --mime-type -b "$IMAGE")
if [[ $MIME_TYPE != image/* ]]; then
    echo "Error: $IMAGE is not an image file."
    exit 1
fi

# Extract file extension
EXT="${IMAGE##*.}"

# Convert to PNG if the file is not already a PNG
if [ "$EXT" != "png" ]; then
    echo "Converting $IMAGE to PNG format"
    CONVERTED_IMAGE="${IMAGE%.*}.png"
    convert "$IMAGE" "$CONVERTED_IMAGE"
    IMAGE="$CONVERTED_IMAGE"
fi

echo "Reducing $IMAGE to $COLORS colors"
pngquant $COLORS $IMAGE --quality 0-100 --verbose -f -s 1 -o ${IMAGE%.*}"_reduced.png"
python3 palette.py ${IMAGE%.*}"_reduced.png"
#python3 vertical.py_old ${IMAGE%.*}"_reduced.png" 32 10
python3 vertical6_web.py ${IMAGE%.*}"_reduced.png" 35 10 40 212
FILE_FILE=$(echo $IMAGE | sed "s/.*\///g")
FILE_PATH=$(echo $IMAGE | sed "s/$FILE_FILE//")
echo $FILE_FILE
echo $FILE_PATH

echo /usr/bin/zip -j -r /home/pyweb/web/downloads/$FILE_FILE".zip" $FILE_PATH"image_data.txt" $FILE_PATH"image_hex.txt" ${IMAGE%.*}"_reduced.png"
/usr/bin/zip -j -r /home/pyweb/web/downloads/$FILE_FILE".zip" $FILE_PATH"image_data.txt" $FILE_PATH"image_hex.txt" ${IMAGE%.*}"_reduced.png"
#rm $FILE_PATH/*png $FILE_PATH"image_data.txt" $FILE_PATH"image_hex.txt"

