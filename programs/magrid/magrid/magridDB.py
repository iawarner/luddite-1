import sys
import os
import logging
import hashlib
import sqlite3 as sql


from ete3 import NCBITaxa

from luddite.databases import uniprot
from config import MAGRID_DB_PATH




logger = logging.getLogger(__name__)

ncbi=NCBITaxa()

"""
This isn't updating like it is supposed to - will likely need a work around or to hack into ete3's NCBITaxa
"""
#ncbi.update_taxonomy_database()

def c_dump(x):
	return json.dumps(x, separators=(',',':'))



class magridDataBase (object):

	def __init__(self , name):

		self.this_DB_PATH = os.path.join(MAGRID_DB_PATH, name)

		try:
			os.makedirs(self.this_DB_PATH)
		except OSError as error:  
			if not os.path.isdir(self.this_DB_PATH):
				raise

		self.fasta_path	 = os.path.join(self.this_DB_PATH , name + '.fasta')
		self.dmnd_path	 = os.path.join(self.this_DB_PATH , name + '.dmnd')
		self.sq3_path	 = os.path.join(self.this_DB_PATH , name + '.sq3')
	

		try:
			self.sq3_con	 = sql.connect(self.sq3_path)
			self.sq3_cur 	 = self.sq3_con.cursor()
			self.sq3_cur.execute("CREATE TABLE IF NOT EXISTS xref ( sequence_hash TEXT , kegg_ontology TEXT , kegg_reaction TEXT , go_term TEXT,  kegg_mapp TEXT , sequence TEXT)")
		except sql.Error as e:
			logger.warn(e)
			raise




	def addrecord(self, record ):
		required = ['sequence']

		if not all(k in record for k in required):
			logger.warn("addrecord() requires: " + ', '.join(required))

		print(record)
		signature = hashlib.sha512(record['sequence']).hexdigest()

		print signature


	def __del__(self):
		self.sq3_con.close()



if __name__ == '__main__':
	logging.basicConfig()
	thisDatabase = magridDataBase("standard")
	thisrecord = {
				'sequence' : 'ATGCGHGHG',
				'kegg_ontology' : 'ko:8675309',
				'go_term' : 'go:GOTERM',
				'genus' : 'Salmonella',
				'species' : 'Salmonella enterica'
				}


#	this = ncbi.get_taxid_translator(ncbi.get_lineage(602))
	print 
	print	ncbi.get_descendant_taxa(602,collapse_subspecies=True)
	#print(this)
	
	