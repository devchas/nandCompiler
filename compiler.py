import sys
import re
from fileIO import fileIn, fileOut
from tokenizer import FlProc, Token
from symTbl import Table


class Compiler(object):

	classVarDec = ['static', 'field']
	varType = ['int', 'char', 'boolean']
	subroutineDec = ['constructor', 'function', 'method']
	statements = ['let', 'if', 'while', 'do', 'return']
	ops = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
	urnaryOps = ['-', '~']
	keyConsts = ['true', 'false', 'null', 'this']
	
	def __init__(self, file):
		self.file = file
		fileTxt = fileIn(self.file).fileText()
		self.tokens = FlProc(fileTxt).tokenize()
		self.t = []
		self.vm = []
		self.tokCnt = 0
		self.nextCnt = self.tokCnt + 1
		self.curTok = Token(self.tokens[self.tokCnt])
		self.nextTok = Token(self.tokens[self.nextCnt])
		self.curOut = self.curTok.tknOut()
		self.nextOut = self.nextTok.tknOut()
		self.curType = self.curTok.tokenType()
		self.nextType = self.nextTok.tokenType()
		self.subTbl = None
		self.exprCnt = 0
		self.wLoop = 0
		self.wEnd = 0
		self.ifYes = 0
		self.ifNo = 0
		
	# append text
	def appTxt(self, text, adv=0):
		#print(text)
		self.t.append(text)
		self.addAdv(adv)
		return

	# append text for each token until token == string then addAdv 'adv' times
	def appUntil(self, string, adv=0):
		while (self.curOut != string):
			self.addAdv()
		self.addAdv(adv)
		return

	# advance to next token and update all relevant variables
	def advance(self):
		if (self.tokCnt + 1) < len(self.tokens):
			self.tokCnt += 1
			self.nextCnt = self.tokCnt + 1
			self.curTok = Token(self.tokens[self.tokCnt])
			self.curOut = self.curTok.tknOut()
			self.curType = self.curTok.tokenType()
			if self.nextCnt < len(self.tokens):
				self.nextTok = Token(self.tokens[self.nextCnt])
				self.nextOut = self.nextTok.tknOut()
				self.nextType = self.nextTok.tokenType()
		return

	# add xml format and advance
	def addAdv(self, num=1):
		if num > 0:
			for _ in range(num):
				self.appTxt(self.curTok.xmlFrmt())
				self.advance()
		return
		
	# starts compilation process
	def constructor(self):
		if self.curOut == 'class':
			self.compileClass()
		return
			
	# append tokens until token = '{' (inclusive), compile any vars or subroutines
	def compileClass(self):
		self.tbl = Table()
		self.appTxt('<class>')
		self.clName = self.nextOut
		self.appUntil('{', 1)
		self.compileClassVarDec()
		self.compileSubroutine()
		self.appUntil('}', 1)
		self.appTxt('</class>')
		self.makeFile()
		print(self.tbl.hash)
		return
		
	# for each set of var declarations, add xml tags
	def compileClassVarDec(self):
		if self.curOut in Compiler.classVarDec:
			self.appTxt('<classVarDec>')
			self.addSymbolsToTable(self.getKindType(), self.tbl)
			self.addAdv()	# passes over semi-colon at end of var declaration
			self.appTxt('</classVarDec>')
			self.compileClassVarDec()
		return

	# gets the kind and type for at least one symbol of the same type (list separated by commas)
	def getKindType(self):
		tFields = []
		for i in range(0, 2):
			tFields.append(self.curOut)
			self.addAdv()
		return tFields

	# adds a new line to current symbol table if multiple of same kind as designated by comma
	def addSymbolsToTable(self, fields, table):
		tFields = [fields[0], fields[1], self.curOut]
		table.appSymbol(tFields)
		self.addAdv()
		if self.curOut == ',':
			self.addAdv()
			self.addSymbolsToTable(fields, table)
		return

	def compileSubroutine(self):
		if self.curOut in Compiler.subroutineDec:
			self.appTxt('<subroutineDec>')
			self.subTbl = Table()
			fncInfo = self.getFncInfo()
			self.appUntil('(', 1)
			self.appTxt('<parameterList>')
			args = self.compileParameterList()
			self.appTxt('</parameterList>', 1)	#	closing paren
			self.writeFnc(fncInfo, args)
			self.compileSubBody()
			self.appTxt('</subroutineDec>')
			print(self.subTbl.hash)
			self.compileSubroutine()
		return

	def writeFnc(self, info, args):
		if info['kind'] == 'method':
			args += 1
		fnc = 'function ' + self.clName + '.' + info['name'] + ' ' + str(args)
		self.vm.append(fnc)
		# sets pointer reference based on 'hidden' first argument for methods
		if info['kind'] == 'method':
			self.vm.append('push argument 0')
			self.vm.append('pop pointer 0')
		# constructor - calls memory.alloc method (1 argument for size); set pointer address
		elif info['kind'] == 'constructor':
			self.vm.append('push constant ' + str(self.calcFieldVars()))
			self.vm.append('call Memory.alloc 1')
			self.vm.append('pop pointer 0')
		return

	# returns dict of fnc kind, type and name
	def getFncInfo(self):
		fncInfo = {}
		fncInfo['kind'] = self.curOut
		self.addAdv()
		fncInfo['type'] = self.curOut
		fncInfo['name'] = self.nextOut
		return fncInfo

	def compileParameterList(self, paramCnt=0):
		params = paramCnt
		if self.curOut != ')':
			params += 1
			pFields = []
			for i in range(0, 2):
				pFields.append(self.curOut)
				self.addAdv()
			pFields = ['argument', pFields[0], pFields[1]]
			self.subTbl.appSymbol(pFields)
			if self.curOut == ',':
				self.addAdv()
			params = self.compileParameterList(params)
		return params

	def compileSubBody(self):
		self.appTxt('<subroutineBody>', 1)	#	open curly brace
		self.compileVarDec()
		self.appTxt('<statements>')
		self.compileStatements()
		self.appTxt('</statements>', 1)
		self.appTxt('</subroutineBody>')
		return

	def compileVarDec(self):
		if self.curOut == 'var':
			self.appTxt('<varDec>')
			self.addSymbolsToTable(self.getKindType(), self.subTbl)
			self.addAdv()
			self.appTxt('</varDec>')
			self.compileVarDec()
		return

	def compileStatements(self):
		if self.curOut in Compiler.statements:
			if self.curOut == 'do':
				self.compileDo()
			elif self.curOut == 'let':
				 self.compileLet()
			elif self.curOut == 'return':
				self.compileReturn()
			elif self.curOut == 'while':
				self.compileWhile()
			elif self.curOut == 'if':
				self.compileIf()
			self.compileStatements()
		return


	def compileDo(self):
		self.appTxt('<doStatement>')
		# advances over 'do' keyword
		self.addAdv()
		# creates function call; if method, "class." elif function "thisClass."
		if self.addClassToFncCall() == False:
			self.fncCall = 'call ' + self.clName + '.' + self.curOut
			# if function, advance over fnc name and open paren
			self.addAdv(2)
		else:
			# if method, advances over "."
			self.addAdv()
			# adds method name
			self.addMethodToFncCall()
			# advances over method name and open paren
			self.addAdv(2)
		self.compileExpressionList()
		self.callFnc()
		self.appUntil(';', 1)
		# pops and disregards output if called function
		self.vm.append('pop temp 0')
		self.appTxt('</doStatement>')
		return

	def compileLet(self):
		arrIndex = None
		self.appTxt('<letStatement>')
		self.addAdv()	#	let statement
		# tuple of (0) kind, (1) index
		varFields = self.getVarFields(self.curOut)
		self.addAdv()	#	var name
		# advances over open bracket and compiles expression upon reaching array item
		if self.curOut == '[':
			self.addAdv()
			arrIndex = self.getVarFields(self.curOut)
			# self.compileExpression()
		# appUntil should still work with array var because needs to advance over closed bracket
		self.appUntil('=', 1)
		# clear value of pop expression (not sure this is necessary)
		self.fncCall = None

		self.compileExpression()

		self.callFnc()
		
		# end assignment pop
		# array pop
		if arrIndex:
			thatRef = varFields[1] + arrIndex[1]
			self.vm.append('pop that ' + str(thatRef))
		# ordinary pop
		else:
			popStmnt = 'pop ' +  varFields[0] + ' ' + str(varFields[1])
			self.vm.append(popStmnt)
		
		self.appTxt('</letStatement>')
		return

	def compileReturn(self):
		self.appTxt('<returnStatement>', 1)
		if self.curOut != ';':
			self.compileExpression()
		else:
			self.vm.append('push constant 0')
			self.addAdv()
		self.appTxt('</returnStatement>')	
		return

	def compileWhile(self):
		self.appTxt('<whileStatement>')

		thiswLoop = self.wLoop
		self.vm.append('label wLoop' + str(thiswLoop))
		self.wLoop += 1

		self.appUntil('(', 1)
		self.compileExpression()
		
		thiswEnd = self.wEnd
		self.vm.append('if-goto wEnd' + str(thiswEnd))
		self.wEnd += 1
		self.newStatement()
		
		self.addAdv()
		self.vm.append('goto wLoop' + str(thiswLoop))
		self.appTxt('</whileStatement>')
		self.vm.append('label wEnd' + str(thiswEnd))
		return

	def compileIf(self):
		self.appTxt('<ifStatement>')
		self.appUntil('(', 1)
		self.compileExpression()

		thisIfYes = self.ifYes
		self.vm.append('if-goto ifYes' + str(thisIfYes))
		self.ifYes += 1

		thisIfNo = self.ifNo
		self.vm.append('goto ifNo' + str(thisIfNo))
		self.ifNo += 1

		self.vm.append('label ifYes' + str(thisIfYes))

		self.newStatement()
		self.addAdv()	# advances over closed curly brace
		self.vm.append('label ifNo' + str(thisIfNo))
		if self.curOut == 'else':
			self.addAdv()
			self.newStatement()
			self.addAdv()	# advances over closed curly brace
		self.appTxt('</ifStatement>')
		return

	def newStatement(self):
		if self.curOut == '{':
			self.addAdv()
			self.appTxt('<statements>')
			self.compileStatements()
			self.appTxt('</statements>')
		return
		
	def compileExpression(self):
		self.appTxt('<expression>')
		self.compileTerm()
		self.appTxt('</expression>')
		# advance and new expression upon reaching comma
		if self.curOut == ',':
			self.exprCnt += 1
			self.addAdv()
			self.compileExpression()
		# advances over closed bracket (end of array item)
		elif self.curOut == ']':
			self.addAdv()
		# advances 1 step upon reaching semi-colon (end expression)
		elif self.nextOut != ';':
			self.addAdv()
		return
		
	def compileTerm(self, oper=None):
		runOper = True
		# stops compiling terms upon reaching the following symbols
		if self.curOut not in [')', ';', ',', ']']:
			# operator advance (not a term)
			if self.curOut in Compiler.ops:
				oper = self.curOut
				runOper = False
				self.addAdv()
			else:
				self.appTxt('<term>')
				# open paren signifies beginning of new expression
				if self.curOut in ['(', '[']:
					self.addAdv()
					self.compileExpression()
				# advances over unary operator and compiles next term
				elif self.curOut in Compiler.urnaryOps:
					oper = self.curOut
					runOper = False
					self.addAdv()
					self.compileTerm(oper)
				elif self.curOut == '"':
						self.compileStr()
				else:
					# push expr if not object or array 
					if self.addClassToFncCall() == False and self.isArray() == False:
						self.writePush()
					elif self.isArray() == True:
						varFields = self.getVarFields(self.curOut)
						self.addAdv(2)
						arrIndex = self.getVarFields(self.curOut)
						thatRef = varFields[1] + arrIndex[1]
						self.vm.append('push that ' + str(thatRef))
						self.addAdv()
					self.addAdv()
					# signifies object instance and advances to compile expression list
					if self.curOut == '.':
						self.addMethodToFncCall()
						self.appUntil('(', 1)
						self.compileExpressionList()
				self.appTxt('</term>')
			self.compileTerm(oper)
			if oper and runOper == True:
				self.writeOper(oper)
		return

	def writeOper(self, oper):
		ops = {
			"+": "add",
			"-": "sub",
			"*": "call Math.multipy()",
			"/": "call Math.divide()",
			"&": "and",
			"|": "or",
			"<": "lt",
			">": "gt",
			"=": "eq",
			"~": "not"
		}
		op = ops[oper]
		self.vm.append(op)	
		return

	def isArray(self):
		if self.nextOut == '[':
			return True
		else:
			return False

	# fnc call = "class." (method added later)
	def addClassToFncCall(self):
		if self.nextOut == '.':
			# Pushes method's object onto stack as hidden first param
			# only if first letter lowercase (meaning is an object - not a class)
			if self.curOut[0].isupper() == False:
				self.writePush()
			self.fncCall = 'call ' + self.curOut + self.nextOut
			return True
		else:
			return False

	# adds method to fnc call so is "class.method"
	def addMethodToFncCall(self):
		self.fncCall = self.fncCall + self.nextOut
		return

	def callFnc(self):
		if self.fncCall:
			self.vm.append(self.fncCall)
			self.fncCall = None
			self.exprCnt = 0
		return

	# write push statement
	# currently only handles int constants and expressions - need to implement string constants
	def writePush(self):
		keyDict = {'true': 'constant 1', 'false': 'constant 0', 'null': 'constant 0', 'this': 'pointer 0'}
		pushExpr = ''
		if self.curType == 'integerConstant':
			pushExpr = 'push contstant ' + str(self.curOut)
		elif self.curOut in keyDict:
			pushExpr = 'push ' + keyDict[self.curOut]
		else:
			varFields = self.getVarFields(self.curOut)
			if varFields:
				pushExpr = 'push ' + varFields[0] + ' ' + str(varFields[1]) + ': ' + self.curOut
		self.vm.append(pushExpr)
		if self.curOut == 'true':
			self.vm.append('neg')
		return

	def writePop(self, key):
		varFields = self.getVarFields(key)
		popExpr = 'pop ' + varFields[0] + ' ' + str(varFields[1])
		self.vm.append(popExpr)
		return

	def compileExpressionList(self, adv=0):
		self.appTxt('<expressionList>')
		if self.curOut != ')':
			# initializes expression count to 1
			self.exprCnt += 1
			self.compileExpression()
		self.appTxt('</expressionList>', 1)
		# add argument count to fnc call -> "class.method #args"
		self.fncCall = self.fncCall + ' ' + str(self.exprCnt)
		self.addAdv(adv)
		return

	# returns tuple of (0) kind and (1) index for given key
	# checks presence in prodecure-level table first then class-level table
	def getVarFields(self, key):
		if self.subTbl:
			if key in self.subTbl.hash:
				fields = self.subTbl.getIndexKind(key)
			else:
				fields = self.checkClassTable(key)
		else:
			fields = self.checkClassTable(key)
		return fields

	def checkClassTable(self, key):
		if key in self.tbl.hash:
			fields = self.tbl.getIndexKind(key)
		else:
			fields = None
		return fields

	# calculates number of field vars by iterating over table hash and counting number with kind = field
	# result will be pushed onto stack for constructor
	def calcFieldVars(self):
		fieldCnt = 0
		for key in self.tbl.hash:
			if self.tbl.hash[key]['kind'] == 'field':
				fieldCnt += 1
		return fieldCnt

	# tokenizer returns all words as single terms - creates string contstant type and string without quotes here
	def compileStr(self):
		self.advance()
		strCon = strTok().strAppend()
		self.curType = 'stringConstant' 
		newString = str(strCon)
		self.appTxt('<' + self.curType + '>' + newString + '</' + self.curType + '>')
		strLen = len(newString)
		self.vm.append('call String.new(' + str(strLen) + ')')
		for i in newString:
			self.vm.append('String.appendChar(' + i + ')')
		self.advance()
		return

	def makeFile(self):
		#print(self.t)
		# for i in self.vm:
		# 	print(i)
		print(str(self.tokCnt + 1) + ' of ' + str(len(self.tokens)))
		fileOut(self.t, fileNm, 'xml').write()
		fileOut(self.vm, fileNm, 'vm').write()


class strTok(object):

	def __init__(self):
		self.strBase = ''

	# returns string as single token - ends when hits quote
	def strAppend(self):
		if go.curOut != '"':
			if go.curOut in ['?', '.', ',', ':', ';']:
				spc = ''
			else:
				spc = ' '
			self.strBase = self.strBase + spc + go.curOut
			go.advance()
			self.strAppend()
		return self.strBase


fileNm = sys.argv[1]
go = Compiler(fileNm)
go.constructor()
