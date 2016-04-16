import sys
import re
from fileIO import fileIn, fileOut

class FlProc(object):

	def __init__(self, fullFile):
		
		self.fullFile = fullFile
		
		#remove multi-line comments
		newFile = self.fullFile
		comment = re.compile('/\*.*?\*/', re.DOTALL)
		newFile = self.stripPtrn(newFile, comment)
		
		#remove single line comments and white space
		comment = re.compile('//.*(\n|$)')
		newFile = self.stripPtrn(newFile, comment)
		self.noComments = newFile
		clnLines = re.split(r'\n', self.noComments)
		noBlanks = []
		clnFile = ''
		for i in clnLines:
			comment = re.compile('(^\s*|\s*$)')
			noSpace = self.stripPtrn(i, comment)
			if len(i) > 0:
				noBlanks.append(noSpace)
				clnFile = clnFile + noSpace

		#clean file as list by line
		self.clnLines = noBlanks
		
		#entire clean file as string
		self.clnFile = clnFile
		
	#split clean file list of tokens
	def tokenize(self):
		tokSplt = re.split(r'(\W)', self.clnFile)
		tokStr = ' '.join(tokSplt)
		tokSplt = re.split(r'\s', tokStr)
		tokens = []
		for i in tokSplt:
			if len(i) > 0:
				tokens.append(i)
		return tokens
		
	#strip out given 'string' from 'text'
	def stripPtrn(self, text, string):
		comCheck = string.search(text)
		if comCheck:
			newText = string.sub('', text)
			return newText
		else:
			return text
		
class Token(object):

	keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
	symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
	strConstant = re.compile('\|\"\w+\|\"')
	ident = re.compile('^[^0-9]\w*')

	spChar = {"<": "&lt;", ">": "&gt;", "\"": "&quot;", "&": "&amp;"}
	
	def __init__(self, token):
		self.token = token
	
	#return token type
	def tokenType(self):
		token = self.token
		if token in self.keywords:
			return 'keyword'
		elif token in self.symbols:
			return 'symbol'
		elif self.representsInt() == True:
			return 'integerConstant'
		elif self.strConstant.match(token):
			return 'stringConstant'
		elif self.ident.match(token):
			return 'identifier'

	#checks if value is int
	def representsInt(self):
	    try:
	        int(self.token)
	        return True
	    except ValueError:
	        return False

	#return xml formatted token type
	def xmlFrmt(self):
		if self.tokenType():
			text = self.tknOut()
			if text in Token.spChar:
				newTxt = Token.spChar[text]
			else:
				newTxt = text
			xmlStr = '<' + self.tokenType() + '> ' + newTxt + ' </' + self.tokenType() + '> '
			return xmlStr
		else:
			return 'NO MATCH'
			
	#return raw token (strips quotes from strings)
	def tknOut(self):
		if self.tokenType() == 'stringConstant':
			s = re.search('/w', 'self.token')
			return s.group(0)
		else:
			return self.token

"""fileNm = sys.argv[1]
#get full file text
fileTxt = fileIn(fileNm).fileText()
#create list of tokens from text string
tokens = FlProc(fileTxt).tokenize()

#create list of xml formatted tokens
tokArr = ['<tokens>']
for i in range(0, len(tokens)):
	xmlStr = Token(tokens[i]).xmlFrmt()
	tokArr.append(xmlStr)
tokArr.append('</tokens>')

fileOut(tokArr, fileNm, 'xml').write()"""