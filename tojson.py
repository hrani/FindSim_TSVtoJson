import json
from fromtsv import *
import re
import os
import sys

# import jsonschema

changed_header = {
    "sourceType": "exptSource", "details": "figure",
    "Metadata": "Experiment metadata",
    "Experiment": "Experiment context", "email": "emailId",
    "Modifications": "Model mapping",
    "design": "exptType", "cellType": "cell-types", "temperature": "temperature-in-Celsius",
    "modelSubset": "subset", "itemstodelete": "itemsToDelete"
}
json_header = {}
json_header = OrderedDict()
json_header["source"] = ['sourceType', 'citationId', 'authors', 'journal', 'details']
json_header["Metadata"] = ['transcriber', 'organization', 'email', 'source', 'notes', 'testModel', 'testMap']
json_header["Experiment"] = ['design', 'species', 'cellType', 'temperature', 'notes']
json_header["Stimuli"] = ['timeUnits', 'quantityUnits', 'entity', 'field']
json_header["Readouts"] = ['timeUnits', 'quantityUnits', 'entities', 'field']
json_header["Modifications"] = ['modelSubset', 'itemstodelete', 'parameterChange', 'notes']


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def convert_value_stderr(value_stderr):
    ss = value_stderr
    if isinstance(ss, str):
        # print(" 30 ",isinstance(ss,str),value_stderr.isdigit())
        if value_stderr.isdigit():
            ss = int(value_stderr)
        elif isfloat(value_stderr):
            ss = float(value_stderr)
    return ss


def getSourcefrommetadata(data, json_headkey):
    Sourceinfo = OrderedDict()
    header_key = "Experiment metadata"
    ''' From Metadata's Source is created '''
    for sublistSrc in json_header[json_headkey]:
        orgsrc = sublistSrc
        if sublistSrc in changed_header.keys():
            sublistSrc = changed_header[sublistSrc]
        if orgsrc == "details":

            if orgsrc in data["Experiment context"]:
                Sourceinfo[sublistSrc] = data["Experiment context"][orgsrc]
        else:
            if sublistSrc in data[header_key]:
                if sublistSrc in 'exptSource':
                    if data[header_key][sublistSrc].lower() == "paper":
                        data[header_key][sublistSrc] = 'paper'
                    elif data[header_key][sublistSrc].lower() == "inhouse":
                        data[header_key][sublistSrc] = 'inhouse'
                    elif data[header_key][sublistSrc].lower() == 'database':
                        data[header_key][sublistSrc] = 'database'
                    else:
                        data[header_key][sublistSrc] == 'other'
                    Sourceinfo[orgsrc] = data[header_key][sublistSrc]
                elif sublistSrc in ['authors']:
                    if sublistSrc in data[header_key]:
                        Sourceinfo[orgsrc] = data[header_key][sublistSrc]
                else:
                    if sublistSrc in data[header_key]:
                        cols = data["Experiment metadata"][sublistSrc]
                        if sublistSrc == "sourceType":
                            print(data["Experiment metadata"][sublistSrc])
                        if sublistSrc == "citationId":
                            # print(" 71 sub",sublistSrc, cols)
                            if cols.lower().find("pmid:") != -1:
                                Sourceinfo["PMID"] = int(cols[cols.lower().find("pmid: ") + 6:len(
                                    cols)])  # cols.lower().find("pmid: ") + 6:len(cols)
                            else:
                                Sourceinfo["PMID"] = int(0000)
                            if cols.lower().find("doi: ") != -1:
                                Sourceinfo["DOI:"] = cols[cols.lower().find("pmid: ") + 5:len(cols)]
                        if sublistSrc == "journal":
                            jour_year = (re.split(r'(\d+)', cols))
                            print(" 72 ", jour_year, len(jour_year))
                            if jour_year:
                                if jour_year[0]:
                                    Sourceinfo["journal"] = jour_year[0]
                                if 1 < len(jour_year):
                                    
                                    if jour_year[1]:    Sourceinfo["year"] = int(jour_year[1])
                                else: Sourceinfo["year"] = int(0000)
    return Sourceinfo


