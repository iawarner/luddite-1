import ftputil
import os
import sys
import sqlite3 as sql
import logging
import tarfile


logger = logging.getLogger(__name__)

source_file_path = '/pub/taxonomy/taxdump.tar.gz'
ncbi_server = 'ftp.ncbi.nih.gov'
source_file_dir = '/pub/taxonomy'
source_file_name = 'taxdump.tar.gz'
target_file_name = 'taxdump.tar.gz'


class ncbiTaxonomy(object):
	"""base class for ncbiTaxonomy"""
	def __init__(self, targetdir = os.path.abspath(os.path.dirname(__file__))):

		#Build target directory / associated variables
		self.targetdir = targetdir
		
		if not os.path.exists(self.targetdir):
			try :
				os.makedirs(self.targetdir)
			except OSError as e:
				logger.error("Couldn't create" , self.targetdir)
				logger.error(e)
				raise

		self.target_path = os.path.abspath(os.path.join(self.targetdir , target_file_name))		
		self.touch_file  = os.path.abspath(os.path.join(self.targetdir,'taxdmp.downloaded'))
		# Test connection to the NCBI
		try:
			self.ncbihost = ftputil.FTPHost(ncbi_server,'anonymous', 'password' )		
		except FTPError as e:
			logger.warn(e)
			raise

		# Initialize all file sizes and mtimes
			#When was the last time someone did something to the taxdmp file on the server
		self.source_size  = self.ncbihost.path.getsize(source_file_path)
		self.source_mtime = self.ncbihost.stat(source_file_path).st_mtime 

			#If a copy of the download file exists when was the last time was it touched
		
		if os.path.exists(self.target_path) :
			self.target_size = os.path.getsize(self.target_path)
			self.target_mtime = os.stat(self.target_path).st_mtime
		else :
			self.target_size = -1
			self.target_mtime = -1

			#If the touch file exists when was the last time it was touched
		
		if os.path.exists(self.touch_file):
			self.touch_size = os.path.getsize(self.touch_file)
			self.touch_mtime = os.stat(self.touch_file).st_mtime
		else:
			self.touch_size = -1
			self.touch_mtime = -1


		
		#logic for if we need to download the file
		self.recent_download = False

		if self.touch_mtime > self.source_mtime:
			#last download was newer than source so pass through
			pass
		elif self.source_mtime > self.target_mtime or self.source_mtime > self.touch_mtime:
			#source is newer , download
			self.download()
		elif self.source_size > self.target_size:
			self.continue_dl()
		else :
			#fall through is to just dowload the damn file
			download()

		#Database building 
		self.ncbi_sq3    = os.path.abspath(os.path.join(self.targetdir,'NCBItaxonomy.sq3'))
		
		if os.path.exists(self.ncbi_sq3):
			self.ncbi_sq3_mtime = os.stat(self.ncbi_sq3).st_mtime
		else:
			self.ncbi_sq3_mtime = -1


		if os.path.exists(self.ncbi_sq3):
			self.ncbi_sq3_mtime = os.stat(self.ncbi_sq3).st_mtime
			try:
				self.sq3_con	 = sql.connect(self.ncbi_sq3)
				self.sq3_cur 	 = self.sq3_con.cursor()
			except sql.Error as e:
				logger.warn(e)
				raise
		else:
			self.ncbi_sq3_mtime = -1


		#logic for if we need a fresh build (if recent download , then yes)
		if not os.path.exists(self.ncbi_sq3):
			self.build_database()
		elif self.recent_download:
			self.build_database()
		


		# Initialize our column names 
		self.sq3_columns = set()
		if os.path.exists(self.ncbi_sq3):
			self.sq3_columns = set_sq3_columns(self.ncbi_sq3)


	def download(self):
		logging.info("Starting full download")

		try:
			self.ncbihost.download(source_file_path , self.target_path)
		except: 
			raise
		else:
			self.target_size = os.path.getsize(self.target_path)
			self.target_mtime = os.stat(self.target_path).st_mtime
			if os.path.exists(self.touch_file):
				self.touch_mtime = os.utime(self.touch_file,None)
			else:
				f = open(self.touch_file, 'w')
				f.close()
		self.recent_download = True


	def continue_dl(self):
		logging.info("Continuing broken download")
		import ftplib

		try:
			ftp = ftplib.FTP(ncbi_server)
			ftp.login()
			ftp.cwd(source_file_dir)
			with open(self.target_path , 'ab') as f:
				ftp.retrbinary('RETR %s' % self.source_file_name , f.write,rest=f.tell())
		except (KeyboardInterrupt, SystemExit):
			raise
		except (ftplib.error_reply , ftplib.error_reply) as e:
			logger.error("An error occured during download")
			logger.error(e)
			raise
		except ftplib.error_perm as error:
			logger.error("A permanent error was raised by ftplib - please report this!")
			logger.error(e)
			raise
		else:
			self.target_size = os.path.getsize(self.target_path)
			self.target_mtime = os.stat(self.target_path).st_mtime

			if os.path.exists(self.touch_file):
				self.touch_mtime = os.utime(self.touch_file,None)
			else:
				f = open(self.touch_file , 'w')
				f.close()
		self.recent_download = True

	def build_database(self):
		
		logger.info("Building NCBI Taxonomy Database")

		try:
				self.sq3_con	 = sql.connect(self.ncbi_sq3)
				self.sq3_cur 	 = self.sq3_con.cursor()
		except sql.Error as e:
				logger.warn(e)
				raise

		try:
			self.sq3_cur.execute('DROP TABLE IF EXISTS ncbi')
		except sqlite3.Error as e:
			logger.warn(e)
			raise

		tar = tarfile.open(self.target_path)
		
		taxID2taxname = {}
		parent2child  = {}
		name2node     = {}
		ranks 		  = set()


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

		os.unlink(self.target_path)



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

		if taxID is None:
				return False
		else:
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
		
		if taxonomy is None:
			return False
		else:
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

			if taxonomy is None:
				return False
			else:
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


def set_sq3_columns(filename):
	internal_set = set()

	try :
		sq3_connection = sql.connect(filename)
		cursor = sq3_connection.cursor()
		tmp = cursor.execute('select * from ncbi')
		internal_set = [descriptions[0] for descriptions in tmp.description]
		sq3_connection.close()
	except sql.Error as e:
		logger.warn(e)
		raise

	return internal_set

if __name__ == '__main__':
	taxonomy = ncbiTaxonomy()
	print(taxonomy.get_string(600))