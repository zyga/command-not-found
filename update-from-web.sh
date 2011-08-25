#!/bin/sh

set -e

cd UnifiedDataExtractor

# backup copy 
if [ -e scan.data ]; then
    cp scan.data scan.data-old
fi

# rookery has the normal archive
wget -O scan.1 http://rookery.ubuntu.com/~mvo/command-not-found/scan.data-latest 
# ports.ubuntu.com
wget -O scan.2 http://ports.ubuntu.com/~mvo/command-not-found/scan.data-latest 

# concat
cat scan.1 scan.2 > scan.data

if [ -e scan.data-old ]; then
    ./diff-scan-data scan.data-old scan.data|less
fi
