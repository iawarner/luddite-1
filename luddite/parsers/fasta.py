from openany import openany

class fasta (object):
	
	def __init__ ( self , path ):
		self.file = openany(path)
		self.path = path

	def __repr__(self):
		return '{}'.format(self.file)

	def read (self):
		buff = ''
		record_break = "\n>"

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





def parse(inc):
	[header,sequence] = inc.split("\n" , 1)
	if header[0] == '>':
		header=header[1:]
	sequence = sequence.replace('\n','')
	return {'header' : header , 'sequence' :sequence}





if __name__ == '__main__':
	fasta = fasta('VFDB_setA_nt.fas')

	for record in fasta.read():
		print '{}'.format(record)
	






