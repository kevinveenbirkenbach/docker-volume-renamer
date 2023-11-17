#!/bin/bash

# Check if two arguments were passed
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 OLD_VOLUME_NAME NEW_VOLUME_NAME"
    exit 1
fi

# Assign the passed arguments to variables
old_volume_name="$1"
new_volume_name="$2"

# Create a new volume
docker volume create "$new_volume_name"

# Start a temporary container and copy data from the old volume to the new volume
docker run --rm \
    -v "$old_volume_name":/from \
    -v "$new_volume_name":/to \
    alpine ash -c "cd /from && cp -av . /to"

# Check if the data was copied successfully
if [ $? -eq 0 ]; then
    echo "Data copied successfully. The old volume can be removed."
    # Remove the old volume
    docker volume rm "$old_volume_name"
else
    echo "Error copying data. Check container logs for details."
    exit 1
fi

# Note: Manually update your containers to use the new volume.
