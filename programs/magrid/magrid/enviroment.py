import sys
import os
import cPickle as pickle
import logging


logger = logging.getLogger(__name__)

__version__ = open('../VERSION').read().strip()


class RunEnviroment(object):

	def __init__ (self , outdir = None):

		if outdir == None:
			logging.error("RunEnviroment requires an outdir")
			sys.exit(200)
	
		self.outdir = outdir 
		self.persistance_file = os.path.join(self.outdir , 'run.info')
		self.log_file = os.path.join(self.outdir,'run.log')

		try:
			os.makedirs(self.outdir)
		except OSError as error:  
			if not os.path.isdir(self.outdir):
				raise

		if os.path.exists( self.persistance_file ):
			self.load()

		if hasattr(self, 'version'):
			if self.version != __version__:
				logging.warn("You appear to have updated magrid between analyses , It's suggested to restart the run")
		else:
			self.set_version()


		if hasattr(self,'magrid_db_path'):
			if os.path.exists(self.magrid_db_path):
				pass
			else:
				logging.error("Previous magrid_db_path path doesn't appear to exist, exiting")
				sys.exit(-1)
		else:
			self.set_magrid_db_path()


		if hasattr(self,'database'):
			if os.path.exists(os.path.join(self.set_magrid_db_path,self.database)):
				pass
			else:
				logging.error("Previously searched database doesn't appear to exist , exiting")
				sys.exit(-1)


		self.save()




	def set_database(self,database):
		'''
		What database did we search against.
		'''
		if os.path.exists(os.path.join(self.set_magrid_db_path,database)):
			self.database = database
		else :
			logging.error('The database %s doesn\'t exist, exiting' , self.database)
		self.save()


	def set_magrid_db_path(self):
		'''
		magrid_db_path :
			can only be set once
			defaults to a directory in the bin can be overridden with the system variable $MAGRID_DB

		'''
		if hasattr(self , 'magrid_db_path'):
			logging.warn("magrid_db_path has already been set , not resetting")
			return

		abs_path 	   = os.path.abspath(os.path.dirname(__file__))
		magrid_db_path = os.path.join(abs_path,'magrid_db')
		magrid_db_path = os.getenv('MAGRID_DB', magrid_db_path)
		
		try:
			os.makedirs(magrid_db_path)
		except OSError as error:  
			if not os.path.isdir(magrid_db_path):
				raise
		self.magrid_db_path = magrid_db_path 
		self.save()

	def set_version(self):
		if hasattr(self,'version'):
			logging.warn('version has already been set , not resetting')
			return
		self.version = __version__
		self.save()

	def load(self):
		'''
		Loading our persistance object from disk
		'''
		logging.info('Loading persistance file from : %s' , self.persistance_file)
		file = open(self.persistance_file, 'rb')
		persistance_dict = pickle.load(file)
		file.close()
		self.__dict__.update(persistance_dict)


	def save(self):
		'''
		Saving our object to disk
		'''
		logging.info('Dumping persistance file to disk : %s' , self.persistance_file)
		file = open(self.persistance_file,'wb')
		pickle.dump(self.__dict__,file,2)
		file.close()












def check_enviroment():
	"""
	Enviromental checking before we start a run:
		Where do our databases reside? (default magrid_db)


	"""




if __name__ == '__main__':
	runinfo = RunEnviroment(outdir = 'magrid_out')
	runinfo.load()
	print(vars(runinfo))
	runinfo.save()
