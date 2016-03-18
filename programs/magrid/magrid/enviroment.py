import sys
import os



__version__ = open('../VERSION').read().strip()


def check_enviroment():
	"""
	Enviromental checking before we start a run:
		Where do our databases reside? (default magrid_db)


	"""

	#__ Where do our databases exist __#
	abs_path 	   = os.path.abspath(os.path.dirname(__file__))
	magrid_db_path = os.path.join(abs_path,'magrid_db')

	magrid_db_path = os.getenv('MAGRID_DB', magrid_db_path)
	try:
		os.makedirs(magrid_db_path)
	except OSError as error:  
		if not os.path.isdir(magrid_db_path):
			raise