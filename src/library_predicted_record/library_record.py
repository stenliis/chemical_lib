from molmass import Formula
from enum import Enum
import re
from openbabel import openbabel
from rdkit import Chem

def getName(raw_data):
    return raw_data.splitlines()[0]

def getOntology(raw_data):
    name = getName(raw_data)
    result = re.match(".*-.*", name)
    if result == None:
        return "Pharmaceuticals - Parent substance"
    else:
        return "Pharmaceuticals - Metabolite"

def getFormula(raw_data):
    line = raw_data.splitlines()[2]
    [a, formula, *_] = line.split('/')
    return formula


def getSmilesUsingRdkit(inchi):
    m = Chem.MolFromInchi(inchi, True, False)
    return Chem.MolToSmiles(m)

def getSmilesUsingOpenBabel(inchi):
    conv = openbabel.OBConversion()
    conv.SetInAndOutFormats("InChI", "SMILES")
    mol = openbabel.OBMol()
    conv.ReadString(mol, inchi)
    return conv.WriteString(mol).rstrip()

def getSmiles(raw_data):
    inchi = raw_data.splitlines()[2]
    return getSmilesUsingRdkit(inchi)
    
def getInchiKey(raw_data):
    line = raw_data.splitlines()[8]
    result = re.search("^#InChiKey=(.*)", line)
    return result.group(1)

class IonMode(Enum):
    NEGATIVE = "Negative"
    POSSITIVE = "Positive"

    def __str__(self) :
        match self:
            case IonMode.NEGATIVE:
                return "Negative"
            case IonMode.POSSITIVE:
                return "Positive"

def getMode(raw_data):
    line = raw_data.splitlines()[4]
    result = re.search("^#In-silico ESI-MS/MS (.*) Spectra", line)
    value = result.group(1)
    if value == "[M+H]+":
        return IonMode.POSSITIVE
    elif value == "[M-H]-":
        return IonMode.NEGATIVE

    

def getPredictionModel(raw_data):
    mode = getMode(raw_data)
    match mode:
        case IonMode.NEGATIVE:
            return "[M-H]-"
        case IonMode.POSSITIVE:
            return "[M+H]+"

def getMolMass(raw_data):
    formula = getFormula(raw_data)
    raw_mol_mass = Formula(formula).isotope.mass
    detector_mol_mass = Formula("H").isotope.mass
    mode = getMode(raw_data)
    match mode:
        case IonMode.NEGATIVE:
            return raw_mol_mass - detector_mol_mass
        case IonMode.POSSITIVE:
            return raw_mol_mass + detector_mol_mass
    
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

class LibraryRecord(object):
    __VALUE_DELIMINER = '\t'

    def __init__(self, raw_data, lam):
        self.__name = getName(raw_data)
        record = lam(self.__name)
        self.__precursormz = getMolMass(raw_data)
        self.__prediction_model = getPredictionModel(raw_data)
        self.__formula = getFormula(raw_data)
        self.__ontopology = getOntology(raw_data)
        self.__inchikey = getInchiKey(raw_data)
        #self.__smiles = getSmiles(raw_data)
        self.__smiles = record.getSmileCode()
        self.__ion_model = getMode(raw_data)
        self.__peaks = getPeaks(raw_data)
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
Ontology:{self.__VALUE_DELIMINER}{self.__ontopology}
INCHIKEY:{self.__VALUE_DELIMINER}{self.__inchikey}
SMILES:{self.__VALUE_DELIMINER}{self.__smiles}
RETENTIONTIME:{self.__VALUE_DELIMINER}
CCS:{self.__VALUE_DELIMINER}
IONMODE:{self.__VALUE_DELIMINER}{self.__ion_model}
INSTRUMENTTYPE:{self.__VALUE_DELIMINER}In-silico
INSTRUMENT:{self.__VALUE_DELIMINER}In-silico
COLLISIONENERGY:{self.__VALUE_DELIMINER}Energy levels: 10 and 20 eV
Comment:{self.__VALUE_DELIMINER}In-silico
Num Peaks:{self.__VALUE_DELIMINER}{self.__peak_number}{self.dumpPeaks()}
"""


