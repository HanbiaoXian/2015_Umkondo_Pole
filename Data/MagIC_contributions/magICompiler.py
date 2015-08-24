import sys
import os

def main():
    """ A simple file that searches all subdirectories for pmag_speciemns.txt and magic_measurements.txt then compiles all the data under one header in a single file in the directory given.

        Syntax: python magICompiler.py <directory path from current directory>

        Flags:
            -h - displays this help message
    """

    if '-h' in sys.argv:
        help(main)

    wd = os.getcwd()
    pmag_files = ("pmag_specimens.txt","magic_measurements.txt","er_sites.txt","er_samples.txt","er_specimens.txt")

    if sys.argv:
        for item in sys.argv:
            if item.count("/") > 0:
                wd = item
    if not wd.endswith("/"):
        wd += "/"

    final_pmag_specimens = ""
    final_magic_measurements = ""
    final_er_sites = ""
    final_er_samples = ""
    final_er_specimens = ""
    current_pmag_specimens_header = ""
    current_magic_measurements_header = ""
    current_er_sites_header = ""
    current_er_samples_header = ""
    current_er_specimens_header = ""

    directories = [x[0] for x in os.walk(wd)]
    if wd in directories:
        directories.remove(wd)

    for directory in directories:
        for pmag_file_name in pmag_files:
            try: pmag_file = open(directory + "/" + pmag_file_name, 'r')
            except IOError: 
                print("IOError no file: " + directory + "/" + pmag_file_name);
                continue
            if pmag_file_name == pmag_files[0]:
                [final_pmag_specimens,current_pmag_specimens_header] = append_header_and_file(final_pmag_specimens,current_pmag_specimens_header,pmag_file)
            elif pmag_file_name == pmag_files[1]:
                [final_magic_measurements,current_magic_measurements_header] = append_header_and_file(final_magic_measurements,current_magic_measurements_header,pmag_file)
            elif pmag_file_name == pmag_files[2]:
                [final_er_sites,current_er_sites_header] = append_header_and_file(final_er_sites,current_er_sites_header,pmag_file)
            elif pmag_file_name == pmag_files[3]:
                [final_er_samples,current_er_samples_header] = append_header_and_file(final_er_samples,current_er_samples_header,pmag_file)
            elif pmag_file_name == pmag_files[4]:
                [final_er_specimens,current_er_specimens_header] = append_header_and_file(final_er_specimens,current_er_specimens_header,pmag_file)

    final_pmag_specimens_file = open(wd + "pmag_specimens.txt", 'w')
    final_pmag_specimens = "tab \tpmag_specimens\n" + current_pmag_specimens_header + final_pmag_specimens
    final_pmag_specimens_file.write(final_pmag_specimens)

    final_magic_measurements_file = open(wd + "magic_measurements.txt", 'w')
    final_magic_measurements = "tab \tmagic_measurements\n" + current_magic_measurements_header + final_magic_measurements
    final_magic_measurements_file.write(final_magic_measurements)

    final_er_sites_file = open(wd + "er_sites", 'w')
    final_er_sites = "tab \ter_sites\n" + current_er_sites_header + final_er_sites
    final_er_sites_file.write(final_er_sites)

    final_er_samples_file = open(wd + "er_samples.txt", 'w')
    final_er_samples = "tab \ter_samples\n" + current_er_samples_header + final_er_samples
    final_er_samples_file.write(final_er_samples)

    final_er_specimens_file = open(wd + "er_specimens.txt", 'w')
    final_er_specimens = "tab \ter_specimens\n" + current_er_specimens_header + final_er_specimens
    final_er_specimens_file.write(final_er_specimens)

def append_header_and_file(final_pmag,current_pmag_header,pmag_file):
        next_pmag_file = pmag_file.read()
        next_header = next_pmag_file.splitlines(True)[1]
        if not current_pmag_header or len(current_pmag_header.split('\t')) > len(next_header.split('\t')):
            current_pmag_header = next_header
        temp = ""
        for line in next_pmag_file.splitlines(True)[2:]:
            temp += line
        next_pmag_file = temp
        final_pmag += (next_pmag_file + '\n')
        return final_pmag, current_pmag_header

main()

#                final_pmag_specimens.strip("\n")
#                final_pmag_specimens.strip("\t")
#                final_pmag_specimens.strip(' ')
#                next_pmag_file.strip("\n")
#                next_pmag_file.strip("\t")
#                next_pmag_file.strip(" ")
