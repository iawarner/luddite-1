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

	def __init__(self, targetdir = None):

		"""
		Setting our target directory
		"""

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
		"""
		Test the connection to ncbi
		"""
		try:
			self.ncbihost = ftputil.FTPHost(ncbibase,'anonymous', 'password' )		
		except FTPError as e:
			logger.warn(e)
			raise


		"""
		Connect to our sqlite db , create table if it doesn't exist
		"""
		self.ncbi_sq3 = os.path.abspath(os.path.join(self.target_dir ,'NCBItaxonomy.sq3'))

			

		try:
			self.sq3_con	 = sql.connect(self.ncbi_sq3)
			self.sq3_cur 	 = self.sq3_con.cursor()
		except sql.Error as e:
			logger.warn(e)
			raise


		if self.download() == True :
			logging.info("Building the database")
			self.build()


	def download(self):
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
		elif target_mtime > source_mtime:
			logging.info("Attempting to continue download.")
			with open (self.target_path , 'ab') as f:
				if (source_size == f.tell()):
					pass
				else:
					try:
						""" If this ever gets supported by ftputil rewrite this try """
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
					
		elif source_mtime < target_mtime:
			os.unlink(self.target_path)
			self.ncbihost.download(self.source_path,self.target_path)
			
		else  :
			os.unlink(self.target_path)
			self.ncbihost.download(self.source_path,self.target_path)
		
		return True
		

	def build(self):

		database_mtime = None
		download_mtime = os.stat(self.target_path).st_mtime

		if os.path.exists(self.ncbi_sq3):
			database_mtime = os.stat(self.ncbi_sq3).st_mtime
			if database_mtime < download_mtime:
				os.unlink(self.ncbi_sq3)
			else:
				logger.info("No need to update NCBI Taxonomy Database")
				return

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
	
		self.sq3_cur.execute(create_table_text)
		

		"""
		Is there any reason we want to keep 'no rank' entries as starting points ? 
		"""

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
				self.sq3_cur.execute(insert,insert_dict.values())

		self.sq3_con.commit()

	def __del__(self):
		self.sq3_con.commit()
		self.sq3_con.close()



def blank_insert_statement(taxID):
	text = "INSERT INTO ncbi (%s) VALUES (%s)" % (escaped_name('taxID') , taxID)
	logging.debug(text)
	return text

def update_statement(taxID , rank , name):
	text = "UPDATE ncbi SET %s = '%s' WHERE `taxID` = %s" % (escaped_name(rank) , cleaned_name(name) , taxID)
	logging.debug(text)
	return text

def cleaned_name (string):
	string = string.replace("'","''")
#	string = string.replace(".","\\.")
	return string

def escaped_name (string):
	return ("`"+string+"`").replace(' ','_')

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	taxonomy = ncbiTaxonomy()
	
