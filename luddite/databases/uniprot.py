import ftputil
import os
import sys
import warnings
import pprint




uniprotBaseURI  = 'ftp.uniprot.org'
uniprotCurrent  = '/pub/databases/uniprot/current_release/knowledgebase'
uniprotPrevious = '/pub/databases/uniprot/previous_releases'
uniprotLICENSE	= 'ftp://ftp.uniprot.org/pub/databases/uniprot/LICENSE'
uniprotTaxonomy = '/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions'

try:
	uniprothost = ftputil.FTPHost('ftp.uniprot.org','anonymous', 'password')
except FTPError as e:
	warnings.warn(e)
	sys.exit()



class uniprot:

	def __init__(self , targetdir = None , version = 'current' , taxonomy = 'complete' , knowledgebase = 'trembl' , dbtype = 'dat' , target_name = None):

		if targetdir == None :
			targetdir = os.getcwd()
		else:
			if not os.path.exists(targetdir):
				try :
					os.makedirs(self.targetdir)
				except OSError as e:
					warnings.warn("Couldn't create" , self.targetdir)
					sys.exit(e)

		self.targetdir = os.path.abspath(targetdir)

		if knowledgebase == 'trembl' or knowledgebase == 'sprot' :
			self.knowledgebase = knowledgebase
		else :
			sys.exit("knowledgebase must be set to tremble or sprot")


		if version != 'current':
			raise NotImplementedError, "I'm not dealing with this yet"
			releases = [string.encode('ascii') for string in uniprothost.listdir(uniprotPrevious)]
			if not version in releases:
				sys.exit("The version you requested doesn't exist")
		self.version = version

		
		if not dbtype in ['dat' , 'fasta' , 'xml']:
			sys.exit("dbtype must be one of the following types : dat , fasta, xml")
		self.dbtype = dbtype


		if taxonomy != 'complete':
			taxa = [string.encode('ascii') for string in uniprothost.listdir(uniprotTaxonomy)]
			if (any(taxonomy in t for t in taxa)):
				self.taxonomy = taxonomy
			self.dbtype = 'dat'
		else:
			self.taxonomy = taxonomy
		


		self.source_uri = self.set_source()
		self.target_uri = self.set_target()
		
		

		

	def set_source(self):
		uri = '' 
		file = ''
		if self.version == 'current':
			uri += uniprotCurrent
			
			if self.taxonomy == 'complete':
				uri += '/complete' 
				files = uniprothost.listdir(uri)				
				files = [f for f in files if self.dbtype in f]
				files = [f for f in files if self.knowledgebase in f]

			else :
				uri += '/taxonomic_divisions'
				files = uniprothost.listdir(uri)
				files = [f for f in files if self.taxonomy in f]
				files = [f for f in files if self.dbtype in f]
				files = [f for f in files if self.knowledgebase in f]

		else:
			raise NotImplementedError, "I'm not dealing with this yet"

		if len(files) > 1 :
			sys.exit("Couldn't whittle our list down to a single file")
		self.target_name = files[0]
		return uri + '/' + files[0]


	def set_target(self):		
		return self.targetdir + '/' + self.target_name


	def download(self):

		source_size = uniprothost.path.getsize(self.source_uri)
		
		if os.path.exists(self.target_uri):
			target_size = os.path.getsize(self.target_uri)
		else:
			target_size = -1

		if source_size == target_size :
			pass	
		elif target_size == -1 : 
			uniprothost.download(self.source_uri,self.target_uri)
		else :
			os.unlink(self.target_uri)
			uniprothost.download(self.source_uri,self.target_uri)

		# if source_size == target_size :
		# 	pass	
		# elif target_size > source_size: # this should NEVER happen
		# 	os.unlink(self.target_uri)
		# 	download(self)

		# elif target_size < source_size:
		# 	source_stat = uniprothost.stat(self.source_uri)
		# 	target_stat = os.stat(self.target_uri)
			
		# 	if (source_stat.st_mtime > target_stat.st_mtime):
		# 		unlink(self.target_uri)
		# 		download(self)
		# 	else:
		# 		with open(self.target_uri , 'ab') as f:
		# 			if target_size == f.tell():
		# 				pass
		# 			else:
		# 				try:
		# 					ftp.ret

			

#		uniprothost.download_if_newer()
		






if __name__ == '__main__':
	from pprint import pprint

	
	connect = uniprot(taxonomy="virus")
	connect.download()
	pprint (vars(connect))


	connect = uniprot()
	pprint (vars(connect))
