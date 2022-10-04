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
        sg.popup_error('FOUT: Er zijn duplicaten gevonden!',title="Error")
        
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

data = []
heading = ['tube','sourceplate','sourceplate position',
                        'target position']

    
layout = [
    [sg.Text("Input samplesheet:       "),sg.Input(key="-SAMPLESIN-"),
    sg.FileBrowse(file_types=(("CSV files","*.csv*"),))],
    
    [sg.Text("BCR files folder:           "),sg.Input(key="-BCRFILES-"),
    sg.FolderBrowse()],

    [sg.Text(
        """Click 'Run' to run this program:""",
        size=(80, 1))],
    [sg.Button('Run')],
    [sg.Text("Export picklist to folder:"),sg.Input(key="-EXPORT-"),
    sg.FolderBrowse()],
    [sg.Text(
        """Click 'Export' to export to .csv:""",
        size=(80, 1))],
    [sg.Button('Export')],

    [sg.Table(values= data, headings= heading,
     key = '-TABLE-',
      auto_size_columns= False, def_col_width= 20,  expand_y= True, num_rows= 24, size= (450,60))],

]

window = sg.Window("TubeFindr - v1.0.1",layout)

while True:
    event, values = window.read()
    window.move_to_center()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    combined_code_reader_list = []
    output_pick_list = []
    if event == 'Run':
        while True:
            try:
                make_list_crfiles(combined_code_reader_list,values["-BCRFILES-"])
            except IndexError:
                sg.popup_error("Selected directory is not compatible",
                title="Error")
                break
            except FileNotFoundError:
                sg.popup_error("Files not found, please select a folder",
                title="Error")
                break
            try:
                make_output_pick_list(combined_code_reader_list,output_pick_list,
                                values["-SAMPLESIN-"])
            except IndexError:
                sg.popup_error("Inserted file not compatible",title="Error")
                break
            except FileNotFoundError:
                sg.popup_error("File not found, please select a file",
                title="Error")
                break
            data =[i for i in output_pick_list[1:]]
            window['-TABLE-'].update(values = data)
            break
    if event == 'Export':
        try:
            csv_sample_list_export(output_pick_list,values["-EXPORT-"])
        except FileNotFoundError:
            sg.popup_error("Output folder not found, please select a folder",
            title="Error")
window.close()