def metadata(data, json_headkey, jsonData, Source):
    data_headKey = json_headkey
    if json_headkey in changed_header.keys():
        data_headKey = changed_header[json_headkey]
    jsonData[json_headkey] = OrderedDict()
    testmodel_flag = False
    testmap_flag = False
    for sublist in json_header[json_headkey]:
        orgsrc = sublist
        if sublist in changed_header.keys():
            sublist = changed_header[sublist]
        if sublist not in ["source", "testModel", "testMap"]:
            if sublist in data[data_headKey]:
                jsonData[json_headkey].update({orgsrc: data[data_headKey][sublist]})
        if sublist in "source":
            if len(Source):
                jsonData[json_headkey].update({"source": Source})
                continue
            elif sublist in data[data_headKey]:
                if sublist in "testModel": testmodel_flag = True
                if sublist in "testMap":  testmap_flag = True
                jsonData[json_headkey].update({orgsrc: data[data_headKey][sublist]})
        elif sublist in "testModel" and not testmodel_flag:
            jsonData[json_headkey].update({"testModel": "Models/synSynth7_FMRP_19Dec2019.g"})
        elif sublist in "testMap" and not testmap_flag:
            jsonData[json_headkey].update({"testMap": "Models/synSynth7_FMRP_20Dec2019.json"})


def expt_sec(data, json_headkey, jsonData):
    data_headKey = json_headkey
    if json_headkey in changed_header.keys():
        data_headKey = changed_header[json_headkey]
    jsonData[json_headkey] = OrderedDict()
    for sublist in json_header[json_headkey]:
        orgsrc = sublist
        if sublist in changed_header.keys():
            sublist = changed_header[sublist]
        if sublist in data[data_headKey]:
            if orgsrc == "temperature":
                if data[data_headKey][sublist]:
                    # print(" 128 ",data[data_headKey][sublist])
                    temp = convert_value_stderr(data[data_headKey][sublist])
                    jsonData[json_headkey].update({orgsrc: temp})
            elif orgsrc == "design":
                if data[data_headKey][sublist].lower() == "barchart":
                    data[data_headKey][sublist] = 'BarChart'
                if data[data_headKey][sublist].lower() == "timeseries":
                    data[data_headKey][sublist] = 'TimeSeries'
                if data[data_headKey][sublist].lower() == "doseresponse":
                    data[data_headKey][sublist] = "DoseResponse"
                if data[data_headKey][sublist].lower() == 'directparameter':
                    data[data_headKey][sublist] = 'DirectParameter'
                jsonData[json_headkey].update({orgsrc: data[data_headKey][sublist]})
            else:
                jsonData[json_headkey].update({orgsrc: data[data_headKey][sublist]})


