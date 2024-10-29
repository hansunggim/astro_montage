#!/bin/bash

echo "Generating cutouts of sources from the radio image"
python3 montage_radio.py

echo "Generating cutouts of sources from the optical images"
python3 montage_optical.py

echo "Cropping and resizing the cutouts"
python3 pdf_crop_resize.py

echo "Combining the radio and optical cutouts"
python3 pdf_combine.py

echo "Combining the PDF files to produce the multi-page PDF"
python3 pdf_generating_figure.py

echo "Clearing all the byproducts"
python3 clear_files.py
