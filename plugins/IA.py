from config import *
def CleanReacion(msg):
            msg = re.sub('reaçãoespantado', '', msg)
            msg = re.sub('reaçãopiscando', '', msg)
            msg = re.sub('reaçãosolhosfechados', '', msg)
            msg = re.sub('reaçãotriste', '', msg)
            msg = re.sub('reaçãosorridente', '', msg)
            msg = re.sub('reaçãonormal', '', msg)
            return msg
def Chat(self,base, chat_type, msg, enviar):
  msg = CleanReacion(msg)
  if enviar == "Sim":
        if 'private' in chat_type or base['text'].startswith("@NathyRoBot "):
          self.sendMessage(msg, "Markdown")
        else:
          if "reply_to_message" in base:
            if base["reply_to_message"]["from"]["id"] == bot["id"]:
                self.sendMessage(msg, "Markdown", reply_to_message_id=base["message_id"])
  return None
class IA:
    def __init__(self,sender, base, texto, nome_user, username_user, id_user, input_texto, chat_type):
        self.sender = sender
        self.base = base
        self.texto = texto
        self.input_texto = input_texto
        self.nome_user = nome_user
        self.username_user = username_user
        self.id_user = id_user
        self.chat_type = chat_type

    def INBOT(self):
      global enviar
      texto_ = self.texto
      if texto_ == ".":
        texto_ = "😶"
      msg = AI(texto_, self.nome_user, self.id_user)
      enviar = "Sim"
      for c in normal:
        if self.texto.startswith(c) or c in msg.lower():
            msg = CleanReacion(msg)
            enviar = "Sim"
            if "reply_to_message" in self.base:
              if self.base["reply_to_message"]["from"]["id"] == bot["id"]:
                self.sender.sendSticker('CAADAQADBwADMX7IRU_8qKe4_akQAg')
            if 'private' in self.chat_type or self.texto.startswith("@NathyRoBot "):
                self.sender.sendSticker('CAADAQADBwADMX7IRU_8qKe4_akQAg')
            break
      for c in espantado:
          if self.texto.startswith(c) or c in msg.lower():
            msg = CleanReacion(msg)
            enviar = "Sim"
            if "reply_to_message" in self.base:
              if self.base["reply_to_message"]["from"]["id"] == bot["id"]:
                self.sender.sendSticker('CAADAQADCwADMX7IRZHNp0DTcDS7Ag')
            if 'private' in self.chat_type or self.texto.startswith("@NathyRoBot "):
                self.sender.sendSticker('CAADAQADCwADMX7IRZHNp0DTcDS7Ag')
            break
      for c in piscando:
          if self.texto.startswith(c) or c in msg.lower():
            msg = CleanReacion(msg)
            enviar = "Sim"
            if "reply_to_message" in self.base:
              if self.base["reply_to_message"]["from"]["id"] == bot["id"]:
                self.sender.sendSticker('CAADAQADCAADMX7IRXZTQZntb84TAg')
            if 'private' in self.chat_type or self.texto.startswith("@NathyRoBot "):
                self.sender.sendSticker('CAADAQADCAADMX7IRXZTQZntb84TAg')
            break
      for c in sorrindo:
          if self.texto.startswith(c) or c in msg.lower():
            msg = CleanReacion(msg)
            enviar = "Sim"
            if "reply_to_message" in self.base:
              if self.base["reply_to_message"]["from"]["id"] == bot["id"]:
                self.sender.sendSticker('CAADAQADDAADMX7IRQIxoXvsblqJAg')
            if 'private' in self.chat_type or self.texto.startswith("@NathyRoBot "):
                self.sender.sendSticker('CAADAQADDAADMX7IRQIxoXvsblqJAg')
            break
      for c in triste:
          if self.texto.startswith(c) or c in msg.lower():
            msg = CleanReacion(msg)
            enviar = "Sim"
            if "reply_to_message" in self.base:
              if self.base["reply_to_message"]["from"]["id"] == bot["id"]:
                self.sender.sendSticker("CAADAQADCQADMX7IRT7bqoWpdIdxAg")
            if 'private' in self.chat_type or self.texto.startswith("@NathyRoBot "):
                 self.sender.sendSticker("CAADAQADCQADMX7IRT7bqoWpdIdxAg")
            break
      for c in olhos_fechados:
          if self.texto.startswith(c) or c in msg.lower():
            msg = CleanReacion(msg)
            enviar = "Sim"
            if "reply_to_message" in self.base:
              if self.base["reply_to_message"]["from"]["id"] == bot["id"]:
                self.sender.sendSticker("CAADAQADCgADMX7IRXMPBWY0cfGvAg")
            if 'private' in self.chat_type or self.texto.startswith("@NathyRoBot "):
                self.sender.sendSticker("CAADAQADCgADMX7IRXMPBWY0cfGvAg")
            break
      Chat(self.sender, self.base, self.chat_type, msg, enviar)
