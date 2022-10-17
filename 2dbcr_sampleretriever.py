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

class Tube:
    """
    string explaining everything.
    """
    def __init__(self,code,rackid,tube_position,date,time):
        self.code = code
        self.rackid = rackid
        self.position = tube_position
        self.datetime = int(f'{date}{time}')

    def __str__(self):
        return (
            f'Tubeid:{self.code}\nRackid:{self.rackid}\n'
            f'Pos:{self.position}\nLastupdated:{self.datetime}'
        )


def create_output_name():
    """
    Uses the datetime module to generate a name for the outputfile
    in the following format: pickfile_YYYYmmddHHMMSS
    """
    output_name = datetime.datetime.now()
    output_name = 'TubePickfile_'+ output_name.strftime("%Y%m%d%H%M%S")+ '.csv'
    return output_name


def check_duplicate_tube_entries(tubeslist):
    """
    Checks if the length of the set (without duplicates)
    differs in length to the list with tubes.
    """
    tubesset = set(tubeslist)
    if len(tubeslist) != len(tubesset):
        return True
    else:
        return False


def make_list_tubeobjects(filespath):
    """returns Tube list with position, tubeID, plate barcode"""
    os.chdir(filespath)
    info_list = []
    for file in os.listdir('./'):
        with open(file = file, mode ='r',errors = 'ignore') as crfile:
            crfile.readline()
            for crline in crfile:
                append = False
                crline = crline.strip('\n')
                crline = crline.split(',')
                tubeid = crline[1]
                rackid = crline[2]
                position = crline[0]
                date = crline[3]
                time = crline[4]
                if len(info_list) > 0:
                    for row in info_list:
                        if row[0] == tubeid:
                            if date >= row[3] and time >= row[4]:
                                info_list.pop(info_list.index(row))
                                append = True
                        else:
                            append = True
                else:
                    append = True
                if len(tubeid) > 0 and append is True:
                    info_list.append([tubeid, rackid, position, date, time])
    tube_list = [Tube(row[0],row[1],row[2],row[3],row[4]) for row in info_list]
    return tube_list


def make_output_pick_list(tube_list,outputlist, samplesheet):
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
            target_tube = line[1]
            targetpos = line[0]
            for tube in tube_list:
                if target_tube == tube.code:
                    outputlist.append(
                        [target_tube, tube.rackid, tube.position, targetpos]
                        )
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


def main():
    """
    Run the code
    """
    sg.theme("Reddit")

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
