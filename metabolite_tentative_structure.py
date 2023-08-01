from pathlib import Path
from src.library_tentative_record import chemical
from src.library_tentative_record import library_record

def createJarFromFile(filename_in):
    in_data = Path(filename_in).read_text()
    return chemical.ChemicalJar(in_data)

def createLibrary(directory, outfile, mode):

    data_in = Path("data/metabolites_r.csv").read_text()

    #remove header
    first = True

    for line in data_in.splitlines():
        if first:
            first = False
            continue

        record = chemical.ChemicalRecord(line)

        lam = lambda name: record
 
        record = library_record.LibraryRecord(record.getChemicalName(), mode, lam)
        outfile.write(record.__str__())
        outfile.write("\n")


if __name__ == '__main__':
    
    #specify output
    file_library_tentative_structure_possitive = "out/metabolite_library_tentative_structure_possitive"
    file_library_tentative_structure_negative = "out/metabolite_library_tentative_structure_negative"

    #!!! Old file will be overwriten !!!
    outfile_possitive = open(file_library_tentative_structure_possitive, "w")
    outfile_negative= open(file_library_tentative_structure_negative, "w")

    #create library from model +
    createLibrary("data/computed+", outfile_possitive, True)

    #create library from model -
    createLibrary("data/computed-", outfile_negative, False)

    outfile_possitive.close()
    outfile_negative.close()

   



