#!/usr/bin/env python3

import json
import csv
import argparse


def qperf_convert_data(in_path, out_path, header, out_format):
    """Convert qperf output file into one of the available formats i.e. csv or json"""
    with open(in_path, 'r',encoding='utf8') as in_file:
        name = in_file.readline()
        lines = in_file.readlines()
    end = 'quit:'
    with open(out_path, 'w',encoding='utf8') as out_file:
        if out_format == 'json':
            json_list = []
        elif out_format == 'csv':
            writer = csv.writer(out_file)
            writer.writerow(header)
        for line in lines:
            if end in line:
                break
            if name not in line:
                line = line.split()
                if len(line) > 3:
                    unit = line[3]
                else:
                    unit = 'NA'
                if out_format == 'json':
                    json_list.append({header[0]: line[0], header[1]: line[2], header[2]: unit})
                elif out_format == 'csv':
                    writer.writerow([line[0], line[2], unit])
        if out_format == 'json':
            json.dump(json_list, out_file)


def to_format(input_string, header, out_format):
    """Convert qperf output string into one of the available formats i.e. csv or json"""
    lines = input_string.split('\n')
    name = lines.pop(0)
    end = 'quit:'
    output = [] if out_format == 'json' else header[0] + ',' + header[1] + ',' + header[2] + '\n'
    #if out_format == 'csv':
    #    output =     elif out_format == 'json':
    #    output = []
    for line in lines:
        if end in line:
            break
        if name not in line:
            line = line.split()
            if len(line) > 3:
                unit = line[3]
            else:
                unit = 'NA'
            if out_format == 'json':
                output.append(
                    {header[0]: line[0], header[1]: line[2], header[2]: unit})
            elif out_format == 'csv':
                output += line[0] + ',' + line[2] + ',' + unit + '\n'
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='CSV and Json parser for qperf output')
    parser.add_argument('--output', type=str, help='Output filename')
    parser.add_argument('--input', type=str, help='qperf log file')
    parser.add_argument('--header', type=str, help='Custom csv header')
    parser.add_argument('--format', type=str, help='CSV or JSON')
    args = parser.parse_args()

    if args.header:
        header_information = args.header
    else:
        header_information = ['Metric', 'Value', 'Unit']

    if args.format == 'csv':
        qperf_convert_data(args.input, args.output, header_information, out_format='csv')
    elif args.format == 'json':
        qperf_convert_data(args.input, args.output, header_information, out_format='json')