def stim_sect(data, json_headkey, jsonData, experimentType):
    if experimentType.lower() == "directparameter":
        pass
    else:
        data_headKey = json_headkey
        if json_headkey in changed_header.keys():
            data_headKey = changed_header[json_headkey]
        if data_headKey in data:
            if data[data_headKey]:
                super_temp_stimdata = []
                if experimentType.lower() == "barchart":
                    for i in range(len(data[data_headKey])):
                        temp_stimdata = {}
                        temp_stimdata = OrderedDict()
                        test = data[data_headKey][i]
                        fss = {}
                        for m, n in test.items():
                            fss[m] = n
                        for sublist in json_header[json_headkey]:
                            orgsrc = sublist
                            if sublist in fss:
                                temp_stimdata.update({orgsrc: fss[sublist]})
                        for i in range(len(fss["Data"])):

                            temp_stim_data = {}
                            temp_stim_data = OrderedDict()
                            temp_stimdataF = {}
                            temp_stimdataF = OrderedDict()
                            # val = convert_value_stderr(fss["Data"][i][1])
                            print(" fssdata ", fss["Data"], len(fss["Data"][i]))
                            if len(fss["Data"][i]) > 2:
                                print(" 189 ", fss["Data"][i][2])
                                temp_stim_data.update({"entity": fss["Data"][i][0], "value": fss["Data"][i][1],
                                                       "label": fss["Data"][i][2]})
                            else:
                                temp_stim_data.update({"entity": fss["Data"][i][0], "value": fss["Data"][i][1]})
                            temp_stim_data.update({"entity": fss["Data"][i][0], "value": fss["Data"][i][1]})
                            temp_stimdataF.update(temp_stimdata)
                            temp_stimdataF.update(temp_stim_data)
                            super_temp_stimdata.append(temp_stimdataF)
                    jsonData[json_headkey] = super_temp_stimdata

                elif experimentType.lower() == "doseresponse":
                    print(" data dose response ", data[data_headKey])
                    temp_doseres = {}
                    # print(" 184 ",data[data_headKey],type(data[data_headKey]))
                    # for i in range(len(data[data_headKey])):
                    #     print(" 186 ",data[data_headKey][i])
                    # barchart Pigott2012_Fig3A.tsv was not working so removed this block
                    # doseresponse yoshihara1990_fig2A not working
                    for i in range(len(data[data_headKey])):
                        print("203 ", data[data_headKey][i])
                        for p, q in data[data_headKey][i].items():
                            print(p, " eee ", q)
                            if p == "entities":
                                p = "entity"
                            temp_doseres[p] = q
                        # for vlist in (data[data_headKey][i]):
                        #     print( "186" , type(vlist),vlist)
                        #     for p,q in vlist.items():
                        #         if p =="entities":
                        #             p = "entity"
                        #         temp_doseres[p] = q

                    jsonData[json_headkey] = [temp_doseres]

                elif experimentType.lower() == "timeseries":
                    temp_stim = {}
                    temp_stim = OrderedDict()
                    # print(" 192 data dose response ",); pprint.pprint(data[data_headKey])
                    for stimlist in data[data_headKey]:
                        # print("stimlist" ,stimlist)
                        for stv in stimlist.items():
                            # print (stv[0],stv[1])
                            if stv[0] == "entities":
                                temp_stim["entity"] = stv[1]
                            elif stv[0] == "Data":
                                temp_stim["data"] = stv[1]
                            else:
                                temp_stim[stv[0]] = stv[1]
                        super_temp_stimdata.append(OrderedDict(temp_stim))

                    jsonData[json_headkey] = (super_temp_stimdata)
                    '''
                    for vlist in data[data_headKey]:
                        print ("## ", len(vlist),type(vlist))
                        # if isinstance(vlist,"list"):
                        #     for k in vlist:
                        #         print ("k ",k)"
                        for l in vlist.items():
                            print (" l ",l)
                            if l[0] != "Data":
                                if l[0] =="entities":
                                    temp_doseres["entity"] = l[1]
                                else:
                                    temp_doseres[l[0]] = l[1]
                            else:
                                print(l[1],type(l[1]))
                                templist = []
                                for llist in l[1]:
                                    print(llist)
                                    for i in range(len(llist)):
                                        print("## ",llist[i])
                                        templist.append((llist[i]))
                                temp_doseres["data"] = [templist]
                    '''
                    # jsonData[json_headkey] = [temp_doseres]

                    # for i in range(len(data[data_headKey])):
                    #     print( "195 ",data[data_headKey][i])
                    #     for vlist in (data[data_headKey][i]):
                    #         print("vlist",vlist)
                    #         for p, q in vlist.items():
                    #             temp_doseres[p] = q
                    # jsonData[json_headkey] = [temp_doseres]
                else:
                    jsonData[json_headkey] = data[data_headKey]


