import os
import pandas as pd
import yaml

def load_config(file_path='main_config.yaml'):
	with open(file_path, 'r') as file:
		config = yaml.safe_load(file)

	return config

def main():
	config = load_config()
	
	global_parameters = config["global_parameters"]
	global_files = config["global_files"]

	cat_file = global_files['cat_file']
	cat = pd.read_csv(cat_file)

	radio_file = global_files['radio_file']
	hst_files = global_files['hst_files']
	jwst_files = global_files['jwst_files']

	fits_files = [radio_file, *hst_files, *jwst_files]
	num_files = len(fits_files)


	for index, row in cat.iterrows():

		image_pdfs=[]
		for i in range(0, num_files):
			file1= f"montage_{row['ID']}_{i}.pdf"
			file2= f"montage_{row['ID']}_{i}_cropped.pdf"

			os.remove(file1)
			os.remove(file2)

if __name__ == "__main__":
	main()

