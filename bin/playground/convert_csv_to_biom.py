#!/usr/bin/python


import os
import sys



def format_input_file(input_file):
	with open(input_file, 'r') as i:
		counter = 0
		for line in i.read():
			line_arr = line.split('\t')
			out = line_arr[0] + ' ' + line_arr[1] 
			for i in range(len(line_arr) - 2):
					out = line_arr + '\t' + line_arr[2+i]
			out_content = out_content + out + '\n'
			counter = counter + 1

	# Overwrite generated output into input file
	with open(input_file, 'w') as o:
		o.write(out_content)

	#DEBUG
	print "new file output:\n", out_content



def get_file_contents(src):
	i = open(src, 'r')
	with open(src, 'r') as i:
		return i.read()
	return -1;



def print_biom_file(command, output_file):
	with open(output_file, 'w') as o:
		o.write("# Constructed from biom file")
	os.system(command)	



def main():
	csv = sys.argv[1]
	biom_output = sys.argv[2] if sys.argv[2] != "" else "biom_output.biom"

	print "current working directory: ", os.getcwd()
	curr_dir = sorted(os.listdir(os.getcwd()))
	print "directory contents: ", curr_dir
	input = curr_dir[1]
	print "input file: ", input
	input_content = get_file_contents(input)
	output = "biom_table.biom"
	command = "biom convert -i " + input + " -o " + output + " --to-hdf5 --table-type=\"OTU table\" --process-obs-metadata taxonomy" 
	print_biom_file(command, output)
	


if __name__ == '__main__':
	main()
