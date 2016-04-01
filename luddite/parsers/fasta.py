"""
Yet another fasta parsing module (Should probably dig into khmer and look / steal theres at some point tbh)
"""
from __future__ import absolute_import

from ..utils import openany

class file (object):
	"""
	The fasta class is a base class for interacting with FASTA files
	"""
	def __init__ ( self , path ):
		"""Summary
		
		Args:
		    path (string): The path to the FASTA file
		"""
		self.file = openany(path)
		self.path = path

	def __repr__(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		return '{}'.format(self.file)

	def read (self):
		"""
		A fasta file iterator , reads one record at a time
		
		Yields:
		    dict:{ 
		    	   header : The FASTA records header,
		    	   sequence : The appropriate sequence
		    	  }
		"""
		buff = ''
		record_break = "\n>"

		while True:
			while record_break in buff:
				position = buff.index(record_break)
				yield(parse(buff[:position]))
				buff = buff[position+len(record_break):]

			chunk = self.file.read(4096)
			if not chunk:
				yield parse(buff)
				break

			buff+=chunk

def parse(inc):
	"""
	An internal function for parsing an individual record into its header and sequence
	
	Args:
	    inc (TYPE): Description
	
	Returns:
	    TYPE: Description
	"""
	[header,sequence] = inc.split("\n" , 1)
	if header[0] == '>':
		header=header[1:]
	sequence = sequence.replace('\n','')
	return {'header' : header , 'sequence' :sequence}





if __name__ == '__main__':
	fasta = fasta('VFDB_setA_nt.fas')

	for record in fasta.read():
		print '{}'.format(record)
	






