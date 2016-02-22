#!/usr/bin/python

"""
USAGE:

gff_file = gff3('path/to/file')

for data in gff_file.getRecord()
    # do a thing
"""


class gffRecord:
    def __init__(self, Seqid, Source, Type, Start, End, Score, Strand, Phase, Attributes):
        self.seqid = Seqid # column 1
        self.source = Source # column 2
        self.type = Type # column 3
        self.start = Start # column 4
        self.end = End # column 5
        self.score = Score # column 6
        self.strand = Strand # column 7
        self.phase = Phase # column 8
        self.attributes = Attributes # column 9


class gff3:
    """
    A class for parsing gff3 format files, getRecord returns a generator that generates gffRecord objects
    """

    def __init__ (self, path_to_file):
        with open(path_to_file, 'r') as f :
            self.f = f

    def getRecord(self) :

        gff_regex = compile('^(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)') # regex to parse columns of annotation file

        for line in self.f :
            gff_matches = gff_regex.search(line) # find regex matches within the gene file

            yield GFFRecord(gff_matches.group(1), # Seqid
                            gff_matches.group(2), # Source
                            gff_matches.group(3), # Type
                            gff_matches.group(4), # Start
                            gff_matches.group(5), # End
                            gff_matches.group(6), # Score
                            gff_matches.group(7), # Strand
                            gff_matches.group(8), # Phase
                            gff_matches.group(9)) # Attributes

#    def PacBio_Parser():
        # do this later
        # parse self.attributes for more specific items
