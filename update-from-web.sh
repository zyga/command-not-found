#!/bin/sh

cd UnifiedDataExtractor
wget http://people.ubuntu.com/~mvo/command-not-found/scan.data-latest 
cp scan.data scan.data-old
mv scan.data-latest scan.data
./diff-scan-data scan.data-old scan.data|less
