"""
Combining code reader files, asking for the path to the samplesheet
searching the combined codereader data for the positions of the samples
creating a .csv with these source and target positions.
script also checks for double barcodes.
Author: Tim Niemeijer 
"""

import os
import csv
import datetime
import PySimpleGUI as sg
import pandas as pd


def create_output_name():
    """
    Uses the datetime module to generate a name for the outputfile
    in the following format: pickfile_YYYYmmddHHMMSS
    """
    output_name = datetime.datetime.now()
    output_name = 'TubePickfile_'+ output_name.strftime("%Y%m%d%H%M%S")+ '.csv'
    return output_name


def make_list_tubeobjects(filespath):
    """returns Tube list with position, tubeID, plate barcode"""
    os.chdir(filespath)
    info_list = pd.DataFrame()
    for file in os.listdir('./'):
        ext_check = file.split('.')
        if ext_check[1] == "csv":
            tubes = pd.read_csv(file,sep=',')
            tubes = tubes.iloc[:,:5]
            tubes = tubes.dropna()
            info_list = pd.concat([info_list,tubes])
    return info_list
# While testing for tube update in multiple files, it is not updated. ??????
# seems to work inside one file.

def make_output_pick_list(tube_list,outputlist, samplesheet):
    """check input list against source list
    input list should consist of position, tubeID
    output is sourceplate, sourceplate position, targetplate position"""

    with open(samplesheet,'r') as sample_list:
        header = ['Tube','Sourceplate','Sourceplate position',
                        'Target position']
        outputlist.append(header)
        for line in sample_list:
            found = False
            line = line.strip('\n')
            line = line.split(';')
            target_tube = int(line[1])
            targetpos = line[0]
            #assuming the target position is in the pick list
            if target_tube in tube_list["Tube ID"].values:
                print("yes")
                tube_target = tube_list[tube_list["Tube ID"]==target_tube]
                tube_rack = tube_target["Rack ID"].values[0]
                tube_pos = tube_target["Tube Position"].values[0]
                outputlist.append([target_tube, tube_rack, tube_pos, targetpos])
                found = True
            if found:
                pass
            else:
                print("No")
                outputlist.append([target_tube, '-', '-', targetpos])
    return outputlist


def csv_sample_list_export(pick_list,exportdir):
    """Changes directory to exportfiles dir, creates .csv from the picklist"""
    os.chdir(exportdir)
    with open(create_output_name(), 'w') as wrfile:
        writer = csv.writer(wrfile)
        data = pick_list
        for line in data:
            writer.writerow(line)


def main():
    """
    Run the code
    """
    sg.theme("Reddit")

    data = []
    heading = ['Tube','Sourceplate','Sourceplate position',
                            'Target position']
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
        auto_size_columns= False, def_col_width= 20,  expand_y= True,
        num_rows= 24, size= (450,60))],

    ]

    window = sg.Window("TubeFindr - v1.1.0",layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        output_pick_list = []
        if event == 'Run':
            while True:
                try:
                    combined_tubes_list = make_list_tubeobjects(
                        values["-BCRFILES-"]
                        )
                except IndexError:
                    sg.popup_error(
                        "Selected directory is not compatible", title="Error"
                    )
                    break
                except FileNotFoundError:
                    sg.popup_error(
                        "Files not found, please select a folder", title="Error"
                        )
                    break
                except OSError:
                    sg.popup_error(
                        "Files not found, please select a folder", title="Error"
                        )
                try:
                    make_output_pick_list(
                        combined_tubes_list,output_pick_list,
                        values["-SAMPLESIN-"])
                except IndexError:
                    sg.popup_error(
                        "Inserted file not compatible", title="Error"
                        )
                    break
                except UnboundLocalError:
                    break
                except FileNotFoundError:
                    sg.popup_error(
                        "File not found, please select a file", title="Error"
                    )
                    break
                data =[i for i in output_pick_list[1:]]
                window['-TABLE-'].update(values = data)
                break
        if event == 'Export':
            try:
                csv_sample_list_export(output_pick_list,values["-EXPORT-"])
            except FileNotFoundError:
                sg.popup_error(
                    "Output folder not found, please select a folder",
                    title="Error"
                )
            except OSError:
                sg.popup_error(
                    "Output folder not found, please select a folder",
                    title="Error"
                )
    window.close()

if __name__ == '__main__':
    main()
