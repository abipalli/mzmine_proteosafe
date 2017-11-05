#!/usr/bin/python

import os
import sys
import xmltodict as xtd
from tempfile import NamedTemporaryFile

def format_input_csv(input_filename, output_filename):
    out_content = "#OTU ID"
    whitelist_headers = ["Peak area"]; whitelist_indeces = []

    # Parse through input file
    with open(input_filename, 'r') as i:
        is_firstline = True
        for line in i:
            line_arr = line.split('\t')
            row_id = line_arr[0] + " " + line_arr[1] + " " + line_arr[2]

            if is_firstline:
                out = ""
            else:
                out = str(row_id)

            # For each tag in the line
            for ind in range(len(line_arr)):
                if is_firstline == 1 and any(substring in line_arr[ind] for substring in whitelist_headers):
                    whitelist_indeces.append(ind)
                    header = str(line_arr[ind])
                    out = out + "\t" + os.path.basename(header).replace(".mzXML", "").replace(".mzML", "")
                    #out = out + '\t' + (header[header.rindex('/')+1:header.index('.mzXML')] if '.' in header else header)
                elif ind in whitelist_indeces:
                    out = out + '\t' + str(line_arr[ind])

            out_content = out_content + out + '\n'

            if is_firstline == 1:
                is_firstline = False

    # Overwrite generated output into input file
    with open(output_filename, 'w') as o:
        o.write(out_content)



def convert_to_biom(input, output, python_runtime, biom_path):
    print("\n---Running Biom Convert Command---")
    command = "%s %s convert -i %s -o %s --to-hdf5 --table-type=\"OTU table\"" % (python_runtime, biom_path, input, output)
    print("running command: ", command)
    #with open(output_file, 'w') as o:
    #	o.write("# Constructed from biom file")
    os.system(command)
    print("---Finished Running Biom Convert Command---")



def main():
    input_csv_filename = sys.argv[1]
    output_biom_filename = sys.argv[2]
    python_runtime = sys.argv[3]
    python_biom_path = sys.argv[4]

    f = NamedTemporaryFile(delete=False)
    f.close()

    format_input_csv(input_csv_filename, f.name)

    #Converting to BioM
    convert_to_biom(f.name, output_biom_filename, python_runtime, python_biom_path)
    os.unlink(f.name)



if __name__ == '__main__':
        main()
