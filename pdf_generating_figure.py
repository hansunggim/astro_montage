import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as FigureCanvasPdf
from matplotlib.figure import Figure
from matplotlib import gridspec
from pdf2image import convert_from_path
import numpy as np
import pandas as pd
import yaml

# Loading the input parameters and files from main_config.yaml
def load_config(file_path='main_config.yaml'):
	with open(file_path, 'r') as file:
		config = yaml.safe_load(file)

	return config


# Generating the combined figures in PDF
def generate_figure(pdf_files, output_file):
	rows = len(pdf_files)
	cols = 1
	total_files = len(pdf_files)

	fig = plt.figure(figsize=(8.0, 10))  # paper size is 8x10 inches to consider the letter size of 8.5x11.0 inches

	gs = gridspec.GridSpec(rows,cols, width_ratios=[1]*cols, height_ratios = [1]*rows)

	for j in range(rows) :
		
		pdf_file = pdf_files[j]
		images = convert_from_path(pdf_file)
		img = images[0]
		ax = fig.add_subplot(gs[j,0])
		ax.imshow(img)
		ax.axis('off')


	plt.tight_layout()
	plt.savefig(output_file)
	plt.close()


def main():
	config = load_config()
	
	global_parameters = config["global_parameters"]
	global_files = config["global_files"]

	cat_file = global_files['cat_file']
	cat = pd.read_csv(cat_file)

	number_figures = float(global_parameters['number_figures_per_page'])

	pdf_files=[]
	i = 0
	for index, row in cat.iterrows():
		idx = int((index+1)/number_figures)
		rdx = (index+1) % number_figures 

		if rdx == 0:   # if the row number is multiplied by {number_figures}, the appended figures are combined in the same page
			i += 1
			output_file=f"montage_{i}.pdf"
			pdf_files.append(f"montage_{row['ID']}_combination.pdf")

			generate_figure(pdf_files, output_file)
			pdf_files = []

		if rdx != 0:   # if the row number is not multiplied by {number_figures}, the figures are appended to reach the number multiplied by {number_figures}
			pdf_files.append(f"montage_{row['ID']}_combination.pdf")

		if index == (len(cat)-1):	# if it reaches the end of row, the appended figures are combined in the same page even though it is not multiplied by {number_figures} 
			i += 1
			output_file=f"montage_{i}.pdf"
	
			generate_figure(pdf_files, output_file)



if __name__ == "__main__":
	main()

