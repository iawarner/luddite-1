#!/usr/bin/python
import argparse
import sys

from luddite.databases import uniprot



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


def fullrun():
	print"Full Run"

def dbsetup():
	print "setup the db"




if __name__ == '__main__':

	
	""" 
	Build Global options using a pre parser
	via:
		http://stackoverflow.com/a/12167709

	"""

	argparse.ArgumentParser.set_default_subcommand = set_default_subcommand
	preparser = argparse.ArgumentParser(add_help=False)

	# ____ Add our shared arguments ___ #
	preparser.add_argument('--version' , action='version' , version = '0.1b')


	preparser.add_argument('--uniprot_taxonomy' ,
								 nargs   = '*',
								 action  = 'append',
								 help	=' A list of taxonomic sub-units to grab from UniProt',
								 )

	preparser.add_argument('--uniprot_knowledgebase' , 
								 nargs   ='*',
								 action  = 'append',
								 help	= 'Which UniProt knowledgebase to grab from'
								 )

	#___ Get them ___ #
	options , leftover = preparser.parse_known_args()



	#__ new parser object __#
	parser = argparse.ArgumentParser(parents = [ preparser ],
									 prog='MGRMID',
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
	subcommand : dbsetup

	Setup and Install the default Uniprot Database
	'''
	parser_db_setup = subparsers.add_parser( 'dbsetup' ,
												parents = [preparser]
											 	)

	parser_db_setup.set_defaults(runthis=dbsetup)
	


	
	'''
	DB Install
	'''


	# __ Kind of a hacky work around __ #
	parser.set_default_subcommand('full')
	options = parser.parse_args()


	#___ Do the damn thing __#
	print options

	if (hasattr(options,'runthis')):
		options.runthis()
	
