# Picked list from https://zenodo.org/record/6531758/files/DoH%20Internet%20Servers%20Dataset.csv?download=1
# help from: https://www.geeksforgeeks.org/load-csv-data-into-list-and-dictionary-using-python/
# https://sparkbyexamples.com/pandas/pandas-convert-dataframe-to-dictionary/
# version sod knows as I spent a week on this - 250822 - v1.0
import pandas as pd
import json
import uuid
import copy
import ipaddress

# vars
working_dict = []
source_dict = []
gdclistdict = {'version': "1.0", 'description': "GDC_POC", 'objects': "[]"}

# functions

# convert to dict - complicated!
def csvreadanddump():
    global source_dict, working_dict
    url = 'https://zenodo.org/record/6531758/files/DoH%20Internet%20Servers%20Dataset.csv?download=1'
    cols = ['ranges', 'name', 'ASN']
    pd.options.display.max_rows = 9999
    reader = pd.read_csv(url, index_col=0, skiprows=1, names=cols)
    reader.sort_values("ranges", inplace=True)
    reader.drop_duplicates(subset="ranges", keep=False, inplace=True)
    reader.dropna(inplace=True)
    reader['description'] = ''
    reader['id'] = ''
    source_dict = reader.to_dict('records')
    working_dict = copy.deepcopy(source_dict)

# let's add the values we want to the dict then dump it
def addkeypairs():
    global working_dict
    for items in working_dict:
        items.pop("ASN")
        for things in working_dict:
            uuidvar = uuid.uuid4()
            rangevar = 'ranges'
            namevar = 'name'
            idvar = 'id'
            descvar = 'description'
            newdesc = things.get(namevar)
            currentrange = things.get(rangevar)
            things.update({rangevar: currentrange})
            things.update({descvar: newdesc})
            things.update({idvar: str(uuidvar)})

# let's just make the names unique too complicated otherwise
# concatting identical rows, into a single object with two addresses was mentally complicated
# more fixes to expand ip6 addresses - 030922
def fixuniquenames():
    global working_dict
    dictpositionvar = 0
    keytoupdate = 'name'
    rangekeytoupdate = 'ranges'
    for listdicts in working_dict:
        for key, innervalue in listdicts.items():
            if keytoupdate in key:
                currentname = listdicts.get('name')
                listdicts.update({keytoupdate: (currentname + str(dictpositionvar))})
                dictpositionvar += 1
            if rangekeytoupdate in key:
                currentrange = listdicts.get('ranges')
                currentrangecopy = copy.deepcopy(currentrange)
                ipvar = ipaddress.ip_address(currentrangecopy)
                if ipvar.version == 6:
                    currentrangev6 = ipaddress.IPv6Address(currentrange)
                    currentrangev6 = currentrangev6.exploded
                    updatev6list = currentrangev6.split(' ', 1)
                    listdicts.update({rangekeytoupdate: updatev6list})
                else:
                    currentrangev4 = currentrange
                    updatev4list = currentrangev4.split(' ', 1)
                    listdicts.update({rangekeytoupdate: updatev4list})

# This function dumps it out to JSON that Check Point can use
# added appended filetype extension - 030922
def dumptojson():
    global gdclistdict, working_dict
    desckeyname = 'description'
    objkeyname = 'objects'
    newgdcname = input("What's the name of your new GDC? >")
    gdclistdict.update({desckeyname: newgdcname})
    gdclistdict.update({objkeyname: list()})
    gdclistdict.update({objkeyname: working_dict})
    filename = input("What's the filename you want to dump to >")
    filename = filename + ".json"
    tojson = json.dumps(gdclistdict, sort_keys=True, indent=4, separators=(',', ': '))
    with open(filename, "w") as outfile:
        outfile.write(tojson)
        print("The file was written to", filename)

# runtime order
csvreadanddump()
addkeypairs()
fixuniquenames()
dumptojson()

