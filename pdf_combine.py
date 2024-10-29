from PIL import Image
from pdf2image import convert_from_path
import pandas as pd
import io
import yaml

# Loading the input parameters and files from main_config.yaml
def load_config(file_path='main_config.yaml'):
	with open(file_path, 'r') as file:
		config = yaml.safe_load(file)

	return config


# Extracting the image from pdf file
def extract_image_from_pdf(pdf_path):
	images = convert_from_path(pdf_path)
	
	return images


# Combining images side by side
def combine_images_side_by_side(images, space):

	widths, heights = zip(*(i.size for i in images))
	
	total_width = sum(widths) + space*(len(images)-1)
	max_height = max(heights)

	new_image = Image.new('RGB', (total_width, max_height), (255,255,255))

	x_offset = 0
	for im in images:
		new_image.paste(im, (x_offset, 0))
		x_offset += im.width + space
	
	return new_image


# Saving the combined image to PDF file
def save_image_as_pdf(image, output_path):
	image.save(output_path, "PDF", resolution=100.0)


def main():
	config = load_config()

	global_parameters = config["global_parameters"]
	global_files = config["global_files"]
	
	radio_file = global_files['radio_file']
	hst_files = global_files['hst_files']
	jwst_files = global_files['jwst_files']

	fits_files = [radio_file, *hst_files, *jwst_files]
	num_files = len(fits_files)

	cat_file = global_files['cat_file']
	cat = pd.read_csv(cat_file)

	for index, row in cat.iterrows():
		image_pdfs=[]
		for i in range(0, num_files):
			pdf_file= f"montage_{row['ID']}_{i}_cropped.pdf"
			image_pdfs.append(extract_image_from_pdf(pdf_file)[0])

		combined_image = combine_images_side_by_side(image_pdfs, 5)   # 5: spacing between images

		output_pdf = f"montage_{row['ID']}_combination.pdf"
		save_image_as_pdf(combined_image, output_pdf)



if __name__ == "__main__":
	main()


