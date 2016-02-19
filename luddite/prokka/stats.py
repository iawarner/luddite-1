import warnings
import argparse
import os

class stats:
    """A simple class for storing prokka output statistics"""
    def __init__(self , file = None):
        self.stats = {
            'contigs': 0 ,
            'bases': 0 ,
            'tmRNA': 0 ,
            'misc_RNA': 0 ,
            'tRNA': 0 ,
            'CDS': 0 ,
            'gene': 0 ,
            'repeat_region': 0 ,
            'rRNA': 0 
            }
        self.file = None
        self.basename = None

        if not file == None:
        	self.set_stats(file)


    def set_stats(self, file = None):
        if file == None:
            warning.warn('No file provided to set_stats')
            return

        if os.path.exists(file) :
            self.file = file
            self.basename = os.path.splitext(os.path.basename(self.file))[0]
        else :
            warning.warn(file + ' does not exist')
            return

        with open(self.file) as f:
            for line in f : 
                line = line.strip("\n\r")
                information = line.split(': ')
                if information[0] in self.stats:
                    self.stats[information[0]] = information[1]

    
    def get_stats(self):
        return self.stats
    
    def get_name(self):
        return self.basename
    
    def get_fp(self):
        return self.file


def print_table(ProkkaObjects = None):
    if ProkkaObjects == None:
        warning.warn("No objects provided to create table")

    headers = ['contigs','bases' ,'tmRNA','misc_RNA','tRNA','CDS','gene','repeat_region','rRNA']

    print "file, " + ", ".join( headers)    

    for o in ProkkaObjects:
        stats = o.get_stats()
        line = []
        line.append(o.get_name())
        for k in headers:
            line.append(stats[k])
        print ", ".join(str(i) for i in line) 





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Getting and handling statsitics from Prokka')
    parser.add_argument('files' , metavar='prokkaStatsFile',  nargs="+" , help='A file name to process')
    parser.add_argument('--table' , action='store_const' , const = 1 , help='Output a table')
    parser.add_argument('--graph' , action='store_const' , const = 1 , help='Output graphs')

    args = parser.parse_args()



    ProkkaStatsObjects = []
    for f in args.files:
        tmpObject = stats(f)
        ProkkaStatsObjects.append(tmpObject)


    if args.table == 1 :
        print_table(ProkkaStatsObjects)

#    if args.graph == 1 :
        #make_graph(ProkkaStatsObjects)



