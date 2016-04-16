class Table(object):

	def __init__(self):
		self.hash = {}
		self.kIndex = {}
		self.kinds = []

	def appSymbol(self, symbol):
		# gets name, type, kind values from Symbol object
		name = Symbol(symbol).getName()
		sType = Symbol(symbol).getType()
		kind = Symbol(symbol).getKind()

		# gets symbol index
		# adds kind to kinds list if not present; otherwise increments index of kind
		if kind in self.kinds:
			self.kIndex[kind] += 1
		else:
			self.kinds.append(kind)
			self.kIndex[kind] = 0

		# add field values to fields dict
		fields = {}
		fields['type'] = sType
		fields['kind'] = kind
		fields['index'] = self.kIndex[kind]
		# adds fields to hash dict to create table of sorts that can be accessed with rtrnField method
		self.hash[name] = fields
		return

	# returns single value for given key (name) and field
	def rtrnField(self, name, field):
		return self.hash[name][field]

	# returns a tuple containing (0) kind and (1) index
	def getIndexKind(self, name):
		kind = self.hash[name]['kind']
		index = self.hash[name]['index']

		# adjust kind classifications for VM output format
		if kind == 'field':
			kind = 'this'
		elif kind == 'var':
			kind = 'local'

		return (kind, index)

class Symbol(object):
	
	# accepts list as parameter containing (0) name, (1) kind , (2) type
	def __init__(self, symbol):
		self.symbol = symbol

	def getKind(self):
		return self.symbol[0]

	def getType(self):
		return self.symbol[1]

	def getName(self):
		return self.symbol[2]
		
class Main(object):

	def __init__(self):
		example1 = ['static', 'int', 'nAccounts']
		example2 = ['field', 'int', 'id']
		example3 = ['field', 'string', 'name']
		examples = [example1, example2, example3]

		go = Table()

		for example in examples: 
			go.appSymbol(example)

		output = []
		fields = ['kind', 'type', 'index']
		for field in fields:
			output.append(go.rtrnField('id', field))

		print(output)
		return

if __name__ == '__main__':
	Main()