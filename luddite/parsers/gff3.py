#!/usr/bin/python

from openany import openany
from re import *

gff_regex = compile('^(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')

class gff3(object):
    """
    A class for parsing gff3 format files.
    """

    def __init__ (self, path):
        self.file = openany(path)
        self.path = path

    def __repr__(self):
        return '{}'.format(self.file)

    def read(self):
        for line in self.file :
            if line[0]=='>':
                break
            elif line[0]!='#':
                yield parse(line)

def parse(line):
    gff_matches  = gff_regex.search(line)
    seqid        = gff_matches.group(1)
    source       = gff_matches.group(2)
    feature_type = gff_matches.group(3)
    start        = gff_matches.group(4)
    end          = gff_matches.group(5)
    score        = gff_matches.group(6)
    strand       = gff_matches.group(7)
    phase        = gff_matches.group(8)
    attributes   = gff_matches.group(9)

    return {'seqid'      : seqid,
            'source'     : source,
            'type'       : feature_type,
            'start'      : start,
            'end'        : end,
            'score'      : score,
            'strand'     : strand,
            'phase'      : phase,
            'attributes' : attributes}

if __name__ == '__main__':
    gff = gff3('/Users/Marina/Desktop/test.gff')
    for record in gff.read():
        print '{}'.format(record)