def readout_sec(data, json_headkey, jsonData):
    data_headKey = json_headkey
    if json_headkey in changed_header.keys():
        data_headKey = changed_header[json_headkey]
    temp_readdata = {}
    temp_readdata = OrderedDict()
    temp_readdata_barchart = {}
    temp_readdata_barchart = OrderedDict()
    normalization = {}
    experimentType = data["Experiment context"]["exptType"]
    if experimentType.lower() in ["directparameter"]:
        dirParalist = []
        dirParadict = {}
        for elem in data[data_headKey]:
            for hh in elem["Data"]:
                dirParadict = OrderedDict()
                # hh1 = convert_value_stderr(hh[1])
                # hh2 = convert_value_stderr(hh[2])
                dirParadict = {"entity": hh[0], "field": elem["field"], "units": elem["quantityUnits"], "value": hh[1],
                               "stderr": hh[2]}
                dirParalist.append(dirParadict)
        jsonData[json_headkey] = OrderedDict()
        jsonData[json_headkey] = {"paramdata": dirParalist}

    else:
        for qt in data[data_headKey]:
            if "quantityUnits" in qt:
                quantityUnits = qt["quantityUnits"]
        # print(" 235 qu", quantityUnits)
        for sublist in json_header[json_headkey]:
            orgsrc = sublist
            if sublist in changed_header.keys():
                sublist = changed_header[sublist]
            for fs in data[data_headKey]:
                if sublist in fs:
                    if orgsrc == "entities":
                        temp_readdata.update({orgsrc: [fs[sublist]]})
                    else:
                        temp_readdata.update({orgsrc: fs[sublist]})
                if "settleTime" in fs and int(convert_value_stderr(fs["settleTime"])) > 0:

                    temp_readdata.update({"settleTime": convert_value_stderr(fs["settleTime"])})
        if experimentType.lower() not in ["directparameter"]:
            sample_RRT = "start"
            if "ratioReferenceTime" in fs:
                RRT = fs["ratioReferenceTime"]

            if quantityUnits.lower() == "ratio":
                normalization = {"time": int(RRT)}
                if len(fs["ratioReferenceEntities"]):
                    normalization.update({"entities": [fs["ratioReferenceEntities"]]})
                if "ratioReferenceDose" in fs:
                    normalization.update({"dose": convert_value_stderr(fs["ratioReferenceDose"])})
                if experimentType.lower() in ["doseresponse"]:
                    sample_RRT = "dose"
                elif experimentType.lower() in ["barchart"]:
                    sample_RRT = "start"
                elif experimentType.lower() in ["timeseries"]:
                    if convert_value_stderr(RRT) < 0:
                        sample_RRT = "each"
                    else:
                        if "Data" in fs:
                            read_data = fs["Data"]
                            if convert_value_stderr(read_data[0][0]) == convert_value_stderr(RRT):
                                sample_RRT = "start"
                            elif convert_value_stderr(read_data[0][0]) != convert_value_stderr(RRT):
                                sample_RRT = "presetTime"
                        else:
                            read_data[0][0] = empty
                normalization.update({"sampling": sample_RRT})
            if quantityUnits == "ratio" and convert_value_stderr(RRT) >= 0 and experimentType.lower() == "timeseries":
                print("TSV", tsvfilename, "quantityUnits:",quantityUnits," Dose: ", fs["ratioReferenceDose"], "Time ",fs["ratioReferenceTime"], "readoutdata ", read_data[0][0], "sampling ", sample_RRT)
            elif "ratioReferenceDose" in fs:
                print("TSV", tsvfilename, "quantityUnits:",quantityUnits," Dose: ", fs["ratioReferenceDose"], "Time ", fs["ratioReferenceTime"], "sampling ", sample_RRT)
            else:
                print("TSV", tsvfilename, "quantityUnits:",quantityUnits, "Time ", fs["ratioReferenceTime"], "sampling ", sample_RRT)
            if bool(normalization):
                temp_readdata.update({"normalization": normalization})
            if (fs["useXlog"] == "FALSE") and (fs["useYlog"] == "FALSE"):
                pass
            else:
                temp_readdata.update(
                    {"display": (
                    {"useXlog": bool(str(fs['useXlog'] == 'true')), "useYlog": bool(fs['useYlog'] == 'true')})})
        if "Data" in fs:
            read_data = fs["Data"]
            # for t in read_data:
            #     for i in range(len(t)):
            #         t[i] = convert_value_stderr(t[i])
            if experimentType.lower() == "barchart":
                # readout_data = data[data_headKey]["Data"]
                readout_data = fs["Data"]
                stimulus_data_dose_order = []
                for nofentry in range(len(jsonData["Stimuli"])):
                    if "label" in jsonData["Stimuli"][nofentry]:
                        stimulus_data_dose_order.append(jsonData["Stimuli"][nofentry]["label"])
                    else:
                        stimulus_data_dose_order.append(jsonData["Stimuli"][nofentry]["entity"])

                strtesting = []
                if len(stimulus_data_dose_order):
                    for ss in fs["Data"]:
                        l = str(ss[0]).zfill(len(stimulus_data_dose_order))
                        testing_order = []
                        for i in range(len(l)):
                            if l[i] == '1':
                                # print(" 369 ",stimulus_data_dose_order[2])
                                testing_order.append(stimulus_data_dose_order[i])
                        # ss1 = convert_value_stderr(ss[1])
                        # ss2 = convert_value_stderr(ss[2])
                        strtesting.append(
                            (OrderedDict({"stimulus": testing_order, "value": ss[1], "stderr": ss[2]})))
                if len(strtesting):
                    temp_readdata.update({"bardata": strtesting})
            if experimentType.lower() == "doseresponse" or experimentType.lower() == "timeseries":
                if len(read_data):
                    temp_readdata.update({"data": read_data})
        jsonData[json_headkey] = OrderedDict()
        jsonData[json_headkey] = temp_readdata


