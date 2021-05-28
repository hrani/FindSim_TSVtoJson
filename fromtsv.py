import csv
from collections import OrderedDict,Counter
import pprint
from os import path
import sys
tsvData = {}
tsvData = OrderedDict()

tsvData['Experiment metadata'] = ['transcriber', 'organization', 'emailId', 'exptSource', 'citationId', 'authors',
                                  'journal', 'notes', "testModel", "testMap"]
tsvData['Experiment context'] = ['exptType', 'species', 'cell-types', 'temperature-in-Celsius', 'details', 'notes']
tsvData['Stimuli'] = ['timeUnits', 'quantityUnits', 'entities', 'field', 'label', 'Data']
tsvData['Readouts'] = ['timeUnits', 'quantityUnits', 'entities', 'field', 'Data', 'useRatio', 'useXlog', 'useYlog',
                       'ratioReferenceTime', 'ratioReferenceDose', 'ratioReferenceEntities', 'entities', 'field',
                       'useSum','useNormalization', 'settleTime', 'readoutType'
                       ]
tsvData['Model mapping'] = ['modelSubset', 'itemstodelete', 'parameterChange', 'notes']

dataWidth = {"stimuli": 2, "readouts": 3, "model mapping": 3}

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def convert_value_stderr(value_stderr):
    ss = value_stderr
    if isinstance(ss,str):
        #print(" 30 ",isinstance(ss,str),value_stderr.isdigit())
        if value_stderr.isdigit():
            ss = int(value_stderr)
        elif isfloat(value_stderr):
            ss = float(value_stderr)
    return ss

