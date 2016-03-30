"""Summary

NCBITaxonomy.py

A python module for downloading and processing a current version of the NCBI taxonomy providing methods 
for accessing taxonomic information from TaxID numbers

Attributes:
    logger (TYPE): logger for this module
    ncbibase (str): the base url for the ncbi's public FTP
    tax_target (str): the target file on ncbi's database
    taxonomy_dir (str): the directory where the file resides
    taxonomy_tar (str):	the actual tar file containing all of the downoad info
"""
import ftputil
import os
import sys
import sqlite3 as sql
import logging
import tarfile

logger = logging.getLogger(__name__)

tax_target  = '/pub/taxonomy/taxdump.tar.gz'
ncbibase 	 = 'ftp.ncbi.nih.gov'
taxonomy_dir = '/pub/taxonomy/'
taxonomy_tar = 'taxdump.tar.gz'

class ncbiTaxonomy(object):
	"""Summary
	Base class for this module
	"""
	def __init__(self, targetdir = None):
		"""Summary
		
		Args:
		    targetdir (TYPE, optional): Where should data be downloaded and stored
		"""
		self.downloaded_file = False


#		Setting our target directory


		if targetdir == None:
			self.target_dir = os.path.abspath(os.path.dirname(__file__))
		else:
			if not os.path.exists(targetdir):
				try :
					os.makedirs(targetdir)
				except OSError as e:
					logger.error("Couldn't create" , targetdir)
					logger.error(e)
					raise


		self.target_path = os.path.join(self.target_dir,taxonomy_tar)

#		Test the connection to ncbi

		try:
			self.ncbihost = ftputil.FTPHost(ncbibase,'anonymous', 'password' )		
		except FTPError as e:
			logger.warn(e)
			raise



#		Connect to our sqlite db , create table if it doesn't exist

		self.ncbi_sq3 = os.path.abspath(os.path.join(self.target_dir ,'NCBItaxonomy.sq3'))

			

		try:
			self.sq3_con	 = sql.connect(self.ncbi_sq3)
			self.sq3_cur 	 = self.sq3_con.cursor()
		except sql.Error as e:
			logger.warn(e)
			raise

		self.download()

		if self.downloaded_file == True or os.path.getsize(self.ncbi_sq3) == 0:
			logging.info("Building the database")
			self.build()


#		Get our column names

		self.sq3_columns = set()
		try :
			tmp = self.sq3_cur.execute('select * from ncbi')
			self.sq3_columns = [description[0] for description in tmp.description]
		except sqlite3.Error as e:
			logger.warn(e)
			raise

	def download(self):
		"""
		Proceedure to download data from the NCBI. Attempts to determine if the file 
		needs to be downloaded , also has minimal functionality for continuation.

		
		Returns:
		    TYPE: Null
		    Interacts with self.downloaded_file on success 

		"""
		source_size  = self.ncbihost.path.getsize(tax_target)
		source_mtime = self.ncbihost.stat(tax_target).st_mtime

		target_size  = None
		target_mtime = None

		if os.path.exists(self.target_path):
			target_size  = os.path.getsize(self.target_path)
			target_mtime = os.stat(self.target_path).st_mtime
		else:
			target_size = -1

		if source_size == target_size :
			logging.info("NCBI Taxonomy up to date.")
		elif target_size == -1 :
			logging.info("Starting download of NCBI Taxonomy data.")
			self.ncbihost.download(tax_target,self.target_path)
			self.downloaded_file = True 
		elif target_mtime > source_mtime:
			logging.info("Attempting to continue download.")
			with open (self.target_path , 'ab') as f:
				if (source_size == f.tell()):
					pass
				else:
					try:
						#If this ever gets supported by ftputil rewrite this try """
						import ftplib
						ftp = ftplib.FTP(ncbibase)
						ftp.login()
						ftp.cwd(taxonomy_dir)
						ftp.retrbinary('RETR %s' % taxonomy_tar , f.write , rest=f.tell())
					except (KeyboardInterrupt, SystemExit):
						raise
					except (ftplib.error_reply , ftplib.error_temp , ftplib.error_proto) as error:
						logger.error("Caught an error from ftplib , retry later if it persists raise issue through github!")
						raise
					except ftplib.error_perm as error:
						logger.error("Caught a serious error from ftplib, raise an issue now!")
						raise
					except :
						logger.error("Continuation download failed for some reason , restarting")
						os.unlink(self.target_path)
						self.ncbihost.download(self.source_path,self.target_path)			
			self.downloaded_file = True 		
		elif source_mtime < target_mtime:
			os.unlink(self.target_path)
			self.ncbihost.download(self.source_path,self.target_path)
			self.downloaded_file = True 
		else  :
			os.unlink(self.target_path)
			self.ncbihost.download(self.source_path,self.target_path)
			self.downloaded_file = True 
		

	def build(self):
		"""
		Proceedure that processes raw data into an SQLite database
		
		Returns:
			void
		"""
		try:
			self.sq3_cur.execute('DROP TABLE IF EXISTS ncbi')
		except sqlite3.Error as e:
			logger.warn(e)
			raise

		logger.info("Building NCBI Taxonomy Database")
		tar = tarfile.open(self.target_path)
		
		taxID2taxname = {}
		parent2child = {}
		name2node    = {}
		ranks 		 = set()

		logger.info("Loading scientific names")
		for l in tar.extractfile("names.dmp"):
			l = str(l.decode())
			fields = [ f.strip() for f in l.split("|")]
			taxID = fields[0]
			if fields[3].lower() == "scientific name":
				taxID2taxname[taxID] = fields[1]
		logger.info("Loaded %d scientific names", len(taxID2taxname))


		logger.info("Loading nodes")
		for l in tar.extractfile("nodes.dmp"):
			l 		= str(l.decode())
			fields  = [ f.strip() for f in l.split("|")]
			current = fields[0]
			parent  = fields[1]
			rank 	= fields[2]
			parent2child[current]=parent
			name2node[current]=rank
			ranks.add(rank)


		logger.info("Populating Table")
		insert = [s.replace(' ', '_') for s in ranks]
		insert = ["`"+ s + "` TEXT" for s in insert]
		create_table_text = "CREATE TABLE IF NOT EXISTS ncbi ( taxID INT PRIMARY KEY, taxonomy TEXT, rank TEXT, " + ", ".join(insert) + ")"
	
		try :
			self.sq3_cur.execute(create_table_text)
		except sqlite3.Error as e:
			logger.warn(e)
			raise			


