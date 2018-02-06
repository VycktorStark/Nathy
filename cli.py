# encoding=utf8
from Cerebro import Neuronio
import os, time, socket, sys
kernel = Neuronio.Kernel()
sessionId = 1234549
kernel.bootstrap(brainFile = "Cerebro/Memoria/DataBase.brn")

def main():
  while True:
    message = input("Digite: ")
    if (message == "quit"):
      kernel.respond("LOAD")
      kernel.saveBrain("Cerebro/Memoria/DataBase.brn")
      exit()
    else:
      bot_response = kernel.respond(message, sessionId)
      print("Bot: %s" % bot_response)
if __name__ == "__main__":
  main()