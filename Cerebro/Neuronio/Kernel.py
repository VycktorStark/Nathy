# encoding=utf8
from Cerebro.Neuronio import AimlParser
from Cerebro.Neuronio import DefaultSubs
from Cerebro.Neuronio import Utils
from Cerebro.Neuronio.PatternMgr import PatternMgr
from Cerebro.Neuronio.WordSub import WordSub
from urllib.request import urlopen
from configparser import ConfigParser
import copy
import glob
import os
import random
import re
import string
import sys
import time
import threading
import xml.sax


class Kernel:
    # module constants
    _globalSessionID = "_global" # key of the global session (duh)
    _maxHistorySize = 10 # maximum length of the _inputs and _responses lists
    _maxRecursionDepth = 100 # maximum number of recursive <srai>/<sr> tags before the response is aborted.
    # special predicate keys
    _inputHistory = "_inputHistory"     # keys to a queue (list) of recent user input
    _outputHistory = "_outputHistory"   # keys to a queue (list) of recent responses.
    _inputStack = "_inputStack"         # Should always be empty in between calls to respond()

    def __init__(self):
        self._verboseMode = True
        self._version = "1.0"
        self._brain = PatternMgr()
        self._respondLock = threading.RLock()
        self._textEncoding = "utf-8"

        # set up the sessions        
        self._sessions = {}
        self._addSession(self._globalSessionID)

        # Set up the bot predicates
        self._botPredicates = {}
        self.setBotPredicate("name", "Nameless")

        # set up the word substitutors (subbers):
        self._subbers = {}
        self._subbers['gender'] = WordSub(DefaultSubs.defaultGender)
        self._subbers['person'] = WordSub(DefaultSubs.defaultPerson)
        self._subbers['person2'] = WordSub(DefaultSubs.defaultPerson2)
        self._subbers['normal'] = WordSub(DefaultSubs.defaultNormal)
        
        # set up the element processors
        self._elementProcessors = {
            "bot":          self._processBot,
            "condition":    self._processCondition,
            "date":         self._processDate,
            "formal":       self._processFormal,
            "gender":       self._processGender,
            "get":          self._processGet,
            "gossip":       self._processGossip,
            "id":           self._processId,
            "input":        self._processInput,
            "javascript":   self._processJavascript,
            "learn":        self._processLearn,
            "li":           self._processLi,
            "lowercase":    self._processLowercase,
            "person":       self._processPerson,
            "person2":      self._processPerson2,
            "random":       self._processRandom,
            "text":         self._processText,
            "sentence":     self._processSentence,
            "set":          self._processSet,
            "size":         self._processSize,
            "sr":           self._processSr,
            "srai":         self._processSrai,
            "star":         self._processStar,
            "system":       self._processSystem,
            "template":     self._processTemplate,
            "that":         self._processThat,
            "thatstar":     self._processThatstar,
            "think":        self._processThink,
            "topicstar":    self._processTopicstar,
            "uppercase":    self._processUppercase,
            "version":      self._processVersion,
        }

    def bootstrap(self, brainFile = None, learnFiles = [], commands = []):
        start = time.clock()
        if brainFile:
            self.loadBrain(brainFile)
        learns = learnFiles
        try: learns = [ learnFiles + "" ]
        except: pass
        for file in learns:
            self.learn(file)
        cmds = commands
        try: cmds = [ commands + "" ]
        except: pass
        for cmd in cmds:
            print(self._respond(cmd, self._globalSessionID))
            
        if self._verboseMode:
            print("A inicialização do Núcleo cerebral do bot será concluída em %.2f segundos" % (time.clock() - start))

    def verbose(self, isVerbose = True):
        self._verboseMode = isVerbose

    def version(self):
        return self._version

    def numCategories(self):
        return self._brain.numTemplates()

    def resetBrain(self):
        del(self._brain)
        self.__init__()

    def loadBrain(self, filename):
        if self._verboseMode: print("Carregando cérebro de %s..." % filename, end=' ')
        start = time.clock()
        self._brain.restore(filename)
        if self._verboseMode:
            end = time.clock() - start
            print("\nPronto! (%d Categorias em %.2f segundos)" % (self._brain.numTemplates(), end))

    def saveBrain(self, filename):
        if self._verboseMode: print("Salvando o dados de resposta em %s..." % filename, end=' ')
        start = time.clock()
        self._brain.save(filename)
        if self._verboseMode:
            print("Pronto! (%.2f segundos)" % (time.clock() - start))

    def getPredicate(self, name, sessionID = _globalSessionID):
        try: return self._sessions[sessionID][name]
        except KeyError: return ""

    def setPredicate(self, name, value, sessionID = _globalSessionID):
        self._addSession(sessionID)
        self._sessions[sessionID][name] = value

    def getBotPredicate(self, name):
        try: return self._botPredicates[name]
        except KeyError: return ""

    def setBotPredicate(self, name, value):
        self._botPredicates[name] = value
        if name == "name":
            self._brain.setBotName(self.getBotPredicate("name"))

    def setTextEncoding(self, encoding):
        self._textEncoding = encoding

    def loadSubs(self, filename):
        inFile = open(filename)
        parser = ConfigParser()
        parser.readfp(inFile, filename)
        inFile.close()
        for s in parser.sections():
            if s in self._subbers:
                del(self._subbers[s])
            self._subbers[s] = WordSub()
            for k,v in parser.items(s):
                self._subbers[s][k] = v

    def _addSession(self, sessionID):
        if sessionID in self._sessions:
            return
        self._sessions[sessionID] = {
            self._inputHistory: [],
            self._outputHistory: [],
            self._inputStack: []
        }
        
    def _deleteSession(self, sessionID):
        if sessionID in self._sessions:
            self._sessions.pop(sessionID)

    def getSessionData(self, sessionID = None):
        s = None
        if sessionID is not None:
            try: s = self._sessions[sessionID]
            except KeyError: s = {}
        else:
            s = self._sessions
        return copy.deepcopy(s)

    def learn(self, filename):
        for f in glob.glob(filename):
            if self._verboseMode: print("Carregando {}...".format(f), end=' ')
            start = time.clock()
            parser = AimlParser.create_parser()
            handler = parser.getContentHandler()
            handler.setEncoding(self._textEncoding)
            try: parser.parse(f)
            except xml.sax.SAXParseException as msg:
                err = "\nErro Fatal no arquivo %s:\n%s\n" % (f,msg)
                sys.stderr.write(err)
                continue
            for key,tem in list(handler.categories.items()):
                self._brain.add(key,tem)
            if self._verboseMode:
                print("Pronto! (%.2f segundos)" % (time.clock() - start))

    def respond(self, inpt, sessionID = _globalSessionID):
        if len(inpt) == 0:
            return ""
        if sys.version_info.major <3:
            try: inpt = inpt.decode(self._textEncoding, 'replace')
            except UnicodeError: pass
            except AttributeError: pass
        self._respondLock.acquire()
        self._addSession(sessionID)
        sentences = Utils.sentences(inpt)
        finalResponse = ""
        for s in sentences:
            inputHistory = self.getPredicate(self._inputHistory, sessionID)
            inputHistory.append(s)
            while len(inputHistory) > self._maxHistorySize:
                inputHistory.pop(0)
            self.setPredicate(self._inputHistory, inputHistory, sessionID)
            response = self._respond(s, sessionID)
            outputHistory = self.getPredicate(self._outputHistory, sessionID)
            outputHistory.append(response)
            while len(outputHistory) > self._maxHistorySize:
                outputHistory.pop(0)
            self.setPredicate(self._outputHistory, outputHistory, sessionID)
            finalResponse += (response + "  ")
        finalResponse = finalResponse.strip()

        assert(len(self.getPredicate(self._inputStack, sessionID)) == 0)
        self._respondLock.release()
        try: 
            if sys.version_info.major < 3:
                return finalResponse.encode(self._textEncoding)
            else:
                return finalResponse
        except UnicodeError: 
            return finalResponse
    def _respond(self, inpt, sessionID):
        if len(inpt) == 0:
            return ""
        inputStack = self.getPredicate(self._inputStack, sessionID)
        if len(inputStack) > self._maxRecursionDepth:
            if self._verboseMode:
                err = "AVISO: O limite máxima de texto foi excedido ('%s')" % inpt.encode(self._textEncoding, 'replace')
                sys.stderr.write(err)
            return ""
        inputStack = self.getPredicate(self._inputStack, sessionID)
        inputStack.append(inpt)
        self.setPredicate(self._inputStack, inputStack, sessionID)
        subbedInput = self._subbers['normal'].sub(inpt)
        outputHistory = self.getPredicate(self._outputHistory, sessionID)
        try: that = outputHistory[-1]
        except IndexError: that = ""
        subbedThat = self._subbers['normal'].sub(that)
        topic = self.getPredicate("topic", sessionID)
        subbedTopic = self._subbers['normal'].sub(topic)
        response = ""
        elem = self._brain.match(subbedInput, subbedThat, subbedTopic)
        if elem is None:
            if self._verboseMode:
                response ='Não Entendi muito bem'
        else:
            response += self._processElement(elem, sessionID).strip()
            response += " "
        response = response.strip()
        inputStack = self.getPredicate(self._inputStack, sessionID)
        inputStack.pop()
        self.setPredicate(self._inputStack, inputStack, sessionID)
        
        return response

    def _processElement(self,elem, sessionID):
        try:
            handlerFunc = self._elementProcessors[elem[0]]
        except:
            if self._verboseMode:
                err = "AVISO: Nenhum manipulador encontrado para <%s> elemento\n" % elem[0].encode(self._textEncoding, 'replace')
                sys.stderr.write(err)
            return ""
        return handlerFunc(elem, sessionID)

    # <bot>
    def _processBot(self, elem, sessionID):
        attrName = elem[1]['name']
        return self.getBotPredicate(attrName)
        
    # <condition>
    def _processCondition(self, elem, sessionID):
        attr = None  # @UnusedVariable
        response = ""
        attr = elem[1]
        if 'name' in attr and 'value' in attr:
            val = self.getPredicate(attr['name'], sessionID)
            if val == attr['value']:
                for e in elem[2:]:
                    response += self._processElement(e,sessionID)
                return response
        else:
            try:
                name = None
                if 'name' in attr:
                    name = attr['name']
                listitems = []
                for e in elem[2:]:
                    if e[0] == 'li':
                        listitems.append(e)
                if len(listitems) == 0:
                    return ""
                foundMatch = False
                for li in listitems:
                    try:
                        liAttr = li[1]
                        if len(list(liAttr.keys())) == 0 and li == listitems[-1]:
                            continue
                        liName = name
                        if liName == None:
                            liName = liAttr['name']
                        liValue = liAttr['value']
                        if self.getPredicate(liName, sessionID) == liValue:
                            foundMatch = True
                            response += self._processElement(li,sessionID)
                            break
                    except:
                        if self._verboseMode: print("Algo errado - ignorando Item da lista", li)
                        raise
                if not foundMatch:
                    try:
                        li = listitems[-1]
                        liAttr = li[1]
                        if not ('name' in liAttr or 'value' in liAttr):
                            response += self._processElement(li, sessionID)
                    except:
                        if self._verboseMode: print("Erro no padrão do Item da lista")
                        raise
            except:
                if self._verboseMode: print("Falha catastrófica")
                raise
        return response
        
    # <date>
    def _processDate(self, elem, sessionID):
        return time.asctime()

    # <formal>
    def _processFormal(self, elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        return string.capwords(response)

    # <gender>
    def _processGender(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        return self._subbers['gender'].sub(response)

    # <get>
    def _processGet(self, elem, sessionID):
        return self.getPredicate(elem[1]['name'], sessionID)

    # <gossip>
    def _processGossip(self, elem, sessionID):
        return self._processThink(elem, sessionID)

    # <id>
    def _processId(self, elem, sessionID):
        return sessionID

    # <input>
    def _processInput(self, elem, sessionID):    
        inputHistory = self.getPredicate(self._inputHistory, sessionID)
        try: index = int(elem[1]['index'])
        except: index = 1
        try: return inputHistory[-index]
        except IndexError:
            if self._verboseMode:
                err = "Nenhum índice %d Enquanto processa o elemento <input>.\n" % index
                sys.stderr.write(err)
            return ""

    # <javascript>
    def _processJavascript(self, elem, sessionID):
        return self._processThink(elem, sessionID)
    
    # <learn>
    def _processLearn(self, elem, sessionID):
        filename = ""
        for e in elem[2:]:
            filename += self._processElement(e, sessionID)
        self.learn(filename)
        return ""

    # <li>
    def _processLi(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        return response

    # <lowercase>
    def _processLowercase(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        return response.lower()

    # <person>
    def _processPerson(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        if len(elem[2:]) == 0:
            response = self._processElement(['star',{}], sessionID)    
        return self._subbers['person'].sub(response)

    # <person2>
    def _processPerson2(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        if len(elem[2:]) == 0:
            response = self._processElement(['star',{}], sessionID)
        return self._subbers['person2'].sub(response)
        
    # <random>
    def _processRandom(self, elem, sessionID):
        listitems = []
        for e in elem[2:]:
            if e[0] == 'li':
                listitems.append(e)
        if len(listitems) == 0:
            return ""
        random.shuffle(listitems)
        return self._processElement(listitems[0], sessionID)
        
    # <sentence>
    def _processSentence(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        try:
            response = response.strip()
            words = response.split(" ", 1)
            words[0] = words[0].capitalize()
            response = " ".join(words)
            return response
        except IndexError: # response was empty
            return ""

    # <set>
    def _processSet(self, elem, sessionID):
        value = ""
        for e in elem[2:]:
            value += self._processElement(e, sessionID)
        self.setPredicate(elem[1]['name'], value, sessionID)    
        return value

    # <size>
    def _processSize(self,elem, sessionID):
        return str(self.numCategories())

    # <sr>
    def _processSr(self,elem,sessionID):
        star = self._processElement(['star',{}], sessionID)
        response = self._respond(star, sessionID)
        return response

    # <srai>
    def _processSrai(self,elem, sessionID):
        newInput = ""
        for e in elem[2:]:
            newInput += self._processElement(e, sessionID)
        return self._respond(newInput, sessionID)

    # <star>
    def _processStar(self, elem, sessionID):
        try: index = int(elem[1]['index'])
        except KeyError: index = 1
        # fetch the user's last input
        inputStack = self.getPredicate(self._inputStack, sessionID)
        inpt = self._subbers['normal'].sub(inputStack[-1])
        # fetch the Kernel's last response (for 'that' context)
        outputHistory = self.getPredicate(self._outputHistory, sessionID)
        try: that = self._subbers['normal'].sub(outputHistory[-1])
        except: that = "" # there might not be any output yet
        topic = self.getPredicate("topic", sessionID)
        response = self._brain.star("star", inpt, that, topic, index)
        return response
    
    # <system>
    def _processSystem(self,elem, sessionID):
        # build up the command string
        command = ""
        for e in elem[2:]:
            command += self._processElement(e, sessionID)

        # normalize the path to the command.  Under Windows, this
        # switches forward-slashes to back-slashes; all system
        # elements should use unix-style paths for cross-platform
        # compatibility.
        #executable,args = command.split(" ", 1)
        #executable = os.path.normpath(executable)
        #command = executable + " " + args
        command = os.path.normpath(command)

        # execute the command.
        response = ""
        try:
            out = os.popen(command)            
        except RuntimeError as msg:
            if self._verboseMode:
                err = "AVISO: tempo de execução excedido ao processar o elemento \"system\":\n%s\n" % msg.encode(self._textEncoding, 'replace')
                sys.stderr.write(err)
            return "Ocorreu um erro ao calcular minha resposta. Por favor, informe o meu Desenvolvedor."
        time.sleep(0.01) # I'm told this works around a potential IOError exception.
        for line in out:
            response += line + "\n"
        response = " ".join(response.splitlines()).strip()
        return response

    # <template>
    def _processTemplate(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        return response

    # text
    def _processText(self,elem, sessionID):
        try: elem[2] + ""
        except TypeError: raise TypeError("O conteúdo do elemento de texto não é texto")
        if elem[1]["xml:space"] == "default":
            elem[2] = re.sub("\s+", " ", elem[2])
            elem[1]["xml:space"] = "preserve"
        return elem[2]

    # <that>
    def _processThat(self,elem, sessionID):
        outputHistory = self.getPredicate(self._outputHistory, sessionID)
        index = 1
        try:
            # According to the AIML spec, the optional index attribute
            # can either have the form "x" or "x,y". x refers to how
            # far back in the output history to go.  y refers to which
            # sentence of the specified response to return.
            index = int(elem[1]['index'].split(',')[0])
        except:
            pass
        try: return outputHistory[-index]
        except IndexError:
            if self._verboseMode:
                err = "Nenhum índice %d durante o processamento desse elemento.\n" % index
                sys.stderr.write(err)
            return ""

    # <thatstar>
    def _processThatstar(self, elem, sessionID):
        try: index = int(elem[1]['index'])
        except KeyError: index = 1
        # fetch the user's last input
        inputStack = self.getPredicate(self._inputStack, sessionID)
        inpt = self._subbers['normal'].sub(inputStack[-1])
        # fetch the Kernel's last response (for 'that' context)
        outputHistory = self.getPredicate(self._outputHistory, sessionID)
        try: that = self._subbers['normal'].sub(outputHistory[-1])
        except: that = "" # there might not be any output yet
        topic = self.getPredicate("topic", sessionID)
        response = self._brain.star("thatstar", inpt, that, topic, index)
        return response

    # <think>
    def _processThink(self,elem, sessionID):
        for e in elem[2:]:
            self._processElement(e, sessionID)
        return ""

    # <topicstar>
    def _processTopicstar(self, elem, sessionID):
        try: index = int(elem[1]['index'])
        except KeyError: index = 1
        # fetch the user's last input
        inputStack = self.getPredicate(self._inputStack, sessionID)
        inpt = self._subbers['normal'].sub(inputStack[-1])
        # fetch the Kernel's last response (for 'that' context)
        outputHistory = self.getPredicate(self._outputHistory, sessionID)
        try: that = self._subbers['normal'].sub(outputHistory[-1])
        except: that = "" # there might not be any output yet
        topic = self.getPredicate("topic", sessionID)
        response = self._brain.star("topicstar", inpt, that, topic, index)
        return response

    # <uppercase>
    def _processUppercase(self,elem, sessionID):
        response = ""
        for e in elem[2:]:
            response += self._processElement(e, sessionID)
        return response.upper()

    # <version>
    def _processVersion(self,elem, sessionID):
        return self.version()
def _testTag(kern, tag, inpt, outputList):
    global _numTests, _numPassed
    _numTests += 1
    print("Testando <" + tag + ">:", end=' ')
    response = kern.respond(inpt).decode(kern._textEncoding)
    if response in outputList:
        print("Aprovado")
        _numPassed += 1
        return True
    else:
        print("FALHA (resposta: '%s')" % response.encode(kern._textEncoding, 'replace'))
        return False