#		Is there any reason we want to keep 'no rank' entries as starting points ? 

		for starting_node in taxID2taxname:
			current_node = starting_node
			taxonomy_string = []	
			insert_dict = {}
			if not name2node[current_node] == 'no rank':
				insert_dict[escaped_name('taxID')] = starting_node
				insert_dict[escaped_name('rank')] = name2node[current_node]
				while not taxID2taxname[current_node] == 'root':
					if not name2node[current_node] == 'no rank':
						insert_dict[escaped_name(name2node[current_node])] = cleaned_name(taxID2taxname[current_node])
						taxonomy_string.append(taxID2taxname[current_node])
					current_node = parent2child[current_node]

				taxonomy_string.reverse()
				insert_dict[escaped_name('taxonomy')]=cleaned_name(';'.join(taxonomy_string))
				insert = 'INSERT OR IGNORE INTO ncbi({}) VALUES ({})'.format(', '.join(insert_dict.keys()),', '.join('?' * len(insert_dict)))
				
				try:
					self.sq3_cur.execute(insert,insert_dict.values())
				except sqlite3.Error as e:
					logger.warn(e)
					raise
		try:
			self.sq3_con.commit()
		except sqlite3.Error as e:
			logger.warn(e)
			raise


	def get_rank(self, taxID):
		"""Summary
		
		Args:
		    taxID (int): NCBI Taxonomic ID 
		
		Returns:
		    string : the taxonomic rank of the Taxonomic ID (i.e. genus / species / sub-species etc.)
		"""
		text = 'SELECT `rank` FROM ncbi WHERE `taxID` = %s' % taxID
		
		try:
			self.sq3_cur.execute(text)
			taxID = self.sq3_cur.fetchone()
		except sqlite3.Error as e:
			logger.warn(e)
			raise

		return taxID[0].encode("ascii")

	def get_string(self , taxID):
		"""Summary
		
		Args:
		    taxID (int): NCBI Taxonomic ID
		
		Returns:
		    string: a semi colon delimited taxonomy for that Taxonomic ID (i.e Bacteria;something;something;genus;species)
		"""
		text = 'SELECT `taxonomy` FROM ncbi WHERE `taxID` = %s' % taxID
		
		try: 
			self.sq3_cur.execute(text)
			taxonomy = self.sq3_cur.fetchone()
		except sqlite3.Error as e:
			logger.warn(e)
			raise

		return taxonomy[0].encode("ascii")


	def get_taxa(self , taxID , level):
		"""Summary
		
		Args:
		    taxID (Int):  NCBI Taxonomic ID
		    level (string): What level from the taxonomic ID you wish . (i.e the Genus from NCBI Taxonomic ID 200)
		
		Returns:
		    string: The taxa from the requested level ( i.e. the genus from Salmonella enterica , would return Salmonella )
		"""
		if level in self.sq3_columns:
			try:
				text = 'SELECT `%s` FROM ncbi WHERE `taxID` = %s' % (level , taxID)
				self.sq3_cur.execute(text)
				taxonomy = self.sq3_cur.fetchone()
			except sqlite3.Error as e:
				logger.warn(e)
				raise

			return taxonomy[0].encode("ascii")			
		else :
			logger.warn("from ncbiTaxonomy.get_taxa(): level %s , doesn't exist" % level)
			return None


	def __del__(self):
		"""Summary
		Destructor method that explicitly commits and closes our connection
		
		Returns:
		    TYPE: Description
		"""
		try :
			self.sq3_con.commit()
			self.sq3_con.close()
		except sqlite3.Error as e:
			logger.warn(e)
			raise

def cleaned_name (string):
	"""
	Cleans text before insertion into sqlite table (double single ticks etc.)
	
	Args:
	    string (string): The string to work on
	
	Returns:
	    string : edited string 
	"""
	string = string.replace("'","''")
	return string

def escaped_name (string):
	"""
	properly escapes column names with back ticks
	
	Args:
	    string (string): column name
	
	Returns:
	    string: column name surrounded by back ticks
	"""
	return ("`"+string+"`").replace(' ','_')


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	taxonomy = ncbiTaxonomy()
	print taxonomy.get_rank(200)
	print taxonomy.get_string(200)
	print taxonomy.get_taxa(200 , 'genus')


