#!/usr/bin/python


import argparse
import sys
sys.dont_write_bytecode = True
import os
import logging


# Setting this as early as possible

logger = logging.getLogger('magrid')
logger.propagate = False
logformat = logging.Formatter('%(asctime)s %(levelname)-2s %(message)s','%m-%d %H:%M')

import runEnviroment
import magrid_db





def set_default_subcommand(self,name,args=None):
	'''
	via:
		http://stackoverflow.com/a/26379693
	'''
	subparser_found = False

	for arg in sys.argv[1:]:
		if arg in ['-h', '--help']:  # global help if no subparser
			break
	else:
		for x in self._subparsers._actions:
			if not isinstance(x, argparse._SubParsersAction):
				continue
			for sp_name in x._name_parser_map.keys():
				if sp_name in sys.argv[1:]:
					subparser_found = True
		if not subparser_found:
			# insert default in first position, this implies no
			# global options without a sub_parsers specified
			if args is None:
				sys.argv.insert(1, name)
			else:
				args.insert(0, name)


def fullrun(options):
	logger.info("Starting a full run")
	


def default_db_install(options):
	logger.info("Downloading databases")
	

	for i in options.uniprot_taxonomy:
		for j in options.uniprot_knowledgebase:
			connect = uniprot.uniprot(taxonomy=i , knowledgebase = j , targetdir = runinfo.magrid_db_path)
			connect.download()

	logger.info("Building the database")





if __name__ == '__main__':

	
	""" 
	Build Global options using a pre parser
	via:
		http://stackoverflow.com/a/12167709

	"""

	argparse.ArgumentParser.set_default_subcommand = set_default_subcommand
	preparser = argparse.ArgumentParser(add_help=False)

	# ____ Add our shared arguments ___ #


	preparser.add_argument('--database',
								nargs   = '+',
								default = 'uniprot_tremble',
								help	= 'Which local database should I use for a search' 
								)

	preparser.add_argument('--outputdir',
							nargs 	= '+',
							default = 'magrid_output',
							help 	= 'Where should I record outputs'
							)

	preparser.add_argument('--verbose',
							action  = 'store_const',
							help 	= 'Verbose Outputs',
							dest 	= 'loglevel',
							const 	= logging.INFO,
							default = logging.WARNING
							)

	preparser.add_argument('--debug',
							action  = 'store_const',
							help 	= 'Verbose Outputs',
							dest 	= 'loglevel',
							const   = logging.DEBUG,
							default = logging.WARNING
							)


	preparser.add_argument('--version' , '-v', action='version' , version = runEnviroment.__version__)
	#___ Get them ___ #
	options , leftover = preparser.parse_known_args()


	#__ new parser object __#
	parser = argparse.ArgumentParser(parents = [ preparser ],
									 prog='magrid',
									 add_help= True,
									 description = "Meta genome restricted mass ID"
										)
	


	subparsers = parser.add_subparsers(title='actions' , 
									   description='valid subcommands',
									   )
	

	'''
	Default sub command object (executes a full run) 

	'''

	full = subparsers.add_parser('full',
								 	parents=[preparser]
									)
	full.set_defaults(runthis=fullrun)



	'''
	subcommand : install-uniprot

	Setup and Install the default Uniprot Database
	'''
	parser_db_setup = subparsers.add_parser( 'default_db_install' ,
												parents = [preparser]
											 	)

	parser_db_setup.add_argument('--uniprot_taxonomy' ,
								 nargs   = '+',
								 action  = 'append',
								 choices = ['complete' , 'archaea' , 'bacteria', 'fungi' , 'human' , 'invertebrates','mammals','plants','rodents','vertebrates','viruses'],
								 help	 = 'Which UniProt taxonomic group to grab from (default: complete)',
								 )

	parser_db_setup.add_argument('--uniprot_knowledgebase', 
								 nargs   ='+',
								 action  = 'append',
								 choices = ['sprot' ,'trembl'],
								 help	 = 'Which Uniprot knowledgebase to grab from (default : trembl)'
								 )


	parser_db_setup.set_defaults(runthis=default_db_install)
	





	# __ Kind of a hacky work around __ #
	parser.set_default_subcommand('full')
	

	options = parser.parse_args()
	
	runinfo=runEnviroment.runEnviroment(outdir = options.outputdir)

	#__ Set Logger stuffs __#
	logger.setLevel(options.loglevel)
	

	loghandle = logging.FileHandler(runinfo.log_file)
	loghandle.setLevel(logging.DEBUG)

	consoleHandler = logging.StreamHandler()
	consoleHandler.setLevel(options.loglevel)

	loghandle.setFormatter(logformat)
	consoleHandler.setFormatter(logformat)

	logger.addHandler(loghandle)
	logger.addHandler(consoleHandler)


	#___ Do the damn thing __#
	
	logger.info("RAWRRRRRRRRRRRRR")
	logger.info(vars(options))
	logger.info(vars(runinfo))
	
	if (hasattr(options,'runthis')):
		options.runthis(options)
	
