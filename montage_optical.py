#####################################################################
###
### montage_optical.py
###
### This python script extracts the image from the FITS files of HST+JWST images using the astrocut, 
### add the ellipses of the radio source size on the optical images, 
### and save them to the pdf files. 
###
#####################################################################


import astrocut 
from astropy.io import fits
from astropy.coordinates import SkyCoord
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches
import sys
import yaml

# Loading the input parameters and files from main_config.yaml
def load_config(file_path='main_config.yaml'):
	with open(file_path, 'r') as file:
		config = yaml.safe_load(file)

	return config


# Reading Header from FITS image file
def fits_header(filename):
	with fits.open(filename) as hdul:
		header = hdul[0].header

	return header


# Determining the lower and upper values for the image contrast (in case of HST and JWST images, it sets to 3)
def calculate_stats(data, num_std=3):
	mean = np.mean(data)
	std = np.std(data)
	lower_value = 0.05*(mean - 1.0 * std)
	upper_value = mean + num_std * std

	return lower_value, upper_value


# Normalize the image with the lower and upper pixel values 
def normalize_image(image):

	lower_bound, upper_bound = calculate_stats(image)
	normalized_image = np.where(image > upper_bound, upper_bound, image)
	normalized_image = np.where(normalized_image < lower_bound, lower_bound, normalized_image)
	normalized_image = (normalized_image - lower_bound) / (upper_bound - lower_bound)

	return normalized_image


# Convert the arcsec to pixel scale in x-axis
def arcsec_to_pixel_x(arcsec, header):
	if ('CDELT1' in header) :
		pixel_scale_x = 3600.0*abs(header['CDELT1'])
	elif ('D001SCAL' in header) :
		pixel_scale_x = abs(header['D001SCAL'])

	return arcsec / pixel_scale_x


# Convert the arcsec to pixel scale in y-axis
def arcsec_to_pixel_y(arcsec, header):
	if ('CDELT2' in header) :
		pixel_scale_y = 3600.0*abs(header['CDELT2'])
	elif ('D001SCAL' in header) :
		pixel_scale_y = abs(header['D001SCAL'])

	return arcsec / pixel_scale_y


# Converting the ellipse in arcsec to that in pixels and drawing the ellipse with red color
# Change the color and linewidth of the ellipse
def draw_ellipse(major, minor, pa, header, cutout_size):

	if major < 1.0:
		major_arcsec = 1.0 
	else:
		major_arcsec = major

	major_axis = arcsec_to_pixel_x(major_arcsec, header)

	if minor < 1.0:
		minor_arcsec = 1.0
	else:
		minor_arcsec = minor

	minor_axis = arcsec_to_pixel_x(minor_arcsec, header)

	e = matplotlib.patches.Ellipse(xy=(cutout_size[0] / 2, cutout_size[1] / 2), width=major_axis, height=minor_axis, angle=pa, color='red', fill=False, linewidth=2.0)

	return e	



### MAIN ###
def main():

	config = load_config()    # Reading the input parameters and files

	global_parameters = config["global_parameters"]
	global_files = config["global_files"]

	size_arcsec = float(global_parameters['size_arcsec'])
	cat_file = global_files['cat_file']

	hst_files = global_files['hst_files']
	jwst_files = global_files['jwst_files']

	fits_files = [*hst_files, *jwst_files]
	num_files = len(fits_files)

	cat = pd.read_csv(cat_file)    # Reading the catalog file formatted in csv

	header = []
	for ii in range(0, num_files) :
		header.append(fits_header(fits_files[ii]))

	cutout_optical_size = round(arcsec_to_pixel_x(size_arcsec, header[0]))   # Converting the cutout size in arcsec to in pixel and setting the cutout size in two dimensions.
	cutout_size = [cutout_optical_size, cutout_optical_size]

	for index, row in cat.iterrows():
		ra = row['RA']
		dec = row['DEC']
		coord_string = f"{ra} {dec}"
		center_coord = SkyCoord(coord_string, unit='deg')


		for i in range(0,num_files):
			fig, ax = plt.subplots(figsize=(5,5))

			cutout = astrocut.fits_cut(fits_files[i], center_coord, cutout_size, extension='all',cutout_prefix='coord1',single_outfile=True,memory_only=True)[0]   # Creating the cutout using astrocut
			normalized_image = normalize_image(cutout[1].data)

			major = 3600.0*float(cat.loc[index, 'Major']) 
			minor = 3600.0*float(cat.loc[index, 'Minor']) 
			pa = float(cat.loc[index,'PA'])+90.0

			e = draw_ellipse(major, minor, pa, header[i], cutout_size)    # Adding the ellipse of radio source to the images
			ax.add_patch(e)

			img = ax.imshow(normalized_image, cmap='gray')
			ax.axis('off')

# Flipping the image upside-down because the y-axis of images is reversed
# The y-axis is flipped during iteration, so the axis is set manually 
			ax.set_ylim(img.get_extent()[3], img.get_extent()[2])

			outfile = f"montage_{row['ID']}_{i+1}.pdf"
			plt.savefig(outfile)

			plt.close()


if __name__ == "__main__":
	main()

