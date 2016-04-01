from luddite.parsers import fasta
from luddite.parsers import gff3

class TestFasta(object):
	"""Fasta file parser testing"""
	def test_init(self):
		this_file=fasta.file('test_files/test.fasta')

	
class TestGFF(object):
	"""docstring for TestGFF"""
	def test_init(self):
		this_file=gff3.file('test_files/test.gff3')	