import os
import sys
import warnings

magic_dict = {
	'\x42\x5A\x68' 				: 'bz2',
	'\x50\x4B\x03\x04' 			: 'zip',
	'\x1f\x8b\x08'				: 'gzip'
	}

peek_length = max(len(x) for x in magic_dict)

"""
This module provides a minimal interface for checking compression on files
and opening for reading with the appropriate libraries as needed.

bzip and gzip have file operators.

As a result of zipfiles lack of a seek() function , so if you need it test for it :
	
	from openany import openany

	file = openany('file.zip')

	import zipfile 
	if isinstance(file, zipfile.ZipExtFile )

"""

def openany(path):
	path = os.path.abspath(path)
	
	if not (os.path.isfile(path)):
		sys.exit('{} : does not appear to exist'.format(path))
	elif not os.access(path, os.R_OK):
		sys.exit('{} : is not readable'.format(path))

	with open(path,'rb') as f:
		peek_magic = f.read(peek_length)
		f.close()


	for magic, filetype in magic_dict.items():
		if peek_magic.startswith(magic):
			if filetype == 'bz2' :
				import bz2

				try :
					file =  bz2.BZ2File(path)
				except Exception as e:
					sys.exit('{}'.format(e))
				return file

			elif filetype == 'zip':
				import zipfile
				archive = zipfile.ZipFile(path , 'r')
	
				try:
					file = archive.open(os.path.splitext(os.path.basename(path))[0])
				except Exception as e:
					sys.exit('{}'.format(e))
				return file
	
			elif filetype == 'gzip':
				import gzip

				try:
					file = gzip.GzipFile(path)
				except Exception as e:
					sys.exit('{}'.format(e))
				return file
	
	
	try:
		file = open(path , 'r')
	except Exception as e:
		sys.exit('{}'.format(e))
	
	return file
				
