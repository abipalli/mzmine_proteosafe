#!/usr/bin/python

import sys
import getopt
import os
import fnmatch
import glob
import xmltodict as xtd



def change_file_paths(file, params, output):
    print("\n---Updating Batch File Paths---")
    print("File: " + file)
    print("Current Working Directory: " + os.getcwd())
    print("Subdirectories in Working Directory: " + str(os.listdir(os.getcwd())))
    print("Params: " + os.path.abspath(params))

    # Convert .xml file to dictionary
    with open(file, "r") as f:
        #xml = xtd.parse(f.read(), dict_constructor=lambda *args, **kwargs: defaultdict(list, *args, **kwargs))
        xml = xtd.parse(f.read())

    # Parse xml dict
    files_list = xml['batch']['batchstep'][0]['parameter']['file']
    if type(files_list) == unicode:
        files_list = [files_list]
    print("HERE", files_list, type(files_list))

    # Parse params dir
    params_dir = params
    params_list = sorted(os.listdir(params_dir))
    for i in range(len(params_list)):
        #print("MING", params_dir, os.path.abspath(params_dir), os.path.basename(params_list[i]))
        #print(os.path.join(os.path.abspath(params_dir), os.path.basename(params_list[i])))
        params_list[i] = os.path.join(os.path.abspath(params_dir), os.path.basename(params_list[i]))

    # Replace Raw Data Files with Local Filepath
    xml['batch']['batchstep'][0]['parameter']['file'] = params_list

    # Replace Export File Names
    for step in xml['batch']['batchstep']:
        if step['@method'].find(".io.") > -1:
            old_filename = step['parameter'][1]['#text']
            step['parameter'][1]['#text'] = os.path.abspath(output+old_filename)
            print step['parameter'][1]['#text']

    print("---Finished Updating File Paths---")

    # Return new xml
    return xml



def copy_dict_to_file(dict, dest):
    print("\n---Writing XML to File---")
    print("Saving to file: "+dest)

    parsed = xtd.unparse(dict, pretty=True)
    with open(dest, "w") as o:
        o.write(parsed)

    print("---Writing to File Successful---")



def run_mzmine(batch, path_to_mzmine):
    print("\n---Running MZmine---")
    print("-  Printing XML File  -")
    batch = os.path.abspath(batch)

    # Open parsed batch file and run mzmine
    with open(batch, "r") as b:
        print("X", path_to_mzmine)
        print(b)
        mzmine_shpath = path_to_mzmine
        exec_cmd = "sh "+ mzmine_shpath + " " + batch
        print("Command: " + exec_cmd)
        os.system(exec_cmd)

    print("---Finished Running MZmine---")



def main():
    if len(sys.argv) < 3:
        exit()

    params = sys.argv[1] + "/"
    input = sys.argv[2]
    output = sys.argv[3] + "/"
    path_to_mzmine = sys.argv[4]

    print("params: " + params)
    print("input: " + input)
    print("ouput: " + output)
    print(os.getcwd())

    parsed_batch = os.getcwd()+"/batch/parsedBatch.xml"
    print(parsed_batch)

    my_dict = change_file_paths(input, params, output)
    copy_dict_to_file(my_dict, parsed_batch)

    run_mzmine(parsed_batch,path_to_mzmine)



if __name__ == "__main__":
    main()
