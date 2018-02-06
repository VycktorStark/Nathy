import marshal
import pprint
import re
import string
import sys

class PatternMgr:
	_UNDERSCORE = 0
	_STAR       = 1
	_TEMPLATE   = 2
	_THAT       = 3
	_TOPIC		= 4
	_BOT_NAME   = 5
	
	def __init__(self):
		self._root = {}
		self._templateCount = 0
		self._botName = "Nameless"
		punctuation = "\"`~!@#$%^&*()-_=+[{]}\|;:',<.>/?"
		self._puncStripRE = re.compile("[" + re.escape(punctuation) + "]")
		self._whitespaceRE = re.compile("\s+", re.LOCALE | re.UNICODE)

	def numTemplates(self):
		return self._templateCount

	def setBotName(self, name):
		self._botName = str(" ".join(name.split()))

	def dump(self):
		pprint.pprint(self._root)

	def save(self, filename):
		try:
			outFile = open(filename, "wb")
			marshal.dump(self._templateCount, outFile)
			marshal.dump(self._botName, outFile)
			marshal.dump(self._root, outFile)
			outFile.close()
		except Exception as e:
			print("Erro ao salvar no arquivo %s:" % filename)
			raise Exception(e)

	def restore(self, filename):
		try:
			inFile = open(filename, "rb")
			self._templateCount = marshal.load(inFile)
			self._botName = marshal.load(inFile)
			self._root = marshal.load(inFile)
			inFile.close()
		except Exception as e:
			print("\nOcorreu um erro ao atualizar memoria do bot que esta salva em: %s\n\nCarregando Novamente:\n" % filename)
			raise Exception(e)

	def add(self, xxx_todo_changeme, template):
		(pattern,that,topic) = xxx_todo_changeme
		node = self._root
		for word in pattern.split():
			key = word
			if key == "_":
				key = self._UNDERSCORE
			elif key == "*":
				key = self._STAR
			elif key == "BOT_NAME":
				key = self._BOT_NAME
			if key not in node:
				node[key] = {}
			node = node[key]
		if len(that) > 0:
			if self._THAT not in node:
				node[self._THAT] = {}
			node = node[self._THAT]
			for word in that.split():
				key = word
				if key == "_":
					key = self._UNDERSCORE
				elif key == "*":
					key = self._STAR
				if key not in node:
					node[key] = {}
				node = node[key]
		if len(topic) > 0:
			if self._TOPIC not in node:
				node[self._TOPIC] = {}
			node = node[self._TOPIC]
			for word in topic.split():
				key = word
				if key == "_":
					key = self._UNDERSCORE
				elif key == "*":
					key = self._STAR
				if key not in node:
					node[key] = {}
				node = node[key]
		if self._TEMPLATE not in node:
			self._templateCount += 1	
		node[self._TEMPLATE] = template

	def match(self, pattern, that, topic):
		if len(pattern) == 0:
			return None
		inpt = pattern.upper()
		inpt = re.sub(self._puncStripRE, " ", inpt)
		if that.strip() == "": that = "ULTRABOGUSDUMMYTHAT"
		thatInput = that.upper()
		thatInput = re.sub(self._puncStripRE, " ", thatInput)
		thatInput = re.sub(self._whitespaceRE, " ", thatInput)
		if topic.strip() == "": topic = "ULTRABOGUSDUMMYTOPIC"
		topicInput = topic.upper()
		topicInput = re.sub(self._puncStripRE, " ", topicInput)
		patMatch, template = self._match(inpt.split(), thatInput.split(), topicInput.split(), self._root)
		return template

	def star(self, starType, pattern, that, topic, index):
		inpt = pattern.upper()
		inpt = re.sub(self._puncStripRE, " ", inpt)
		inpt = re.sub(self._whitespaceRE, " ", inpt)
		if that.strip() == "": that = "ULTRABOGUSDUMMYTHAT"
		thatInput = that.upper()
		thatInput = re.sub(self._puncStripRE, " ", thatInput)
		thatInput = re.sub(self._whitespaceRE, " ", thatInput)
		if topic.strip() == "": topic = "ULTRABOGUSDUMMYTOPIC"
		topicInput = topic.upper()
		topicInput = re.sub(self._puncStripRE, " ", topicInput)
		topicInput = re.sub(self._whitespaceRE, " ", topicInput)
		patMatch, template = self._match(inpt.split(), thatInput.split(), topicInput.split(), self._root)
		if template == None:
			return ""
		words = None
		if starType == 'star':
			patMatch = patMatch[:patMatch.index(self._THAT)]
			words = inpt.split()
		elif starType == 'thatstar':
			patMatch = patMatch[patMatch.index(self._THAT)+1 : patMatch.index(self._TOPIC)]
			words = thatInput.split()
		elif starType == 'topicstar':
			patMatch = patMatch[patMatch.index(self._TOPIC)+1 :]
			words = topicInput.split()
		else:
			raise ValueError("starType must be in ['star', 'thatstar', 'topicstar']")
		foundTheRightStar = False
		start = end = j = numStars = k = 0
		for i in range(len(words)):
			if i < k:
				continue
			if j == len(patMatch):
				break
			if not foundTheRightStar:
				if patMatch[j] in [self._STAR, self._UNDERSCORE]: 
					numStars += 1
					if numStars == index:
						foundTheRightStar = True
					start = i
					for k in range (i, len(words)):
						if j+1  == len (patMatch):
							end = len (words)
							break
						if patMatch[j+1] == words[k]:
							end = k - 1
							i = k
							break
				if foundTheRightStar:
					break
			j += 1
		if foundTheRightStar:
			if starType == 'star': return " ".join(pattern.split()[start:end+1])
			elif starType == 'thatstar': return " ".join(that.split()[start:end+1])
			elif starType == 'topicstar': return " ".join(topic.split()[start:end+1])
		else: return ""

	def _match(self, words, thatWords, topicWords, root):
		if len(words) == 0:
			pattern = []
			template = None
			if len(thatWords) > 0:
				try:
					pattern, template = self._match(thatWords, [], topicWords, root[self._THAT])
					if pattern != None:
						pattern = [self._THAT] + pattern
				except KeyError:
					pattern = []
					template = None
			elif len(topicWords) > 0:
				try:
					pattern, template = self._match(topicWords, [], [], root[self._TOPIC])
					if pattern != None:
						pattern = [self._TOPIC] + pattern
				except KeyError:
					pattern = []
					template = None
			if template == None:
				pattern = []
				try: template = root[self._TEMPLATE]
				except KeyError: template = None
			return (pattern, template)

		first = words[0]
		suffix = words[1:]
		if self._UNDERSCORE in root:
			for j in range(len(suffix)+1):
				suf = suffix[j:]
				pattern, template = self._match(suf, thatWords, topicWords, root[self._UNDERSCORE])
				if template is not None:
					newPattern = [self._UNDERSCORE] + pattern
					return (newPattern, template)
		if first in root:
			pattern, template = self._match(suffix, thatWords, topicWords, root[first])
			if template is not None:
				newPattern = [first] + pattern
				return (newPattern, template)
		if self._BOT_NAME in root and first == self._botName:
			pattern, template = self._match(suffix, thatWords, topicWords, root[self._BOT_NAME])
			if template is not None:
				newPattern = [first] + pattern
				return (newPattern, template)
		if self._STAR in root:
			for j in range(len(suffix)+1):
				suf = suffix[j:]
				pattern, template = self._match(suf, thatWords, topicWords, root[self._STAR])
				if template is not None:
					newPattern = [self._STAR] + pattern
					return (newPattern, template)
		return (None, None)			
