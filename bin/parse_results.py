#!/usr/bin/python

import sys
import getopt
import os
import fnmatch
import glob
import xmltodict as xtd
import copy



# Console Line Argument Index
OUTPUT_INDEX = 1
FLOWPARAMS_INDEX = 2
RESULT_INDEX = 3

# Regex Dictionary
csv_round_headers = {"m/z":[4], "row retention time":[2], "Peak area":[0], "Peak RT":[2]} # {'header':[decimal,index]}
mgf_round_headers = {"RTINSECONDS=":2, "PEPMASS=":4}
char_dict = {',':'\t'}
filenames_dict = {}
regexes = [csv_round_headers, mgf_round_headers]


def get_filenames_dict(flowparams):
	print "\n---Parsing WorkflowParameters for Upload File Names---"

	with open(flowparams, 'r') as fp:
		params = xtd.parse(fp.read())
    
	files = {}

	whitelisted_file_prefixes = ["inputParams", "spec"]

	for param in params['parameters']['parameter']:
		if param['@name'] == "upload_file_mapping":
			entry = param['#text'].split('|')
			if any(substring in entry[0] for substring in whitelisted_file_prefixes):
				files[entry[0]] = entry[1]

	print "files list: ", files
	print "---Finished Parsing Workflow Parameters---"
    
	return files


def copy_output(src, dest):
	print "\n---Copying Output Files to Result Port---"
	print "src path: ", src
	print "dest path: ", dest
    
	# Copy file to destination with new name
	i = open(os.path.abspath(src), 'r')
	o = open(os.path.abspath(dest), 'w')
	
	regex_copy = copy.deepcopy(regexes)
	for line in i:
		final_line = ""
		# Parse line
		for regex_dict in regex_copy:
			# Clean line
			line = parse_line(line, char_dict, None)
			
			# Parse for replaceable regexes
			line = parse_line(line, regex_dict, dest[dest.index('.'):])

			final_line = line
			
		o.write(final_line)

	print "---Finished Copying File to Result Port---"



def parse_line(line, replace_dict, ext):
	for key in replace_dict.keys():
		if replace_dict.keys() == csv_round_headers.keys():
			if ext == ".csv":
				line_arr = line.split('\t')
				if len(replace_dict[key]) < 2 and key in line:
					print len(line_arr), ' line_arr: ', line_arr
					for i in range(len(line_arr)):
						if key in line_arr[i]:
							print 'key: ', key
							print 'text: ', line_arr[i]
							print 'index: ', i
							replace_dict[key].append(i)
				else:
					for i in range(1, len(replace_dict[key])):
						#print 'line arr: ', line_arr
						#print '\tindex: ', replace_dict[key][i]
						val = float(line_arr[replace_dict[key][i]])
						pow = 10.**replace_dict[key][0]
						val = round(val*pow)/pow
						line_arr[replace_dict[key][i]] = str(val)
				line = '\t'.join(line_arr)
		elif replace_dict.keys() == mgf_round_headers.keys():
			if ext == ".mgf":
				if key in line:
					val = float(line[line.index('=')+1:])
					pow  = 10.**replace_dict[key]
					val = round(val*pow)/pow
					line = key + str(val) + '\n'
		else:
			while key in line:
				#print 'key: ', key
				#print 'replace_dict: ', replace_dict
				#print 'replace_dict[key]: ', replace_dict[key]
				line = line.replace(key, replace_dict[key])
			#print "text"
		
	return line



def usage():
	print "./parse_results.py <output port> <workflowParameters.xml> <result port>"



def main():
	print "\n===Running Parse Results==="

	if len(sys.argv) < 3:
		usage()
		exit(1)
    
	# Collect arguments
	input = sys.argv[OUTPUT_INDEX] + '/'
	flowparams = sys.argv[FLOWPARAMS_INDEX]
	output = sys.argv[RESULT_INDEX] + '/'

	# Print console arguments
	print "\n---Console Line Arguments---"
	print "input port: ", input
	print "flowparams path: ", flowparams
	print "output port: ", output
	print "---Finished Console Arguments---"

	filenames_dict = get_filenames_dict(flowparams)
	regexes.append(filenames_dict)
	for file in os.listdir(input):
		print "regexes: ", regexes
		copy_output(input+file, output+file)

	print "\n===Finished Running Parse Results==="



if __name__ == '__main__':
	main()
