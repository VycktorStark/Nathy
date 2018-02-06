#!/usr/bin/env python3
from config import *
ru = lambda text: text
AIAPI.bootstrap(brainFile = "Cerebro/Memoria/DataBase.brn")
class Server:
    def about(self):
        self.info = []
        self.info.append('''\033[0;0m\033[02;34m
 _   _       _   _
| \ | | __ _| |_| |__  _   _
|  \| |/ _` | __| '_ \| | | |   \033[0;0m\033[01;0mBy: \033[01;36m{}\033[00;0m\033[02;34m
| |\  | (_| | |_| | | | |_| |   \033[01;0mVersão: \033[02;36m{}\033[02;34m
|_| \_|\__,_|\__|_| |_|\__, |                                   \033[0;36mData: {}\033[02;34m
                       /___/     \033[0;0mÚltima atualização do Cérebro:
                                                                \033[0;36mHora: {}'''.format(lang('create').info(),lang('version').info(), time.strftime('%d/%m/%Y', time.localtime(os.path.getatime("Cerebro/Memoria/DataBase.brn"))), time.strftime('%H:%M:%S', time.localtime(os.path.getatime("Cerebro/Memoria/DataBase.brn")))))
        self.info.append("\n\033[0;0m______________")
        self.info.append('\n\033[0;36mNome: \033[01;0m{}'.format(bot_name))
        self.info.append('\n\033[0;36mUsername: \033[01;0m{}'.format(bot_username))
        self.info.append('\n\033[0;36mID: \033[01;0m{}'.format(bot_id))
        return ru("".join(self.info))

if __name__ == '__main__':
    telepot.DelegatorBot(TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, main, timeout=3600 * 3600),
        pave_event_space()(
            per_callback_query_origin(), create_open, Callback, timeout=3600 * 3600),
    ]).message_loop(run_forever=Server().about())