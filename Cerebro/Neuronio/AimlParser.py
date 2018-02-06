from xml.sax.handler import ContentHandler
from xml.sax.xmlreader import Locator
import sys
import xml.sax
import xml.sax.handler

class AimlParserError(Exception): pass

class AimlHandler(ContentHandler):
	# The legal states of the AIML parser
	_STATE_OutsideAiml    = 0
	_STATE_InsideAiml     = 1
	_STATE_InsideCategory = 2
	_STATE_InsidePattern  = 3
	_STATE_AfterPattern   = 4
	_STATE_InsideThat     = 5
	_STATE_AfterThat      = 6
	_STATE_InsideTemplate = 7
	_STATE_AfterTemplate  = 8
	
	def __init__(self, encoding = "UTF-8"):
		self.categories = {}
		self._encoding = encoding
		self._state = self._STATE_OutsideAiml
		self._version = ""
		self._namespace = ""
		self._forwardCompatibleMode = False
		self._currentPattern = ""
		self._currentThat    = ""
		self._currentTopic   = ""
		self._insideTopic = False
		self._currentUnknown = ""
		self._skipCurrentCategory = False
		self._numParseErrors = 0
		self._validInfo = self._validationInfo101
		self._foundDefaultLiStack = []
		self._whitespaceBehaviorStack = ["default"]
		
		self._elemStack = []
		self._locator = Locator()
		self.setDocumentLocator(self._locator)

	def getNumErrors(self):
		return self._numParseErrors

	def setEncoding(self, encoding):
		self._encoding = encoding

	def _location(self):
		line = self._locator.getLineNumber()
		column = self._locator.getColumnNumber()
		return "(line %d, column %d)" % (line, column)

	def _pushWhitespaceBehavior(self, attr):
		assert len(self._whitespaceBehaviorStack) > 0, "Pilha de comportamento de espaço em branco nunca deve estar vazia!"
		try:
			if attr["xml:space"] == "default" or attr["xml:space"] == "preserve":
				self._whitespaceBehaviorStack.append(attr["xml:space"])
			else:
				raise AimlParserError("Invalid value for xml:space attribute "+self._location())
		except KeyError:
			self._whitespaceBehaviorStack.append(self._whitespaceBehaviorStack[-1])

	def startElementNS(self, name, qname, attr):
		print("QNAME:", qname)
		print("NAME:", name)
		uri,elem = name
		if (elem == "bot"): print("name:", attr.getValueByQName("name"), "a'ite?")
		self.startElement(elem, attr)
		pass

	def startElement(self, name, attr):
		if self._currentUnknown != "":
			return
		if self._skipCurrentCategory:
			return
		try: self._startElement(name, attr)
		except AimlParserError as msg:
			sys.stderr.write("PARSE ERROR: %s\n" % msg)
			self._numParseErrors += 1
			if self._state >= self._STATE_InsideCategory:
				self._skipCurrentCategory = True
			
	def _startElement(self, name, attr):
		if name == "aiml":
			if self._state != self._STATE_OutsideAiml:
				raise AimlParserError("Unexpected <aiml> tag "+self._location())
			self._state = self._STATE_InsideAiml
			self._insideTopic = False
			self._currentTopic = ""
			try: self._version = attr["version"]
			except KeyError:
				self._version = "1.0"
			self._forwardCompatibleMode = (self._version != "1.0.1")
			self._pushWhitespaceBehavior(attr)
		elif self._state == self._STATE_OutsideAiml:
			return
		elif name == "topic":
			if (self._state != self._STATE_InsideAiml) or self._insideTopic:
				raise AimlParserError("Unexpected <topic> tag").with_traceback(self._location())
			try: self._currentTopic = str(attr['name'])
			except KeyError:
				raise AimlParserError("Required \"name\" attribute missing in <topic> element "+self._location())
			self._insideTopic = True
		elif name == "category":
			if self._state != self._STATE_InsideAiml:
				raise AimlParserError("Unexpected <category> tag "+self._location())
			self._state = self._STATE_InsideCategory
			self._currentPattern = ""
			self._currentThat = ""
			if not self._insideTopic: self._currentTopic = "*"
			self._elemStack = []
			self._pushWhitespaceBehavior(attr)
		elif name == "pattern":
			if self._state != self._STATE_InsideCategory:
				raise AimlParserError("Unexpected <pattern> tag "+self._location())
			self._state = self._STATE_InsidePattern
		elif name == "that" and self._state == self._STATE_AfterPattern:
			self._state = self._STATE_InsideThat
		elif name == "template":
			if self._state not in [self._STATE_AfterPattern, self._STATE_AfterThat]:
				raise AimlParserError("Unexpected <template> tag "+self._location())
			if self._state == self._STATE_AfterPattern:
				self._currentThat = "*"
			self._state = self._STATE_InsideTemplate
			self._elemStack.append(['template',{}])
			self._pushWhitespaceBehavior(attr)
		elif self._state == self._STATE_InsidePattern:
			if name == "bot" and "name" in attr and attr["name"] == "name":
				self._currentPattern += " BOT_NAME "
			else:
				raise AimlParserError(("Unexpected <%s> tag " % name)+self._location())
		elif self._state == self._STATE_InsideThat:
			if name == "bot" and "name" in attr and attr["name"] == "name":
				self._currentThat += " BOT_NAME "
			else:
				raise AimlParserError(("Unexpected <%s> tag " % name)+self._location())
		elif self._state == self._STATE_InsideTemplate and name in self._validInfo:
			attrDict = {}
			for k,v in list(attr.items()):
				attrDict[str(k)] = str(v)
			self._validateElemStart(name, attrDict, self._version)
			self._elemStack.append([name,attrDict])
			self._pushWhitespaceBehavior(attr)
			if name == "condition":
				self._foundDefaultLiStack.append(False)
		else:
			if self._forwardCompatibleMode:
				self._currentUnknown = name
			else:
				raise AimlParserError(("Unexpected <%s> tag " % name)+self._location())
	def characters(self, ch):
		if self._state == self._STATE_OutsideAiml:
			return
		if self._currentUnknown != "":
			return
		if self._skipCurrentCategory:
			return
		try: self._characters(ch)
		except AimlParserError as msg:
			sys.stderr.write("PARSE ERROR: %s\n" % msg)
			self._numParseErrors += 1
			if self._state >= self._STATE_InsideCategory:
				self._skipCurrentCategory = True
			
	def _characters(self, ch):
		text = str(ch)
		if self._state == self._STATE_InsidePattern:
			self._currentPattern += text
		elif self._state == self._STATE_InsideThat:
			self._currentThat += text
		elif self._state == self._STATE_InsideTemplate:
			try:
				parent = self._elemStack[-1][0]
				parentAttr = self._elemStack[-1][1]
				required, optional, canBeParent = self._validInfo[parent]
				nonBlockStyleCondition = (parent == "condition" and not ("name" in parentAttr and "value" in parentAttr))
				if not canBeParent:
					raise AimlParserError(("Unexpected text inside <%s> element "%parent)+self._location())
				elif parent == "random" or nonBlockStyleCondition:
					if len(text.strip()) == 0:
						return
					else:
						raise AimlParserError(("Unexpected text inside <%s> element "%parent)+self._location())
			except IndexError:
				raise AimlParserError("Element stack is empty while validating text "+self._location())
			try: textElemOnStack = (self._elemStack[-1][-1][0] == "text")
			except IndexError: textElemOnStack = False
			except KeyError: textElemOnStack = False
			if textElemOnStack:
				self._elemStack[-1][-1][2] += text
			else:
				self._elemStack[-1].append(["text", {"xml:space": self._whitespaceBehaviorStack[-1]}, text])
		else:
			pass

	def endElementNS(self, name, qname):
		uri, elem = name
		self.endElement(elem)
		
	def endElement(self, name):
		"""Wrapper around _endElement which catches errors in _characters()
		and keeps going.

		"""		
		if self._state == self._STATE_OutsideAiml:
			return
		if self._currentUnknown != "":
			if name == self._currentUnknown:
				self._currentUnknown = ""
			return
		if self._skipCurrentCategory:
			if name == "category":
				self._skipCurrentCategory = False
				self._state = self._STATE_InsideAiml
			return
		try: self._endElement(name)
		except AimlParserError as msg:
			sys.stderr.write("PARSE ERROR: %s\n" % msg)
			self._numParseErrors += 1
			if self._state >= self._STATE_InsideCategory:
				self._skipCurrentCategory = True

	def _endElement(self, name):
		if name == "aiml":
			if self._state != self._STATE_InsideAiml:
				raise AimlParserError("Unexpected </aiml> tag "+self._location())
			self._state = self._STATE_OutsideAiml
			self._whitespaceBehaviorStack.pop()
		elif name == "topic":
			if self._state != self._STATE_InsideAiml or not self._insideTopic:
				raise AimlParserError("Unexpected </topic> tag "+self._location())
			self._insideTopic = False
			self._currentTopic = ""
		elif name == "category":
			if self._state != self._STATE_AfterTemplate:
				raise AimlParserError("Unexpected </category> tag "+self._location())
			self._state = self._STATE_InsideAiml
			key = (self._currentPattern.strip(), self._currentThat.strip(),self._currentTopic.strip())
			self.categories[key] = self._elemStack[-1]
			self._whitespaceBehaviorStack.pop()
		elif name == "pattern":
			if self._state != self._STATE_InsidePattern:
				raise AimlParserError("Unexpected </pattern> tag "+self._location())
			self._state = self._STATE_AfterPattern
		elif name == "that" and self._state == self._STATE_InsideThat:
			self._state = self._STATE_AfterThat
		elif name == "template":
			if self._state != self._STATE_InsideTemplate:
				raise AimlParserError("Unexpected </template> tag "+self._location())
			self._state = self._STATE_AfterTemplate
			self._whitespaceBehaviorStack.pop()
		elif self._state == self._STATE_InsidePattern:
			if name not in ["bot"]:
				raise AimlParserError(("Unexpected </%s> tag " % name)+self._location())
		elif self._state == self._STATE_InsideThat:
			if name not in ["bot"]:
				raise AimlParserError(("Unexpected </%s> tag " % name)+self._location())
		elif self._state == self._STATE_InsideTemplate:
			elem = self._elemStack.pop()
			self._elemStack[-1].append(elem)
			self._whitespaceBehaviorStack.pop()
			if elem[0] == "condition": self._foundDefaultLiStack.pop()
		else:
			raise AimlParserError(("Unexpected </%s> tag " % name)+self._location())
	_validationInfo101 = {
		"bot":      	( ["name"], [], False ),
		"condition":    ( [], ["name", "value"], True ), 
		"date":         ( [], [], False ),
		"formal":       ( [], [], True ),
		"gender":       ( [], [], True ),
		"get":          ( ["name"], [], False ),
		"gossip":		( [], [], True ),
		"id":           ( [], [], False ),
		"input":        ( [], ["index"], False ),
		"javascript":	( [], [], True ),
		"learn":        ( [], [], True ),
		"li":           ( [], ["name", "value"], True ),
		"lowercase":    ( [], [], True ),
		"person":       ( [], [], True ),
		"person2":      ( [], [], True ),
		"random":       ( [], [], True ), 
		"sentence":     ( [], [], True ),
		"set":          ( ["name"], [], True),
		"size":         ( [], [], False ),
		"sr":           ( [], [], False ),
		"srai":         ( [], [], True ),
		"star":         ( [], ["index"], False ),
		"system":       ( [], [], True ),
		"template":		( [], [], True ), 
		"that":         ( [], ["index"], False ),
		"thatstar":     ( [], ["index"], False ),
		"think":        ( [], [], True ),
		"topicstar":    ( [], ["index"], False ),
		"uppercase":    ( [], [], True ),
		"version":      ( [], [], False ),
	}

	def _validateElemStart(self, name, attr, version):
		required, optional, canBeParent = self._validInfo[name]  
		for a in required:
			if a not in attr and not self._forwardCompatibleMode:
				raise AimlParserError(("Required \"%s\" attribute missing in <%s> element " % (a,name))+self._location())
		for a in attr:
			if a in required: continue
			if a[0:4] == "xml:": continue
			if a not in optional and not self._forwardCompatibleMode:
				raise AimlParserError(("Unexpected \"%s\" attribute in <%s> element " % (a,name))+self._location())
		if name in ["star", "thatstar", "topicstar"]:
			for k,v in list(attr.items()):
				if k == "index":
					temp = 0
					try: temp = int(v)
					except:
						raise AimlParserError(("Bad type for \"%s\" attribute (expected integer, found \"%s\") " % (k,v))+self._location())
					if temp < 1:
						raise AimlParserError(("\"%s\" attribute must have non-negative value " % (k))+self._location())
		try:
			parent = self._elemStack[-1][0]
			parentAttr = self._elemStack[-1][1]
		except IndexError:
			raise AimlParserError(("Element stack is empty while validating <%s> " % name)+self._location())
		required, optional, canBeParent = self._validInfo[parent]
		nonBlockStyleCondition = (parent == "condition" and not ("name" in parentAttr and "value" in parentAttr))
		if not canBeParent:
			raise AimlParserError(("<%s> elements cannot have any contents "%parent)+self._location())
		elif (parent == "random" or nonBlockStyleCondition) and name!="li":
			raise AimlParserError(("<%s> elements can only contain <li> subelements "%parent)+self._location())
		elif name=="li":
			if not (parent=="random" or nonBlockStyleCondition):
				raise AimlParserError(("Unexpected <li> element contained by <%s> element "%parent)+self._location())
			if nonBlockStyleCondition:
				if "name" in parentAttr:
					if len(attr) == 0:
						if self._foundDefaultLiStack[-1]:
							raise AimlParserError("Unexpected default <li> element inside <condition> "+self._location())
						else:
							self._foundDefaultLiStack[-1] = True
					elif len(attr) == 1 and "value" in attr:
						pass
					else:
						raise AimlParserError("Invalid <li> inside single-predicate <condition> "+self._location())
				elif len(parentAttr) == 0:
					if len(attr) == 0:
						if self._foundDefaultLiStack[-1]:
							raise AimlParserError("Unexpected default <li> element inside <condition> "+self._location())
						else:
							self._foundDefaultLiStack[-1] = True
					elif len(attr) == 2 and "value" in attr and "name" in attr:
						pass
					else:
						raise AimlParserError("Invalid <li> inside multi-predicate <condition> "+self._location())
		return True

def create_parser():
	parser = xml.sax.make_parser()
	handler = AimlHandler("UTF-8")
	parser.setContentHandler(handler)
	return parser

def main():
	parser = create_parser()
	handler = parser.getContentHandler()
	handler.setEncoding("utf-8")
		
	for key, tem in handler.categories.items():
		print("Key = %s, tem = %s" % (key, tem))

if __name__ == '__main__':
	main()
