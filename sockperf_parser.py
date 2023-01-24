#!/usr/bin/env python3
import json
import re


def to_format(input_string, header=None, out_format=None):
    """Convert spockperf output string into one of the available formats i.e. csv or json"""
    summary = 'Summary: (.*)'
    msg_size = 'using msg-size=([0-9])+'
    secondary_units = '\((.*)\)'
   
    msg_size_str = re.search(msg_size,input_string).group(0)
    msg_size = msg_size_str.replace('using msg-size=','')
    print(msg_size,end=',')
    for match in re.findall(summary,input_string):
        number_and_unit = '([0-9])+.([0-9])+(.*)'
        res = re.search(number_and_unit,match).group(0)
        res = re.sub(secondary_units,'',res)
        res = res.replace('sockperf: Summary: ','')
        res = res.replace('is','')
        if header:
            for h in header:
                res =  res.replace(h,'')
        for s in res.split():
                print(s,end=',')
    print('')
