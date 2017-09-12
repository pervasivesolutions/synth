"""evt2csv: Given an event log, produce a sparse matrix.

    Event logs are naturally compact.
    Each row consists of a time, a device ID, and then optionally (property,value)
    pairs for each property that changes at that time.

    This module takes such representations and expands them into a sparse
    matrix, with a header row listing all property names.

    These functions all operate on an externally-defined dict
    which can be initialised to {}

    Input is either read from a .evt file:
        c = read_evt_file("filename.evt")
        convert_to_csv(c)
    or input property-by-property:
        evts = {}
        insert_properties(evt,...)  # Repeatedly
        convert_to_csv(c)


    This module can also be run on the command-line as a standalone utility, with filenames as arguments.
"""

import re
import logging

SEP = "!"

def insert_properties(the_dict, time, device_id, properties):
    """Update an event dict, given a set of properties that are updated
       at a particular <time> on a particular <device_id>"""
    newProps = []

    # Construct list of (prop,value)
    for k in properties.keys():
        if k not in ["$id","$ts"]:
            newProps.append( (k, properties[k]) )

    # Insert
    key = str(time) + SEP + str(device_id)
    if key in the_dict:
        existingProps = the_dict[key] # Extend list if it already exists
    else:
        existingProps = []
    existingProps.extend(newProps)

    the_dict[key] = existingProps


def convert_to_csv(the_dict):
    """Convert dict and return a CSV file contents as a string"""
    out_str=""

    # Collect all property names
    props = []
    for k in the_dict.keys():
        for (p,v) in the_dict[k]:
            if p not in props:
                props.append(p)
    props.sort()

    # Write header row (i.e. column titles)
    out_str += "$ts,$id," + ",".join( [str(x) for x in props] ) + "\n"

    # Write time series
    for k in sorted(the_dict):
        (t,i) = k.split(SEP)
        out_str += t + ","
        out_str += i + ","
        for propName in props:  # For every column
            found=False
            for (p,v) in the_dict[k]: # If we have a value, write it
                if p==propName:
                    out_str += str(v)+","
                    found=True
                    break
            if not found:
                out_str += ","
        out_str += "\n"

    return out_str

def read_evt_file(filename):
    """Load an .evt file as a dict"""
    # An event file can contains two types of line:
    #     *** Comment lines that start with three stars, which we ignore
    #     2017-09-08 01:43:50 $id,6a-02-d2-4c-5d-31,$ts,1504835030.7,is_demo_device,True,label,Thing 0,
    # We ignore the human datestamp.
    # Following that are pairs thus: "<propertyname>,<propertyvalue>,"
    # Pairs for $ts and $id are mandatory.
    # No other pairs are mandatory, e.g. a heartbeat could contain nothing else.
    result = {}
    seen_start = False
    for line in open(filename,"rt").read().splitlines():
        line = line.rstrip(",") # Trailing comma is legal but confusing
        if line.startswith("*** New simulation"):
            if seen_start:
                logging.warning(".evt file contains multiple simulation runs - ignoring all but the last run")
                result = {}
            seen_start = True
        if line.startswith("***"):
            continue
        if not re.search("^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][ T][0-9][0-9]:[0-9][0-9]:[0-9][0-9] ", line):
            logging.error("Unrecognised line format in .evt file "+str(line))
        singles = line[20:].split(",")
        pairs = zip(singles[::2], singles[1::2])
        properties = dict(pairs)
        insert_properties(result, properties["$ts"], properties["$id"], properties)
    return result 

if __name__ == "__main__":
    import sys
    for filename in sys.argv[1:] :
        print "Converting ",filename
        evt = read_evt_file(filename+".evt")
        open(filename+"_converted.csv","wt").write(convert_to_csv(evt))
    print "Done"