def model(data, json_headkey, jsonData):
    if json_headkey in changed_header.keys():
        data_headKey = changed_header[json_headkey]
    # jsonData[json_headkey] = OrderedDict()
    modification_dictionary = {}
    modification_list = []
    modification_dictionary = OrderedDict()
    for sublist in json_header[json_headkey]:
        orgsrc = sublist
        if sublist in changed_header.keys():
            sublist = changed_header[sublist]
        mol = data[data_headKey]

        if orgsrc in mol:
            if orgsrc == "parameterChange":
                parameterlist = []
                if len(data[data_headKey]["parameterChange"]) != 0:
                    for l in data[data_headKey][orgsrc]:
                        # l2 = convert_value_stderr(l[2])
                        if l[1].lower() in ["conc", "concinit"]:
                            parUnit = 'mM'
                        else:
                            parUnit = "none"
                        parameterlist.append({"entity": l[0], "field": l[1], "value": l[2], "units": parUnit})
                if bool(parameterlist):
                    modification_dictionary[sublist] = parameterlist
            elif data[data_headKey][orgsrc] != "":
                if sublist == 'subset':
                    if data[data_headKey][orgsrc] != "all":
                        modification_dictionary[sublist] = data[data_headKey][orgsrc]
                else:
                    if sublist.lower() == "itemstodelete":
                        if data[data_headKey][orgsrc]:
                            modification_dictionary[sublist] = data[data_headKey][orgsrc]
                    else:
                        modification_dictionary[sublist] = data[data_headKey][orgsrc]
    if bool(modification_dictionary):
        jsonData[json_headkey] = {}
        jsonData[json_headkey] = OrderedDict()
        jsonData[json_headkey] = modification_dictionary


