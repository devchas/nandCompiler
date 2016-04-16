#file input and output handling module

#file input handling
class fileIn(object):
	
	def __init__(self, fileIn):
		self.fileIn = fileIn
		
	#return full text of file
	def fileText(self):
		with open(str(self.fileIn), 'r') as f:
			return f.read()
	
	#create array by line from file input
	def fileLines(self):
		lineList = []
		with open(str(self.fileIn), 'r') as f:
			for line in f:
				lineList.append(line)
		return lineList
		
	#returns number of lines in file
	def fLineCnt(self):
		return len(self.fileLines())

#file output handling
class fileOut(object):
	
	def __init__(self, text, file, ext):
		self.text = text
		self.file = file
		self.ext = ext
		#give file new name
		fileParts = self.file.split('.')
		fileW = fileParts[0] + '.' + self.ext
		self.fileW = fileW
		
	#converts list to text file with each list item as line
	def write(self):
		with open(self.fileW, 'w', newline='') as f:
			if isinstance(self.text, list):
				for i in self.text:
					f.write(i + '\n')
					#print(i)
			elif isinstance(self.text, str):
				f.write(self.text)