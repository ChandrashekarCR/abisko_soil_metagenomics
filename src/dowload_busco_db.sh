#!/bin/bash

# download_busco_db.sh - Download BUSCO databases for soil metagenomics

BUSCO_DIR="/home/inf-21-2024/nbis/busco_db"
mkdir -p "${BUSCO_DIR}"

echo "Downloading BUSCO prokaryotic lineages..."
echo "Target directory: ${BUSCO_DIR}"
echo ""

mkdir -p "${BUSCO_DIR}/lineages"
cd "${BUSCO_DIR}/lineages"


echo "Downloading bacteria_odb12..."
wget -c https://busco-data.ezlab.org/v5/data/lineages/bacteria_odb12.2025-05-14.tar.gz
tar -xvf bacteria_odb12.2025-05-14.tar.gz
rm -rf bacteria_odb12.2025-05-14.tar.gz

echo "Downloading archaea_odb12..."
wget -c https://busco-data.ezlab.org/v5/data/lineages/archaea_odb12.2025-05-14.tar.gz
tar -xzf archaea_odb12.2025-05-14.tar.gz
rm archaea_odb12.2025-05-14.tar.gz


echo ""
echo "Verifying installation"
if [ -d "${BUSCO_DIR}/lineages/bacteria_odb12" ]; then
    echo "bacteria_odb12 installed"
    ls -lh "${BUSCO_DIR}/lineages/bacteria_odb12/" | head -5
else
    echo "bacteria_odb12 NOT found"
fi

if [ -d "${BUSCO_DIR}/lineages/archaea_odb12" ]; then
    echo "archaea_odb12 installed"
else
    echo "archaea_odb12 NOT found"
fi

echo ""
echo "Disk usage"
du -sh "${BUSCO_DIR}"