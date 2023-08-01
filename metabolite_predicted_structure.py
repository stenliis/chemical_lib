from pathlib import Path
from src.library_predicted_record import chemical
from src.library_predicted_record import library_record
import os

def createJarFromFile(filename_in):
    in_data = Path(filename_in).read_text()
    return chemical.ChemicalJar(in_data)

def decodeRawRecord(record):
    if record.count('\n') < 6:
        return ""
    return record


def createLibrary(directory, outfile, jar):
    lam = lambda name: jar.getChemical(name)

    for filename in sorted(os.listdir(directory)):
        raw_data = Path(directory + "/" + filename).read_text()
        decoded_data = decodeRawRecord(raw_data)
        if decoded_data.__len__() == 0:
            print(f"""Probably invalid data in file: {directory}/{filename} => skipped""")
            continue
        record = library_record.LibraryRecord(decoded_data, lam)
        outfile.write(record.__str__())
        outfile.write("\n")

if __name__ == '__main__':
    
    #specify output
    file_library_predicted_structure_possitive = "out/library_predicted_structure_possitive"
    file_library_predicted_structure_negative = "out/library_predicted_structure_negative"

    #!!! Old file will be overwriten !!!
    outfile_possitive = open(file_library_predicted_structure_possitive, "w")
    outfile_negative = open(file_library_predicted_structure_negative, "w")

    #create chemical jar
    jar = createJarFromFile("data/chemical_list.csv")

    #create library from model +
    createLibrary("data/computed+", outfile_possitive, jar)

    #create library from model -
    createLibrary("data/computed-", outfile_negative, jar)

    outfile_possitive.close()
    outfile_negative.close()
