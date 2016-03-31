import sys
import os
import logging
import hashlib
import sqlite3 as sql
import cPickle as pickle
import gzip


logger = logging.getLogger(__name__)

from config import MAGRID_DB_PATH



class genes(object):
	"""base class for genes database"""
	def __init__(self, base_name = 'standard' , nrlevel = 100 , taxonomic_level = -1):

		self.base_name = base_name
		self.gene_database_path = os.path.abspath(os.path.join(MAGRID_DB_PATH,base_name))

#	Set all of our paths

		self.database_config_file = os.path.abspath(os.path.join(self.gene_database_path,base_name + '.config'))
		self.database_sqlite_file = os.path.abspath(os.path.join(self.gene_database_path,base_name + '.sq3'))
		self.database_fasta_file  = os.path.abspath(os.path.join(self.gene_database_path,base_name + '.fasta.gz'))
		self.database_dmnd_file   = os.path.abspath(os.path.join(self.gene_database_path,base_name + '.dmnd'))

#	Connect to the database , load from the config file 
		
		try :
			os.makedirs(self.gene_database_path)
		except OSError as error:
			if not os.path.isdir(self.gene_database_path):
				logger.warn('%s exists already and not a directory!' % self.gene_database_path)
				raise

#	Attempt to load our config information , if we can't - set it and dump it 	
		if os.path.exists(self.database_config_file):
			self.database_config = pickle.load(open(self.database_config_file , "rb"))
		else :
			self.database_config = {
									'base_name' 	  : base_name,
									'nrlevel'   	  : nrlevel,
									'taxonomic_level' : taxonomic_level
									}
			pickle.dump(self.database_config , open(self.database_config_file,"wb"))

#	Connect to our cross reference database , create table if it doesn't exist
		self.sq3_connection = sql.connect(self.database_sqlite_file)
		self.sq3_cursor		= self.sq3_connection.cursor()
		self.sq3_cursor.execute("CREATE TABLE IF NOT EXISTS xref ( sequence_hash TEXT , genus TEXT, species TEXT, NCBItaxID INT, kegg_ontology TEXT , kegg_reaction TEXT , go_term TEXT,  kegg_mapp TEXT , sequence TEXT)")
		self.sq3_connection.commit()

#	Connect to the FASTA database
		self.fasta_connection = gzip.open(self.database_fasta_file,"ab")	


	def __del__(self):
		"""
		Destructor , explicit close
		
		Returns:
			void
		"""
		self.sq3_connection.close()
	


class compounds(object):
	"""base class for compounds"""
	def __init__(self, base_name = 'standard'):
		
		self.base_name = base_name



def c_dump(x):
	"""
	creates a compact json dump
	
	Args:
	    x (): any python data structure
	
	Returns:
	    string: compact json dump of  data structure
	"""
	return json.dumps(x, separators=(',',':'))

if __name__ == '__main__':
	database = genes()