def tsv2Json(data, des, filename):
    # pprint.pprint(data)
    print("###################### TSV to Json conversion done here###################")
    ''' Clearing header_key for reuse'''
    json_headkey = ""
    jsonData = {}
    jsonData = OrderedDict()
    experimentType = ""
    Source = OrderedDict()
    global tsvfilename
    tsvfilename = filename
    stimulus_data_dose = []

    for json_headkey in json_header:
        head_key = json_headkey
        if "Experiment context" in data:
            experimentType = data["Experiment context"]["exptType"]
        else:
            print("Check the experiment Type in the TSV")

        if json_headkey.lower() == "source":
            Source = getSourcefrommetadata(data, json_headkey)
        elif json_headkey.lower() == "metadata":
            metadata(data, json_headkey, jsonData, Source)
        elif json_headkey.lower() == "experiment":
            expt_sec(data, json_headkey, jsonData)
        elif json_headkey.lower() == "stimuli":
            stim_sect(data, json_headkey, jsonData, experimentType)
        elif json_headkey.lower() == "readouts":
            readout_sec(data, json_headkey, jsonData)
        elif json_headkey.lower() == "modifications":
            model(data, json_headkey, jsonData)
    # pprint.pprint(jsonData)

    json_object = json.dumps(jsonData, indent=4)
    # Writing to sample.json
    # des = '/tmp/doseresponse/json/' + filename + '.json'
    print(" Json file written to  ", des)
    with open(des, "w", ) as outfile:
        outfile.write(json_object)
    # print("========================= Validating the json file =================")

    validate = "python validate.py " + des + " findSimSchema.json"
    print("## ", validate)
    t = os.system(validate)
    print("\n")


if __name__ == '__main__':

    ###   Tested ####
    # -------------- TimeSeries ---------------------------

    # filename = "TestTSV/ts_norm_m3b"           #TimeSeries :  1 stimulus block and 1 readouts block
    # filename = "TSV/Antion2008_Fig1B_pS6"      #TimeSeries :  2 stimulus but entities are same DHPG, 1 readout
    # filename ="TestTSV/epsc_ratio"             #TimeSeries :  3 stimulus 1 readout
    # filename = "TestTSV/epsp"                  # TimeSeries:  2 stimulus, 3 data point, 1 readout
    #
    # #------------------DirectParameter------------
    # filename = "TestTSV/dp"                        #DirectParameter: 0 stimulus block and 2 readoutblock with 2 pools
    # filename = "TestTSV/dp_Kd_tau"                 #DirectParameter: 0 stimulus block 2readouts wit 2 pools

    # ------------------DoseResponse------------
    # filename = "TestTSV/dr_j2"                 #DoseResponse: 1 stimuli with no datapoint 1 readout
    # filename = "TestTSV/dr_ratio_b2c"          #DoseResponse: 1 stimuli with no datapoint
    # filename = "TSV/Yuen1999_Fig1D"            #DoseResponse: 1 stimuli with no datapoint

    # ------------------ BarChart------------
    # filename = "TestTSV/bc_ratio_sb8"                #BarChart : 1 stimulus block (3 pool's Ca,DAG,AA) and 1 readouts block
    # filename = "TSVtoJson/Antion2008_Fig3B_pS6"
    # filename = "TSVtoJson/Antion2008_Fig3B_pS6_old"  #BarChart : 1 stimulus block
    #                                                  # (3 pools but PI3K is repeated, changed the name as PI3R_1, PI3R_2)
    #                                                  # and 1 readouts block check since barchart need to replace 000 as DHPG,PI3K_1,PI3K_2
    # filename = "TSV/Troca-Martin2011_Fig2E"
    # filename = "TSV/Kumar2005_Fig6L_pERK"
    # filename = "TSV/Gottschalk1999_Fig2B"
    # filename = "TSV/Andreozzi2003_Fig2B"
    # filename = 'TestTSV/bc_ratio_sb8'
    # filename ="old_newTSV/newFindSim/TSV/TestTSV/New_ts_norm_m3b"
    # src = '/home/harsha/findsim2020/SynPlast_ap22/AutSim/' + filename + '.tsv'
    # ------------------  End ------
    src = sys.argv[1]
    des = sys.argv[2]
    # print(src)
    # print(des)
    filenames, fileext = os.path.splitext(src)
    filename = os.path.basename(filenames)
    data4mtsv = ""
    if path.exists(src):
        data4mtsv = datafromTsv(src)
    else:
        print(" file or path doesn't exist ", src)
    if data4mtsv:
        tsv2Json(data4mtsv, des, filename)
    else:
        print("Return data dictionary was empty")
