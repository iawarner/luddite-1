from luddite.parsers import fasta
from luddite.parsers import gff3
from luddite.parsers import dat

class TestFasta(object):
	"""Fasta file parser testing"""
	def test_init(self):
		this_file=fasta.file('test_files/test.fasta.bz2')

	
class TestGFF(object):
	"""docstring for TestGFF"""
	def test_init(self):
		this_file=gff3.file('test_files/test.gff3.bz2')	

class TestDAT(object):
	"""docstring for TestGFF"""

	def test_init(self):
		this_file=dat.file('test_files/test.dat.bz2')	

	def test_read(self):
		this_file=dat.file('test_files/test.dat.bz2')
		for record in this_file.read():
			print(record)
