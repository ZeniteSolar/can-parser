#!/usr/bin/python3
import re
import sys, getopt

def convert(input_filename: str):
    input_regex = r"\((?P<timestamp>\d{10}\.\d{6})\) can0 (?P<topic_id>\w{3})\#(?P<module>\w{2})(?P<message>\w+)"
    output_regex = '\g<timestamp>,\g<topic_id>,\g<module>,\g<message>'

    output_filename = input_filename + '.csv'

    try:
        input_file = open(input_filename, 'r')
    except IOError:
        print(f"Error: can't open file '{input_filename}'")
        sys.exit(1)

    try:
        output_file = open(output_filename, 'w')
    except IOError:
        print(f"Error: can't open file '{ouput_filename}'")
        sys.exit(1)


    pattern = re.compile(input_regex)

    output_file.write(pattern.sub(output_regex, input_file.read()))

    input_file.close()
    output_file.close()

def main(argv):
    usage = "Usage: candump2csv.py -i <input_filename>"
    input_filename = ''

    try:
        opts, args = getopt.getopt(argv, "hi:", ["ifile="])
    except getopt.GetoptError as e:
        print(str(e))
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_filename = arg
            convert(input_filename)

if __name__ == "__main__":
    main(sys.argv[1:])
