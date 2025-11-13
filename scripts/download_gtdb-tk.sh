#!/bin/bash

echo "Creating the database.."
DOWNLOAD_DIR="/home/inf-21-2024/nbis/gtdb-tk"
mkdir -p "${DOWNLOAD_DIR}"
cd "$DOWNLOAD_DIR"

BASE_URL="https://data.gtdb.ecogenomic.org/releases/release220/220.0/auxillary_files/gtdbtk_package/split_package/gtdbtk_r220_data.tar.gz.part_"
PARTS=("aa" "ab" "ac" "ad" "ae" "af" "ag" "ah" "ai" "aj" "ak")

for suffix in "${PARTS[@]}"; do
    filename="gtdbtk_r220_data.tar.gz.part_${suffix}"

    echo "Downloading ${filename} in background..."
    
    wget -c --tries=3 --waitretry=5 --timeout=60 "${BASE_URL}${suffix}" -O "${filename}" &

    # Verify if the download is complete
    if [ $? -ne 0 ]; then
        echo "Failed to download ${filename}.."
        exit 1
    fi


done

wait

echo "All parts downloaded successfully."

# Verify if the file is present
if [ ! -e gtdbtk_r220_data.tar.gz ]; then
    echo "Concatenating the files..."
    cat gtdbtk_r220_data.tar.gz.part_* > gtdbtk_r220_data.tar.gz
else
    echo "File exists!"
fi

echo "Done"