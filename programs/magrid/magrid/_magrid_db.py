"""Summary

Attributes:
    logger (TYPE): Description
    ncbi (TYPE): Description
"""
import sys
import os
import logging
import hashlib
import sqlite3 as sql



from luddite import uniprot
from luddite.ncbi import taxonomy
from config import MAGRID_DB_PATH




logger = logging.getLogger(__name__)
taxonomy = taxonomy.ncbiTaxonomy()






class magrid_genesDB (object):
	"""
	A base class for the magridDatabase
	"""
	def __init__(self , name):
		"""Summary

		Args:
		    name (str): name of the database
		"""
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




	def addrecord(self, sequence_hash = None , kegg_ontology = None , kegg_mapp = None , kegg_reaction = None , go_term = None , sequence = None ):
		"""Summary
		
		Add a record to the database

		Args:
		    sequence_hash (str, optional): Description
		    kegg_ontology (str, optional): Description
		    kegg_mapp (str, optional): Description
		    kegg_reaction (str, optional): Description
		    go_term (str, optional): Description
		    sequence (str, required): Description
		
		Returns:
		    void: 
		"""
		required = ['sequence']

		if not all(k in record for k in required):
			logger.warn("addrecord() requires: " + ', '.join(required))


		print(record)
		signature = hashlib.sha512(sequence).hexdigest()

		self.sq3_con.commit()
		print signature


	def __del__(self):
		"""Summary
		Class destructor , on any exit attempts to commit then exits.
		Returns:
		    void:
		"""
		self.sq3_con.commit()
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


	
	