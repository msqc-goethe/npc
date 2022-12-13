#!/usr/bin/env python3

import json
import csv
import argparse


def qperf_convert_data(in_path,out_path,header,out_format):
    f = open(in_path,'r')
    name = f.readline()
    end = 'quit'
    c = open(out_path,'w')

    if out_format == 'json':
        l = []
    elif out_format == 'csv':
        writer = csv.writer(c)
        writer.writerow(header)

    for line in f.readlines():
        if end in line:
            break
        if name not in line:
            line = line.split()
            if len(line) > 3:
                unit = line[3]
            else:
                unit = 'NA'
            if out_format == 'json':
               l.append({header[0]:line[0],header[1]:line[2],header[2]:unit})
            elif out_format == 'csv':
               writer.writerow([line[0],line[2],unit])
    if out_format == 'json':
        json.dump(l,c)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSV and Json parser for qperf output')
    parser.add_argument('--output',type=str,help='Output filename')
    parser.add_argument('--input',type=str,help='qperf log file')
    parser.add_argument('--header',type=str,help='Custom csv header')
    parser.add_argument('--format',type=str,help='CSV or JSON')
    args = parser.parse_args()

    if args.header:
        header = args.header
    else:
        header = ['Metric','Value','Unit']

    if args.format == 'csv':
        qperf_convert_data(args.input,args.output,header,out_format='csv')
    elif args.format == 'json':
        qperf_convert_data(args.input,args.output,header,out_format='json')
