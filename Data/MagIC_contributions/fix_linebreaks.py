import sys,os

def fix_line_breaks():
    """ Reads in the file given as a command line argument and rewrites it both line 
        break types '\ r' and '\ n' so that python will for sure register all lines
    """
    file_name = sys.argv[1]
    #fix line breaks between different OS and python's default
    csv_file = open(file_name, 'r')
    csv_str = csv_file.read()
    if csv_str.find('\r\n') == -1: fixed_lines = csv_str.replace('\r\n','\n')
    else: fixed_lines = csv_str.replace('\r','\n')
    new_csv_file = open(file_name, 'w')
    new_csv_file.write(fixed_lines)
    csv_file.close()

fix_line_breaks()
