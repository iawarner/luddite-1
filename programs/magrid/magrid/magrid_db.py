import sys
import os
import logging
import hashlib
import sqlite3 as sql
import cPickle as pickle
import gzip
import itertools
import json


logger = logging.getLogger(__name__)

from config import MAGRID_DB_PATH
from luddite.parsers import dat


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
		self.sq3_connection.row_factory	= sql.Row
		self.sq3_cursor		= self.sq3_connection.cursor()
		self.sq3_cursor.execute("CREATE TABLE IF NOT EXISTS genes ( sequence_hash TEXT, genus TEXT, species TEXT, NCBItaxID INT, kegg_ontology TEXT , kegg_reaction TEXT , go_term TEXT,  kegg_map TEXT , sequence TEXT)")
		self.sq3_connection.commit()

#	Connect to the FASTA database
		self.fasta_connection = gzip.open(self.database_fasta_file,"ab")	



	def add_record( self, sequence_hash = None , kegg_ontology = None , kegg_map = None , kegg_reaction = None , go_term = None , sequence = None , NCBItaxID = None , immediate_commit = True , **kwargs):

		incoming_dict = {
			'sequence' 		: sequence,
			'kegg_ontology' : kegg_ontology,
			'kegg_reaction' : kegg_reaction,
			'kegg_map' 		: kegg_map,
			'go_term' 		: go_term,
			'NCBItaxID' 	: NCBItaxID
			}
	
		
		for k,v in incoming_dict.items():
			if isinstance(v,list):
				incoming_dict[k] = c_dump(v)


		required = ['sequence']
		one_of   = ['kegg_ontology','go_term']
		strongly_suggested = ['NCBItaxID']

		if sequence == None:
			logger.warn("add_record() requires sequence")
			return False

		if kegg_ontology == None and go_term == None:
			logger.warn("add_record() requires one of %s" % tuple(one_of))
			return False

		if NCBItaxID == None:
			logger.warn("Providing an NCBItaxID to add_record() is strongly suggested")

		incoming_dict['sequence_hash'] = hashlib.sha512(sequence).hexdigest()
		insert_dict = {i:j for i,j in incoming_dict.items() if j != []}
		insert = 'INSERT OR ABORT INTO genes({}) VALUES ({})'.format(', '.join(insert_dict.keys()),', '.join('?' * len(insert_dict)))
		
	# HOLY SHIT THIS WAS A TERRIBLE IDEA IN RETROSPECT - adding a completely seperate database reduction step 
# #		We've gotten all the information we're going to get at this point
# #		Let's see if we've gotten this hash before
# 		lookup_query = 'select * FROM genes where `sequence_hash` = \'%s\'' % incoming_dict['sequence_hash']

# 		self.sq3_cursor.execute(lookup_query)
# 		rows = self.sq3_cursor.fetchall()
# 		rows_selected = len(rows) 
# 		assert 0 <= rows_selected <= 1 
		
# 		if rows_selected == 0:
# 			#simple insert
# 			insert_dict = {i:j for i,j in incoming_dict.items() if j != []}
# 			insert = 'INSERT OR ABORT INTO genes({}) VALUES ({})'.format(', '.join(insert_dict.keys()),', '.join('?' * len(insert_dict)))

# 		if rows_selected == 1:
# 			selected_dict = dict(zip(rows[0].keys(),rows[0]))
# 			insert_dict = merge_insert_dicts(selected_dict,incoming_dict)
# 			delete_statement ='DELETE FROM genes WHERE `sequence_hash` = \'%s\' ' % incoming_dict['sequence_hash']
# 			self.sq3_cursor.execute(delete_statement)
# 			self.sq3_connection.commit()
# 			insert = 'INSERT OR ABORT INTO genes({}) VALUES ({})'.format(', '.join(insert_dict.keys()),', '.join('?' * len(insert_dict)))

			
		try:
			self.sq3_cursor.execute(insert,insert_dict.values())
		except sql.Error as e:
			logger.warn(e)
			raise
		if immediate_commit == True :
			self.sq3_connection.commit()


	def __del__(self):
		"""
		Destructor , explicit close
		
		Returns:
			void
		"""
		self.sq3_connection.commit()
		self.sq3_connection.close()
	
	def add_dat_file(self,file):
		from luddite.parsers import dat
		file = dat.file(file)
		#sequence_hash = None , kegg_ontology = None , kegg_mapp = None , kegg_reaction = None , go_term = None , sequence = None , NCBItaxID = None , immediate_commit = True
		for record in file.read():
			if not record == None:
				self.add_record( sequence = record['sequence'],
								 kegg_ontology = record['kegg_ontology'],
								 go_term = record['go_term'],
								 NCBItaxID = record['NCBItaxID'],
								 immediate_commit = False
									)


		self.sq3_connection.commit()

class compounds(object):
	"""base class for compounds"""
	def __init__(self, base_name = 'standard'):
		
		self.base_name = base_name

def merge_insert_dicts(dict1 , dict2):
	return_dict = {}
	keys = set()

	temporary_dict = dict1.copy()
	temporary_dict.update(dict2)
	dict2 = temporary_dict


	for k,v in dict1.items():
		try:
			dict1[k]=json.loads(v)
		except (TypeError, ValueError):
			dict1[k] = v
		if isinstance(dict1[k], unicode):
			dict1[k] = str(dict1[k])
		keys.add(k)

	for k,v in dict2.items():
		try: 
			dict2[k]=json.loads(v)
		except (TypeError, ValueError):
			dict2[k]=v
		if isinstance(dict2[k], unicode):
			dict2[k] = str(dict2[k])
		keys.add(k)


	for k in keys:
		if dict1[k] == [] and dict2[k] == []:
			return_dict[k]= None
		elif dict1[k] == []:
			return_dict[k] = dict2[k]
		elif dict2[k] == []:
			return_dict[k] = dict1[k]
		elif dict1[k] == dict2[k]:
			return_dict[k] = dict1[k]
		else:
			
			if isinstance(dict1[k],str):
				dict1[k] = [dict1[k]]
			if isinstance(dict2[k],str):
				dict2[k] = [dict2[k]]

			tmp_set = set()
			for t in dict1[k]:
				tmp_set.add(t)
			for t in dict2[k]:
				tmp_set.add(t)

			return_dict[k] = c_dump(list(tmp_set))
		
	return_dict = {i:j for i,j in return_dict.items() if j != None}
	return return_dict

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
	logging.basicConfig()
	database = genes()
	database.add_dat_file('/home/dstorey/Desktop/luddite/luddite/uniprot/uniprot_trembl_viruses.dat.gz')






