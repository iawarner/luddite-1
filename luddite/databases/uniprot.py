import ftputil
import os
import sys
import pprint
import logging

logger = logging.getLogger(__name__)

uniprotBaseURI  = 'ftp.uniprot.org'
uniprotCurrent  = '/pub/databases/uniprot/current_release/knowledgebase'
uniprotPrevious = '/pub/databases/uniprot/previous_releases'
uniprotLICENSE	= 'ftp://ftp.uniprot.org/pub/databases/uniprot/LICENSE'
uniprotTaxonomy = '/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions'





class uniprot:

	def __init__(self , targetdir = None , version = 'current' , taxonomy = 'complete' , knowledgebase = 'trembl' , dbtype = 'dat' , target_name = None):

		self.source_dir  = None
		self.target_file_name  = None
		self.source_file_name = None
		self.target_dir   = None
		self.uniprothost = None
		self.knowledgebase = None
		self.version = None
		self.dbtype = None
		self.taxonomy = None
		self.target_path = None
		self.source_path = None

		try:
			self.uniprothost = ftputil.FTPHost('ftp.uniprot.org','anonymous', 'password')
		except FTPError as e:
			logger.warn(e)
			raise

		if targetdir == None :
			targetdir = os.path.abspath(os.path.dirname(__file__))
		else:
			if not os.path.exists(targetdir):
				try :
					os.makedirs(targetdir)
				except OSError as e:
					logger.error("Couldn't create" , targetdir)
					logger.error(e)
					raise

		self.target_dir = os.path.abspath(targetdir)

		if knowledgebase == 'trembl' or knowledgebase == 'sprot' :
			self.knowledgebase = knowledgebase
		else :
			logger.error("knowledgebase must be set to tremble or sprot")
			sys.exit(-1)


		if version != 'current':
			raise NotImplementedError, "I'm not dealing with this yet"
			releases = [string.encode('ascii') for string in self.uniprothost.listdir(uniprotPrevious)]
			if not version in releases:
				logger.error("The version you requested doesn't exist")
				sys.exit(-1)
		self.version = version

		
		if not dbtype in ['dat' , 'fasta' , 'xml']:
			logger.error("dbtype must be one of the following types : dat , fasta, xml")
			sys.exit(-1)
		self.dbtype = dbtype


		if taxonomy != 'complete':
			taxa = [string.encode('ascii') for string in self.uniprothost.listdir(uniprotTaxonomy)]
			if (any(taxonomy in t for t in taxa)):
				self.taxonomy = taxonomy
			self.dbtype = 'dat'
		else:
			self.taxonomy = taxonomy
		

		

		self.source_path  = self.set_source()
		self.target_path  = self.set_target()
		
		




	def set_source(self):

		uri = '' 
		file = ''
		if self.version == 'current':
			uri += uniprotCurrent
			
			if self.taxonomy == 'complete':
				uri += '/complete' 
				files = self.uniprothost.listdir(uri)				
				files = [f for f in files if self.dbtype in f]
				files = [f for f in files if self.knowledgebase in f]

			else :
				uri += '/taxonomic_divisions'
				files = self.uniprothost.listdir(uri)
				files = [f for f in files if self.taxonomy in f]
				files = [f for f in files if self.dbtype in f]
				files = [f for f in files if self.knowledgebase in f]

		else:
			raise NotImplementedError, "I'm not dealing with this yet"

		if len(files) > 1 :
			raise TooManyTargets , "I was unable to get to one target"
		
		self.source_dir = uri
		self.source_file_name = files[0]
		self.target_file_name = files[0]

		return uri + '/' + files[0]


	def set_target(self):		
		return self.target_dir + '/' + self.target_file_name


	def download(self):

		
		source_size  = None
		target_size  = None
		source_mtime = None
		target_mtime = None


		source_size = self.uniprothost.path.getsize(self.source_path)
		source_mtime = self.uniprothost.stat(self.source_path).st_mtime
		
		if os.path.exists(self.target_path):
			target_size = os.path.getsize(self.target_path)
			target_mtime = os.stat(self.target_path).st_mtime
		else:
			target_size = -1


		if source_size == target_size :
			pass	
		elif target_size == -1 : 
			self.uniprothost.download(self.source_path,self.target_path)
		elif target_mtime > source_mtime:
			with open (self.target_path , 'ab') as f:
				if (source_size == f.tell()):
					pass
				else:
					try:
						""" If this ever gets supported by ftputil rewrite this try """
						import ftplib
						ftp = ftplib.FTP(uniprotBaseURI)
						ftp.login()
						ftp.cwd(self.source_dir)
						ftp.retrbinary('RETR %s' % self.target_file_name , f.write , rest=f.tell())
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
						self.uniprothost.download(self.source_path,self.target_path)			

		elif source_mtime < target_mtime:
			os.unlink(self.target_path)
			self.uniprothost.download(self.source_path,self.target_path)
		else  :
			os.unlink(self.target_path)
			self.uniprothost.download(self.source_path,self.target_path)


		

class TooManyTargets(Exception):
		def __init__(self,message,errors):
			super(TooManyTargets,self).__init__(message)
			self.errors = errors




if __name__ == '__main__':
	from pprint import pprint

	
	connect = uniprot(taxonomy="virus")
	connect.download()
	pprint (vars(connect))


	connect = uniprot()
	connect.download()
	pprint (vars(connect))