def datafromTsv(src):

    ### TSV is read and poupulated into data dictionary ##############

    with open(src, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        data = OrderedDict()
        experimentType = ""
        header_key = ""
        data_stim = []
        data_read = []
        data_model = []
        stim_listcollection = []
        readout_listcollection = []
        foundDataBlock = False
        temp_stim_holder = {}
        foundstimulusblock = False
        for row in reader:
            if any(x for x in row):
                if row[0] == "Stimuli":
                    foundstimulusblock = True
                if row[0] in tsvData.keys():
                    if row[0] not in data:
                        data[row[0]] = {}
                        data[row[0]] = OrderedDict()

                    header_key = row[0]

                elif row[0] in tsvData[header_key]:
                        if row[0].lower() == "expttype":
                            experimentType = row[1].lower()
                        if row[0].lower() in ["modelsubset", "itemstodelete"]:
                            mss = []
                            if len(row[1]):
                                for ts in row[1].split(','):
                                    mss.append(ts)
                                data[header_key][row[0]] = mss
                        else:
                            if row[1] == "" and row[0]  not in ["Data","notes","details"]:
                                print("In",header_key,"section -->",row[0]," is empty or indentation needs clean up")
                                
                            if 1 < len(row):
                            	data[header_key][row[0]] = row[1]
                elif row[0].lower() in ["data", "parameterchange","readouttype","compartment"]:
                    continue
                elif row[0].lower() in ["time", "dose", "entity", "object","compartment"]:
                    foundDataBlock = True
                    continue
                else:
                    if header_key in ["Stimuli", "Readouts", "Model mapping"]:
                        t = []
                        if foundDataBlock:
                            if len(row[0]):
                                for col in range(dataWidth[header_key.lower()]):
                                    t.append(convert_value_stderr(row[col]))
                                if header_key == "Stimuli":
                                    data_stim.append(t)
                                elif header_key == "Readouts":
                                    data_read.append(t)
                                elif header_key == "Model mapping":
                                    data_model.append((t))
            else:
                #This section if multiple readout or stimulus section exist then data shdould be added in 2 blocks
                if "Readouts" in data.keys():
                    if data_read:
                        data["Readouts"]["Data"] = data_read
                        readout_listcollection.append(data["Readouts"])
                        #readout_listcollection.append([{k :data["Readouts"][k]} for k in data["Readouts"]])
                        data["Readouts"] = {}
                    data_read = []
                    foundDataBlock = False
                if "Stimuli" in data.keys():
                    if data_stim:
                        ''' Check if in stimuli block under Data ->Entity:value; if in Entity same pool is specified twiced then it replace with _number'''
                        if experimentType == "barchart":
                            ranges = {k: [str(i + 1) for i in range(v)] for k, v in
                                      Counter(item[0] for item in data_stim).items()}
                            new_list = [el if ranges[el] == ['1'] else (el + '_' + ranges[el].pop(0)) for el in
                                        [el[0] for el in data_stim]]
                            for newVal, subList in zip(new_list, data_stim):
                                #subList[0] = newVal
                                if subList[0] != newVal:
                                    subList.extend([newVal])

                                #data["Stimuli"]["label"] = newVal
                        data["Stimuli"]["Data"] = data_stim
                        stim_listcollection.append((data["Stimuli"]))
                        data["Stimuli"] = {}
                    else:
                        #stimulus block exist without data,value
                        if len(data_stim) == 0:
                            if "Data" in data["Stimuli"]:
                                del data["Stimuli"]["Data"]
                            if foundstimulusblock:
                                if any(data["Stimuli"]):
                                    stim_listcollection.append(data["Stimuli"])
                                foundstimulusblock = False
                    data_stim = []
                    foundDataBlock = False
        if readout_listcollection:
            data["Readouts"]= readout_listcollection
        else:
            pass
        if stim_listcollection:
            data["Stimuli"] = stim_listcollection
        else:
            #For consistency stimuls value are packed as list of dict value, which in timeseries there may exist more than one stimulus
            dictvaluetolist = []
            if "Stimuli" in data:
                dictvaluetolist.append([{k :data["Stimuli"][k]} for k in data["Stimuli"]])
                data["Stimuli"] = {}
                data["Stimuli"]= dictvaluetolist
        if "Model mapping" in data.keys():
            #print("147 ",data_model)
            data["Model mapping"]["parameterChange"] = data_model
            model_dictionary = data["Model mapping"]
            data["Model mapping"] = {}
            data["Model mapping"] = model_dictionary
            foundDataBlock = False
    #pprint.pprint(data)
    #print("##150")
    return  data
    # ################ TSV building into data's dictionary is End ###########


# Run the 'main' if this script is executed standalone.
if __name__ == '__main__':
    #src = sys.argv[1]
    src = "../TSV/Alessi1998_Fig6A.tsv"
    '''
    ###   Tested ####
    ### TSV Files ####                      ##TYPES###
    # -------------- TimeSeries ---------------------------
    filename = "TestTSV/ts_norm_m3b"           #TimeSeries :  1 stimulus block and 1 readouts block
    filename = "TSV/Antion2008_Fig1B_pS6"      #TimeSeries :  2 stimulus but entities are same DHPG
    # filename ="TestTSV/epsc_ratio"             #TimeSeries :  3 stimulus (push to gitlab this tsv file indentation)
    # filename = "TestTSV/epsp"                         # TimeSeries:  2 stimulus, 3 data point
    filename ="TSV/Pigott2012_Fig4C"
    # ------------------DirectParameter------------
    # filename = "TestTSV/dp"                        #DirectParameter: 0 stimulus block and 2 readoutblock
    # filename = "TestTSV/dp_kd_tau"                 #DirectParameter: 0 stimulus block

    # ------------------DoseResponse------------
    # filename = "TestTSV/dr_j2"                 #DoseResponse: 1 stimuli with no datapoint 1 readout
    # filename = "TestTSV/dr_ratio_b2c"          #DoseResponse: 1 stimuli with no datapoint
    # filename = "TSV/Yuen1999_Fig1D"            #DoseResponse: 1 stimuli with no datapoint
    #filename = "TestTSV/epsc_ratio"
    filename = "TSV/Jain2009_Fig3F"
    src = '/home/harsha/findsim2020/SynPlast_may14/AutSim/' + filename + '.tsv'
    print(" src ",src)
    '''
    if path.exists(src):
        datafromTsv(src)
    else:
        print (" file or path doesn't exist")
