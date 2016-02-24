import parasail






"""
parasail function naming conventions:



Pairwise Comparisons:

{ required }
[ optional ]

1) {nw , sg , sw}_ - (global , semi-global , local)
2) [stats_] - (do we want stats)
3) [{table,rowcol}_] - return DP table 
4) {striped , scan , diag , blocked }_- vectorized approach
5) {8,16,23,64,sat} - integer width of solution



results object:

Simple Measures
	.length			- alignment length
	.matches	  	- number of exact matches
	.saturated 		- did 8 bit solution overflow 
	.score 			- alignment score (bit score)
	.similar 		- number of similar matches

Table Measures
	.similar_table	- DP table of similar substitutions
	.score_table	- DP table of scores
	.matches_table	- DP table of exact matches 
	.length_table	- DP table of lengths ( ? )

Last Row / Column  of Named Table
	.similar_col
	.score_col
	.matches_col
	.length_col

	.similar_row
	.score_row
	.matches_row
	.length_row

General usage 

results = parasail.function(sequence , sequence , open penalty , gap penalty, matrix)	

matrix is one of :
parasail.blosum+[30,35,40,45,50,55,60,52,65,70,75,80,85,90,100]
parasail.pam+[10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400,410,420,430,440,450,460,470,480,490,500]


Profile Search Outline:

profile the query:

profile = parasail.Profile(query, parasail.blosum62, 'sat')

for reference in references:
	result = parasail.nw_striped_profile_sat(profile,reference,10,1)
	results.score 




"""





#This is working - lets define as a decorator ?

def simmilarity (protein1 , protein2 , alignment_class = 'nw' , stats = None , dp=None , vectorized = 'striped' ,  width = 'sat'):

	function_arguments = [alignment_class , stats, dp , vectorized , width]

	command = '_'.join(item for item in function_arguments if item)

	# for f in dir(parasail):
	# 	print '%s = %s' % (f , getattr(parasail,f))

	try :
		result = getattr(parasail, command )(protein1 , protein2 , 10 , 1 , parasail.blosum62)

	except AttributeError as e :
		
# function = parasail(command)
	
	for f in dir(result):
		print '%s = %s' % (f , getattr(result,f))		

#	results = parasail(protein1 , protein2 , 10 , 1 , parasail.blosum62).command


if __name__ == '__main__':
	simmilarity('this' , 'that')