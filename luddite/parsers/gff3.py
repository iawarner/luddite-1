#!/usr/bin/python

from openany import openany

gff_regex = compile('^(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)') # regex to parse columns of annotation file

class gff3(object):
    """
    A class for parsing gff3 format files, getRecord returns a generator that generates gffRecord objects
    """

    def __init__ (self, path):
		self.file = openany(path)
		self.path = path

	def __repr__(self):
		return '{}'.format(self.file)

    def parse(inc):
        gff_matches = gff_regex.search(line) # find regex matches within the gene file
        seqid        = gff_matches.group(1), # Seqid
        source       = gff_matches.group(2), # Source
        feature_type = gff_matches.group(3), # Type
        start        = gff_matches.group(4), # Start
        end          = gff_matches.group(5), # End
        score        = gff_matches.group(6), # Score
        strand       = gff_matches.group(7), # Strand
        phase        = gff_matches.group(8), # Phase
        attributes   = gff_matches.group(9)) # Attributes

        return {'seqid'      : seqid,
                'source'     : source,
                'type'       : feature_type,
                'start'      : start,
                'end'        : end,
                'score'      : score,
                'strand'     : strand,
                'phase'      : phase,
                'attributes' : attributes}

#    def PacBio_Parser():
        # do this later
        # parse self.attributes for more specific items

    if __name__ == '__main__':
    	# gff3 = gff3('file_name') # for testing
            # only will run things here if script is run directly
            # will not run if called via import

    for record in gff3.readline():
    	print '{}'.format(record)
