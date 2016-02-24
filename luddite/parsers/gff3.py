#!/usr/bin/python

from openany import openany

gff_regex = compile('^(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')

class gff3(object):
    """
    A class for parsing gff3 format files, getRecord returns a generator that generates gffRecord objects
    """

    def __init__ (self, path):
		self.file = openany(path)
		self.path = path

	def __repr__(self):
		return '{}'.format(self.file)

    def parse(line):
        gff_matches  = gff_regex.search(line)
        seqid        = gff_matches.group(1),
        source       = gff_matches.group(2),
        feature_type = gff_matches.group(3),
        start        = gff_matches.group(4),
        end          = gff_matches.group(5),
        score        = gff_matches.group(6),
        strand       = gff_matches.group(7),
        phase        = gff_matches.group(8),
        attributes   = gff_matches.group(9))

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
        # parse attributes for more specific items

    if __name__ == '__main__':
    	# gff3 = gff3('file_name') # for testing
            # only will run things here if script is run directly
            # will not run if called via import

    for record in gff3.readline():
    	print '{}'.format(record)
