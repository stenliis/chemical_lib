class ChemicalRecord(object):
    __DELIMINER = ';'

    def __init__(self, raw_data):
        [
            self.__id,
            self.__chemical_name,
            self.__chemical_formula,
            self.__monoisotopic_mass,
            self.__monoisotopic_mass_plus,
            self.__monoisotopic_mass_minus,
            self.__smile_code,
            self.__inchi,
            self.__source,
            *_
        ] = raw_data.split(';')

 
    def getChemicalName(self):
        return self.__chemical_name
    
    def getChemicalFormula(self):
        return self.__chemical_formula
    
    def getMonoisotopicMass(self):
        return self.__monoisotopic_mass
    
    def getMonoisotopicMassPlus(self):
        return self.__monoisotopic_mass_plus
    
    def getMonoisotopicMassMinus(self):
        return self.__monoisotopic_mass_minus
    
    def getSmileCode(self):
        return self.__smile_code
    
    def getInchiCode(self):
        return self.__inchi
    
    def getSourceCode(self):
        return self.__source
    
class ChemicalJar(object):
    def __init__(self, raw_data):
        self.__jar = {}
        for line in raw_data.splitlines():
            record = ChemicalRecord(line)
            name = record.getChemicalName()
            self.__jar[name] = record

    def getChemical(self, name):
        return self.__jar[name]

