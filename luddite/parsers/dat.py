from __future__ import absolute_import
import re
import logging
logger = logging.getLogger(__name__)
print(__name__)



# DAT FILE Regex
# Build this up as we need it
IDregex=re.compile("ID.*\s+(\d+)\s+AA\.\n",re.MULTILINE|re.DOTALL) 
ACregex=re.compile("AC\s+(.*);\n",re.MULTILINE)
OSregex=re.compile("OS\s+(.*?)\.\n",re.MULTILINE|re.DOTALL)
OCregex=re.compile("OC\s+(.*?)\.\n",re.MULTILINE|re.DOTALL)

OXregex=re.compile("OX\s+NCBI_TaxID=(\d+).*;\n",re.MULTILINE|re.DOTALL)
OHregex=re.compile("OH\s+NCBI_TaxID=(\d+;.*?)\.\n",re.MULTILINE|re.DOTALL)

BioCycregex=re.compile("DR\s+BioCyc;(.*);.*\.\n")
GOregex=re.compile	("DR\s+GO;(.*)\.\n")
KEGGregex=re.compile	("DR\s+KEGG;(.*?)\.\n",re.MULTILINE|re.DOTALL)
KOregex=re.compile	("DR\s+ KO;(.*?)\.\n",re.MULTILINE|re.DOTALL)

SQregex=re.compile("SQ\s+SEQUENCE\s+\d+\s+AA;\s+\d+\s+MW;\s+(.*)\s+CRC64;\n([\t[A-Z|\s+]+\s*]*)",re.MULTILINE|re.DOTALL)

class DAT(object):
	"""Base class for parsing DAT files"""
	def __init__(self, filename):
		
		self.filename = filename
		self.file = openany(self.filename)


	def read (self):
		"""
		A dat file iterator , reads one record at a time
		
		Yields:
		    dict:
		"""

		buff = ''
		record_break = "//\n>"

		while True:
			while record_break in buff:
				position = buff.index(record_break)
				yield(parse(buff[:position]))
				buff = buff[position+len(record_break):]

			chunk = self.file.read(4096)
			if not chunk:
				yield parse(buff)
				break

			buff+=chunk


def parse(record):

	"""
	Get the ID line , and AA length for internal checking
	"""

	if not record:
		return None

	m=IDregex.search(record)
	AAlength = 0
	if m:
		AAlength = m.group(1)

	
	m=ACregex.search(record)
	accession = []
	if m:
		list_context=m.group(1).split(';')
		accession.append(list_context[0])


	species = []
	m = OSregex		.search(record)
	if m:
		list_context=m.group(1).split('(')
		if  "virus" in m.group(1):			
			species.append(list_context[0])
		else:
			list_context=list_context[0].split(' ')
			if len(list_context) > 2 :
				species.append(list_context[0] + ' ' + list_context[1])
			else : 
				species.append(list_context[0])
	

	m = OCregex.search(record)
	OCstring = []
	if m:
		tmpOCstring = m.group(0).translate(None,"OC")
		tmpOCstring = tmpOCstring.translate(None," ")
		OCstring.append(tmpOCstring.translate(None,"\n"))


	m = OXregex.search(record)
	ncbiTaxID = []
	if m:
		ncbiTaxID.append(m.group(1).translate(None," "))
	

	"""
	Host ranges on viruses to estimate content based on pathogens
	"""

	m = OHregex.findall(record)
	OH_ncbiTaxID = []
	OH_strings = []
	if m:
		for i in m:
			list_context = i.split(';')
			OH_ncbiTaxID.append(list_context[0].translate(None," "))	
			list_context = list_context[1].split('(')
			OH_strings.append(list_context[0].translate(None," "))


	BioCyc_ID = []
	BioCyc_ID = BioCycregex.findall(record)
	
	GO_codes = []
	m = GOregex.findall(record)
	if m:
		for i in m:
			list_context = i.split(';')
			GO_codes.append(list_context[0].translate(None," "))
	

	KEGG_IDs =[]
	m = KEGGregex.findall(record)
	if m :
		for i in m:
			list_context=i.split(';')
			KEGG_IDs.append(list_context[0].translate(None," "))
	

	KO_IDs = []
	m = KOregex.findall(record)
	if m:
		for i in m:
			list_context=i.split(';')
			KO_IDs.append(list_context[0].translate(None," "))

	crc64 = ''
	sequence = ''
	m = SQregex.search(record)
	if m:
		crc64 = m.group(1)
		sequence = m.group(2)
		sequence = sequence.translate(None," ")
		sequence = sequence.translate(None,"\n")
	
	"""
	We need to raise exceptions if we need to.
	"""

	if not accession:
		warn("No accession value!\n",record)
		return None

	
	if not OCstring:
		warn("No OC string defined!\n",record)
		return None

	if not ncbiTaxID:
		warn("No NCBI taxonomy ID defined!\n",record)
		return None

	if not sequence :
		warn("No sequence value!\n",record)
		return None

	
	return { 	'accession'	: accession , 
			  	'NCBI_TaxID': ncbiTaxID,
			  	'sequence' 	: sequence,			
			 	'BioCyc'	: BioCyc_ID,
			 	'GO_codes'	: GO_codes,
				'KEGG_IDs'	: KEGG_IDs,
				'KO_IDs'	: KO_IDs
				}

if __name__ == '__main__':
	print('yay')