'''
validator v1.0

Version history:
v1.0 (17-May-2016) - Created by Ottoni Bastos.
v1.1 (20-Aug-2016) - Enhanced and validated by Gabriel Ramos.
'''

from py_expression_eval import Parser
import sys
import argparse

class Validator:

	def __init__(self):		
		self.__functions = {}
		self.__nodes = []
		self.__edges = []
	
	def __is_number(self, s):
	    try:
	        float(s)
	        return True
	    except ValueError:
	        return False

	def __check_function(self, a_list):

		list_of_terms = [] # terms = constants + variables
		list_of_variables = []
		buffer_string = ""

		if len(a_list) < 4:
			return "Function definition is incomplete or invalid!"
		elif len(a_list) > 4:# and a_list[4][0] != "#":
			return "Invalid character(s) after function's formula!"
		
		# get terms
		p = Parser()
		list_of_terms = p.parse(a_list[3]).variables()
	
		# check if variables were defined correctly
		if (a_list[2][0] != "(") or (a_list[2][len(a_list[2])-1] != ")"):
			return "Function's variables need to be defined between parentheses!"

		# get variables
		buffer_string = a_list[2].replace("(","")
		buffer_string = buffer_string.replace(")","")
		if len(buffer_string) > 0:
			list_of_variables = buffer_string.split(",")

			# check consistency of the variables
			for v in list_of_variables:
				if v not in list_of_terms:
					return "Variable '%s' is not part of the function!" % v

		# check if the function name is already in use
		if a_list[1] in self.__functions.keys():
			return "Function's name already declared!"
		else:
			self.__functions[a_list[1]] = [list_of_terms, list_of_variables] # to be used in the edge's checking function
		
		return ""

	def __check_node(self, a_list):
		
		if len(a_list) < 2:
			return "Node definition is incomplete or invalid!"
		elif len(a_list) > 2:
			return "Invalid character(s) after node's name!"
		else:
			if a_list[1] in self.__nodes:
				return "Node's name already declared!"
			else:
				self.__nodes.append(a_list[1])
		
		return ""

	def __check_edge(self, a_list):
		
		edge_name = []
		if '-' not in a_list[1]:
			return "Edge's name is not in the correct format!"
		else:
			edge_name = a_list[1].split("-")
			if (edge_name[0] != a_list[2]) or (edge_name[1] != a_list[3]):
				return "Edge's name does not correspond to the nodes it connects!"
		
		if a_list[1] in self.__edges:
			return "Edge's name already declared!"
		else:
			self.__edges.append(a_list[1])
		
		if (a_list[2] not in self.__nodes) or (a_list[3] not in self.__nodes):
			return "Nodes connected by the edge were not defined!"
		
		if a_list[4] not in self.__functions.keys():
			return "Edge's function was not defined!"
		
		expected_length = (5 + ( len(self.__functions[a_list[4]][0]) - len(self.__functions[a_list[4]][1]) ) )
		
		if len(a_list) < expected_length:
			return "Edge definition is incomplete or invalid!"
		elif len(a_list) > expected_length:
			return "Invalid character(s) after edges's constant(s)!"

		for e in a_list[5:]:
			if not self.__is_number(e):
				return "One or more constants are not numbers!"
		
		return ""

	def __check_od(self, a_list):

		od_name = []
		if '|' not in a_list[1]:
			return "OD pair's name is not in the correct format!"
		else:
			od_name = a_list[1].split("|")
			if (od_name[0] != a_list[2]) or (od_name[1] != a_list[3]):
				return "OD pair's name does not correspond to the specified origin and destination nodes!"
		
		if (a_list[2] not in self.__nodes) or (a_list[3] not in self.__nodes):
			return "Origin or destination nodes were not defined!"
		
		if len(a_list) < 5:
			return "OD pair's definition is incomplete or invalid!"
		elif len(a_list) > 5:
			return "Invalid character(s) after OD pair's total flow!"
		
		if not self.__is_number(a_list[4]):
			return "OD pair's total flow is not a number!"
		
		return ""



	def __validate_int(self, file_name):
		
		msg = ''
		lineid = 0
		
		state = 'function'
		
		for line in open(file_name, 'r'):
			
			lineid += 1
			
			# ignore \n
			line = line.rstrip()
			
			# ignore comments
			hash_pos = line.find('#')
			if hash_pos > -1:
				line = line[:hash_pos]
			
			taglist = line.split()
			
			if len(taglist) == 0:
				continue
				
			elif (taglist[0] == 'function'):	
				if state != 'function':
					msg = "Functions should be defined before nodes, edges and OD pairs!"
					break
				else:
					msg = self.__check_function(taglist)
					if msg:
						break

			elif (taglist[0] == 'node'):
				if state == 'function':
					state = 'node'
				elif state != 'node':
					msg = "Nodes should be defined after functions and before edges and OD pairs!"
					break
				msg = self.__check_node(taglist)
				if msg:
					break

			elif (taglist[0] == 'edge'):
				if state == 'node':
					state = 'edge'
				elif state != 'edge':
					msg = "Edges should be defined after functions and nodes and before OD pairs!"
					break
				msg = self.__check_edge(taglist)
				if msg:
					break

			elif (taglist[0] == 'od'):
				if state == 'edge':
					state = 'od'
				elif state != 'od':
					msg = "OD pairs should be defined after functions, nodes and edges!"
					break

				msg = self.__check_od(taglist)
				if msg:
					break

			else:
				msg = "Undefined type '%s'!" % taglist[0]
				break
			
		return msg, lineid
		
	def validate(self, file_name):
		msg, line = self.__validate_int(file_name)
		
		if not msg:
			sys.exit("The network file %s is correct!" % file_name)
		else:
			sys.exit("ERROR on line %d: %s" % (line, msg))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Validate a network file following the specification in http://wiki.inf.ufrgs.br/network_files_specification.', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('-f', dest='filename', required=True, type=str, help='name of the network file to be validated')
	args = parser.parse_args()

	validator = Validator()
	validator.validate(args.filename)
