from pathlib import Path
import re
from src.library_tentative_record import chemical

def getParentName(name):
    [parent_name, metabolite_stuff] = name.split('-')
    return parent_name

def getFormulaFromParent(name, lam):
    parent_name = getParentName(name)
    parent_record = lam(parent_name)
    return parent_record.getChemicalFormula()

def decodeRawRecord(record):
    if record.count('\n') < 6:
        return ""
    return record

def getDecodeParentFile(name, mode):
    filename = getParentName(name)
    if mode:
        directory = "data/computed+"
    else:
        directory = "data/computed-"
    raw_data = Path(directory + "/" + filename).read_text()
    decoded_data = decodeRawRecord(raw_data)
    if decoded_data.__len__() == 0:
        print(f"""Probably invalid data in file: {directory}/{filename} => skipped""")
        return ""
    return decoded_data

def getInchiKeyFromParentPrediction(name, mode):
    decoded_data = getDecodeParentFile(name, mode)
    
    line = decoded_data.splitlines()[8]
    result = re.search("^#InChiKey=(.*)", line)
    return result.group(1)


def getSmileCodeFromParenCsv(name, lam):
    parent_name = getParentName(name)
    parent_record = lam(parent_name)
    return parent_record.getSmileCode()

def getPeaks(raw_data):
    my_dict = dict()

    for line in raw_data.splitlines():
        #skip empty line
        if not line:
            continue

        #terminete after reaching energy2
        if line == "energy2":
            break

        #only peaks start with digit, so skip everything else
        if not line[0].isdigit():
            continue
        
        words = line.split()
        a = words[0]
        if float(a)%1 == 0:
            continue
        b = float(words[1])

        #add new record or add value to existing
        if a in my_dict.keys():
            my_dict[a] = b + my_dict[a]
        else:
            my_dict[a] = b

    #convert sorted dict
    sorted_dict = {}
    sorted_key = sorted(my_dict.keys(), key = lambda x:float(x))
    for key in sorted_key:
        sorted_dict[key] = str(my_dict[key])
    return sorted_dict

def getPeaksFromParentPrediction(name, mode):
    data = getDecodeParentFile(name, mode)
    return getPeaks(data)   

def getPossitiveModeMassFromCsv(name):
    data_in = Path("data/metabolites_r.csv").read_text()
    search = ";" + name + ";"
    for line in data_in.splitlines():
        #print(line)
        if search in line:
            record = chemical.ChemicalRecord(line)
            return record.getMonoisotopicMassPlus()
    return ""

def getNegativeModeMassFromCsv(name):
    data_in = Path("data/metabolites_r.csv").read_text()
    search = ";" + name + ";"
    for line in data_in.splitlines():
        #print(line)
        if search in line:
            record = chemical.ChemicalRecord(line)
            return record.getMonoisotopicMassMinus()
    return ""

def getMassCsv(name, mode):
    if mode:
        return getPossitiveModeMassFromCsv(name)
    else:
        return getNegativeModeMassFromCsv(name)

class LibraryRecord(object):
    __VALUE_DELIMINER = '\t'

    def __init__(self, name, mode, lam):
        self.__name = name
        self.__precursormz = getMassCsv(name, mode)
        if mode:
            self.__prediction_model = "[M+H]+"
            self.__ion_model = "Positive"
        else:
            self.__prediction_model = "[M-H]-"
            self.__ion_model = "Negative"
        
        self.__formula = getFormulaFromParent(name, lam)
        self.__inchikey = getInchiKeyFromParentPrediction(name, lam)
        self.__smiles = getSmileCodeFromParenCsv(name, lam)
        self.__peaks = getPeaksFromParentPrediction(name, mode)
        self.__peak_number = len(self.__peaks)
    
    def dumpPeaks(self):
        ret=''
        is_first = False
        for a, b in self.__peaks.items():
            if is_first:
                is_first = False
            else:
                ret = f"""{ret}\n"""

            b_rounded = "{:.2f}".format(round(float(b), 2))
            a_rounded = "{:.5f}".format(round(float(a), 5))
            ret = f"""{ret}{a_rounded}{self.__VALUE_DELIMINER}{b_rounded}"""
        return ret


    def __str__(self) :
        return f"""NAME:{self.__VALUE_DELIMINER}{self.__name}
PRECURSORMZ:{self.__VALUE_DELIMINER}{self.__precursormz}
PRECURSORTYPE:{self.__VALUE_DELIMINER}{self.__prediction_model}
FORMULA:{self.__VALUE_DELIMINER}{self.__formula}
Ontology:{self.__VALUE_DELIMINER}Pharmaceuticals - Metabolite S or SR
INCHIKEY:{self.__VALUE_DELIMINER}{self.__inchikey}
SMILES:{self.__VALUE_DELIMINER}{self.__smiles}
RETENTIONTIME:{self.__VALUE_DELIMINER}
CCS:{self.__VALUE_DELIMINER}
IONMODE:{self.__VALUE_DELIMINER}{self.__ion_model}
INSTRUMENTTYPE:{self.__VALUE_DELIMINER}In-silico
INSTRUMENT:{self.__VALUE_DELIMINER}In-silico
COLLISIONENERGY:{self.__VALUE_DELIMINER}Energy levels: 10 and 20 eV
Comment:{self.__VALUE_DELIMINER}In-silico
Num Peaks:{self.__VALUE_DELIMINER}{self.__peak_number + 1}{self.dumpPeaks()}
{self.__precursormz}{self.__VALUE_DELIMINER}50
"""


