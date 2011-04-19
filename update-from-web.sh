#!/bin/sh


cd UnifiedDataExtractor

# backup copy 
cp scan.data scan.data-old

# rookery has the normal archive
wget -O scan.1 http://rookery.ubuntu.com/~mvo/command-not-found/scan.data-latest 
# frei has ports.ubuntu.com
wget -O scan.2 http://rookery.ubuntu.com/~mvo/command-not-found-ports/scan.data-latest 
# concat
cat scan.1 scan.2 > scan.data
./diff-scan-data scan.data-old scan.data|less
