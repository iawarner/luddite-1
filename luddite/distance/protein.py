import parasail
import logging

"""
parasail function naming conventions:

general call format:

results = parasail.function(query , target , open penalty , gap penalty, matrix)	

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




def similarity (protein1 , protein2 , alignment_class = 'nw' , stats = 'stats' , dp=None , vectorized = 'striped' ,  width = 'sat' , gap = 10 , extension = 1):

	function_arguments = [alignment_class , stats, dp , vectorized , width]

	command = '_'.join(item for item in function_arguments if item)

	try :
		result = getattr(parasail, command )(protein1 , protein2 , gap , extension , parasail.blosum62)

	except AttributeError as e :
		print e		
	
	try : 
		simmilarity = float(result.similar) / result.length
	except ZeroDivisionError: 	
		simmilarity = 0

	return simmilarity

def identity (protein1 , protein2 , alignment_class = 'nw' , stats = 'stats' , dp=None , vectorized = 'striped' ,  width = 'sat' , gap = 10 , extension = 1):

	function_arguments = [alignment_class , stats, dp , vectorized , width]

	command = '_'.join(item for item in function_arguments if item)

	try :
		result = getattr(parasail, command )(protein1 , protein2 , gap , extension , parasail.blosum62)

	except AttributeError as e :
		print e		
	
	try : 
		identity = float(result.matches) / result.length
	except ZeroDivisionError: 	
		identity = 0

	return identity



def score(protein1 , protein2 , alignment_class = 'nw' , stats = 'stats' , dp=None , vectorized = 'striped' ,  width = 'sat' , gap = 10 , extension = 1):

	function_arguments = [alignment_class , stats, dp , vectorized , width]

	command = '_'.join(item for item in function_arguments if item)

	try :
		result = getattr(parasail, command )(protein1 , protein2 , gap , extension , parasail.blosum62)

	except AttributeError as e :
		print e		
	
	return result.score








if __name__ == '__main__':
	protein1 = "MPKIIEAIYENGVFKPLQKVDLKEGEKIRILLKKIDVEKFIMAKLPEEKIRELERRFEDENLY"
	protein2 = "MTRILTACKVVKTLKSGFGLANVTSKRQWDFSRPGIRLLSVKAQTAHIVLEDGTKMKGYSFGHPSSVAGEVVFNTGLGGYSEALTDPAYKGQILTMANPIIGNGGAPDTTARDELGLNKYMESDGIKVAGLLVLNYSHDYNHWLATKSLGQWLQEEKVPAIYGVDTRMLTKIIRDKGTMLGKIEFEGQSVDFVDPNKQNLIAEVSTKDVKVFGKGNPTKVVAVDCGIKNNVIRLLVKRGAEVHLVPWNHDFTQMDYDGLLIAGGPGNPALAQPLIQNVKKILESDRKEPLFGISTGNIITGLAAGAKSYKMSMANRGQNQPVLNITNRQAFITAQNHGYALDNTLPAGWKPLFVNVNDQTNEGIMHESKPFFAVQFHPEVSPGPTDTEYLFDSFFSLIKKGKGTTITSVLPKPALVASRVEVSKVLILGSGGLSIGQAGEFDYSGSQAVKAMKEENVKTVLMNPNIASVQTNEVGLKQADAVYFLPITPQFVTEVIKAERPDGLILGMGGQTALNCGVELFKRGVLKEYGVKVLGTSVESIMATEDRQLFSDKLNEINEKIAPSFAVESMEDALKAADTIGYPVMIRSAYALGGLGSGICPNKETLMDLGTKAFAMTNQILVERSVTGWKEIEYEVVRDADDNCVTVCNMENVDAMGVHTGDSVVVAPAQTLSNAEFQMLRRTSINVVRHLGIVGECNIQFALHPTSMEYCIIEVNARLSRSSALASKATGYPLAFIAAKIALGIPLPEIKNVVSGKTSACFEPSLDYMVTKIPRWDLDRFHGTSSRIGSSMKSVGEVMAIGRTFEESFQKALRMCHPSVDGFTPRLPMNKEWPANLDLRKELSEPSSTRIYAIAKALENNMSLDEIVKLTSIDKWFLYKMRDILNMDKTLKGLNSESVTEETLRQAKEIGFSDKQISKCLGLTEAQTRELRLKKNIHPWVKQIDTLAAEYPSVTNYLYVTYNGQEHDIKFDEHGIMVLGCGPYHIGSSVEFDWCAVSSIRTLRQLGKKTVVVNCNPETVSTDFDECDKLYFEELSLERILDIYHQEACNGCIISVGGQIPNNLAVPLYKNGVKIMGTSPLQIDRAEDRSIFSAVLDELKVAQAPWKAVNTLNEALEFANSVGYPCLLRPSYVLSGSAMNVVFSEDEMKRFLEEATRVSQEHPVVLTKFIEGAREVEMDAVGKEGRVISHAISEHVEDAGVHSGDATLMLPTQTISQGAIEKVKDATRKIAKAFAISGPFNVQFLVKGNDVLVIECNLRASRSFPFVSKTLGVDFIDVATKVMIGESVDEKHLPTLEQPIIPSDYVAIKAPMFSWPRLRDADPILRCEMASTGEVACFGEGIHTAFLKAMLSTGFKIPQKGILIGIQQSFRPRFLGVAEQLHNEGFKLFATEATSDWLNANNVPATPVAWPSQEGQNPSLSSIRKLIRDGSIDLVINLPNNNTKFVHDNYVIRRTAVDSGIALLTNFQVTKLFAEAVQKARTVDSKSLFHYRQYSAGKAA"


	print identity( protein1 , protein2)
	print similarity( protein1 , protein2)
	print score( protein1 , protein2)
	print score( protein2 , protein2)



