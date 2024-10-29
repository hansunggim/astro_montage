import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
import io
import yaml

# Loading the input parameters and files from main_config.yaml
def load_config(file_path='main_config.yaml'):
	with open(file_path, 'r') as file:
		config = yaml.safe_load(file)

	return config


# Cropping the image with the defined positions
# crop_box[0,1,2,3] = [left, bottom, right, top]
def crop_pdf(input_pdf, output_pdf, crop_box):
	reader = PdfReader(input_pdf)
	writer = PdfWriter()

	page = reader.pages[0]
	page.mediabox.lower_left = (crop_box[0], crop_box[1])
	page.mediabox.upper_right = (crop_box[2], crop_box[3])
	writer.add_page(page)

	cropped_pdf = "cropped_temp.pdf"
	with open(cropped_pdf, "wb") as output_pdf:
		writer.write(output_pdf)

	return cropped_pdf


# Resizing the image to have the designated size and putting the label on the image
def resize_pdf_label(input_pdf, output_pdf, target_size, label):
	images = convert_from_path(input_pdf)
	image = images[0]

	resized_image = image.resize(target_size, Image.Resampling.LANCZOS)

	draw = ImageDraw.Draw(resized_image)
	font_size = 20
	font = ImageFont.truetype("Helvetica.ttc", font_size)
	text_position = (10,10)
	draw.text(text_position, label, font=font, fill="white")

	img_byte_arr = io.BytesIO()
	resized_image.save(img_byte_arr, format='PNG')
	img_byte_arr.seek(0)

	packet = io.BytesIO()
	can = canvas.Canvas(packet, pagesize=target_size)
	can.drawImage(ImageReader(img_byte_arr), 0, 0, width=target_size[0], height=target_size[1])
	can.save()

	packet.seek(0)
	new_pdf = PdfReader(packet)
	writer = PdfWriter()
	writer.add_page(new_pdf.pages[0])

	with open(output_pdf, "wb") as f:
		writer.write(f)


# Resizing the image to have the designated size
def resize_pdf(input_pdf, output_pdf, target_size):
	images = convert_from_path(input_pdf)
	image = images[0]

	resized_image = image.resize(target_size, Image.Resampling.LANCZOS)

	img_byte_arr = io.BytesIO()
	resized_image.save(img_byte_arr, format='PNG')
	img_byte_arr.seek(0)

	packet = io.BytesIO()
	can = canvas.Canvas(packet, pagesize=target_size)
	can.drawImage(ImageReader(img_byte_arr), 0, 0, width=target_size[0], height=target_size[1])
	can.save()

	packet.seek(0)
	new_pdf = PdfReader(packet)
	writer = PdfWriter()
	writer.add_page(new_pdf.pages[0])

	with open(output_pdf, "wb") as f:
		writer.write(f)


### MAIN ###

def main():

	config = load_config()      # Reading the input parameters and files
	
	global_parameters = config["global_parameters"]
	global_files = config["global_files"]

	crop_box_str = global_parameters['crop_box']
	target_size_str = global_parameters['target_size']

	crop_box1 = crop_box_str.strip("()").split(",")
	crop_box = tuple(int(num) for num in crop_box1)

	target_size1 = target_size_str.strip("()").split(",")
	target_size = tuple(int(num) for num in target_size1)

	cat_file = global_files['cat_file']
	cat = pd.read_csv(cat_file)      # Reading the catalog file formatted in csv

	radio_file = global_files['radio_file']
	hst_files = global_files['hst_files']
	jwst_files = global_files['jwst_files']

	fits_files = [radio_file, *hst_files, *jwst_files]
	num_files = len(fits_files)

	for index, row in cat.iterrows():
		for ii in range(0, num_files):
			input_pdf = f"montage_{row['ID']}_{ii}.pdf"
			output_pdf = f"montage_{row['ID']}_{ii}_cropped.pdf"
			label = str(row['ID'])

			if os.path.exists(input_pdf):
				try:
					cropped_pdf = crop_pdf(input_pdf, output_pdf, crop_box)

					if ii==0:
						resize_pdf_label(cropped_pdf, output_pdf, target_size, label)
					else:
						resize_pdf(cropped_pdf, output_pdf, target_size)

					os.remove(cropped_pdf)

				except Exception as e:
					print(f"Error processing {input_pdf}: {e}")

			else:
				print(f"File {input_pdf} does not exist")



if __name__ == "__main__":
	main()

