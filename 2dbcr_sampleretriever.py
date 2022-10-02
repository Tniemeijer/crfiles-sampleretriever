"""
Combining code reader files, asking for the path to the samplesheet
searching the combined codereader data for the positions of the samples
creating a .csv with these source and target positions.

script should also check for double files

Author: Tim Niemeijer
"""

import os
import csv
import datetime
import PySimpleGUI as sg

#FILES = '/Users/timniemeijer/Downloads/code_reader_files'
#EXPORTFILES = '/Users/timniemeijer/Downloads'

def create_output_name():
    """Uses the datetime module to generate a name for the outputfile
    in the following format: pickfile_YYYYmmddHHMMSS"""
    output_name = datetime.datetime.now()
    output_name = 'TubePickfile_'+ output_name.strftime("%Y%m%d%H%M%S")+ '.csv'
    return output_name

def check_duplicate_tube_entries(tubeslist):
    tubesset = set(tubeslist)
    if len(tubeslist) != len(tubesset):
        print(tubesset)
        print(tubeslist)
        return True
    else:
        return False

def make_list_crfiles(outputlist,filespath):
    """returns source list with position, tubeID, plate barcode"""

    os.chdir(filespath)
    for file in os.listdir('./'):
        with open(file = file, mode ='r',errors = 'ignore') as crfile:
            crfile.readline()
            for crline in crfile:
                crline = crline.strip('\n')
                crline = crline.split(',')
                if len(crline[1]) > 0:
                    outputlist.append(crline[0:3])
    tubeslist = [crline[1] for crline in outputlist]
    if check_duplicate_tube_entries(tubeslist):
        print('FOUT: Er zijn duplicaten gevonden!')
        exit()
    else:
        return outputlist

def make_output_pick_list(combined_cr_list,outputlist, samplesheet):
    """check input list against source list
    input list should consist of position, tubeID
    output is sourceplate, sourceplate position, targetplate position"""

    with open(samplesheet,'r') as sample_list:
        header = ['tube','sourceplate','sourceplate position',
                        'target position']
        outputlist.append(header)
        for line in sample_list:
            found = False
            line = line.strip('\n')
            line = line.split(';')
            tube = line[1]
            targetpos = line[0]
            for crline in combined_cr_list:
                crtube = crline[1]
                crpos = crline[0]
                crbarcode = crline[2]
                if crtube == tube:
                    outputlist.append([tube, crbarcode, crpos, targetpos])
                    found = True
            if found:
                pass
            else:
                outputlist.append([tube, '-', '-', targetpos])
    
    return outputlist

def csv_sample_list_export(pick_list,exportdir):
    """Changes directory to exportfiles dir, creates .csv from the picklist"""
    os.chdir(exportdir)
    with open(create_output_name(), 'w') as wrfile:
        writer = csv.writer(wrfile)
        data = pick_list
        for line in data:
            writer.writerow(line)



    
layout = [
    [sg.Text("Input samplesheet:       "),sg.Input(key="-SAMPLESIN-"),
    sg.FileBrowse(file_types=(("CSV files","*.csv*"),))],
    
    [sg.Text("Export picklist to folder:"),sg.Input(key="-EXPORT-"),
    sg.FolderBrowse()],

    [sg.Text("BCR files folder:           "),sg.Input(key="-BCRFILES-"),
    sg.FolderBrowse()],

    [sg.Text("""Click 'Run' to run this program :""",size=(120, 1))],
    [sg.Button('Run')],
]

window = sg.Window("TubeFindr - v1.0.0",layout)

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == 'Run':
        combined_code_reader_list = []
        output_pick_list = []
        make_list_crfiles(combined_code_reader_list,values["-BCRFILES-"])
        make_output_pick_list(combined_code_reader_list,output_pick_list,
                              values["-SAMPLESIN-"])
        csv_sample_list_export(output_pick_list,values["-EXPORT-"])
        sg.popup_no_titlebar("Done! :)")

window.close()