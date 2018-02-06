from config import *
class control_plugin:
    def __init__(self,sender, base, texto, nome_user, username_user, id_user, input_texto):
        self.sender = sender
        self.base = base
        self.texto = texto
        self.input_texto = input_texto
        self.nome_user = nome_user
        self.username_user = username_user
        self.id_user = id_user
    def control_plugin(self):
        if self.texto.startswith('/debug'):
            self.sender.sendMessage(self.base)
        if self.texto.startswith('/atualizar'):
            self.sender.sendVoice('AwADBAADpDgAAg0YZAfPWtfCBRVyPQI')
            AIAPI.respond('ATUALIZAR_IA_NATHY')
            AIAPI.saveBrain("Cerebro/Memoria/DataBase.brn")
            time.sleep(0.2)
            os.execl(sys.executable, sys.executable, *sys.argv)
        if self.texto.startswith('/run'):
          shell = bash('/run', self.texto)
          if len(shell) == 0:
            shell = 'Ok'
          self.sender.sendMessage("`{}`".format(shell), 'markdown')
        if self.texto.startswith('/git_'):
          shell = bash('/git_', self.texto)
          if len(shell) == 0:
            shell = 'Ok'
          self.sender.sendMessage("`{}`".format(shell), 'markdown')
