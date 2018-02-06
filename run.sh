#!/usr/bin/env bash
xtitle Nathy
OPC=0
while [ $OPC -ne 5 ];do
  clear;printf "\033[01;36m\n"; figlet Nathy
  printf "\n\033[01;37m############ \033[01;32mMENU\033[01;37m ############"
	printf "\n# \033[01;31m1\033[01;37m - Iniciar no Telegram.   #"
	printf "\n# \033[01;31m2\033[01;37m - Iniciar no Terminal.   #"
	printf "\n# \033[01;31m3\033[01;37m - Sincronizar.           #"
	printf "\n# \033[01;31m4\033[01;37m - Instalar libs.         #"
	printf "\n# \033[01;31m0\033[01;37m - Sair.                  #"
	printf "\n##############################\n"
	echo -n "Digite o número da opção > "
	read OPC
	case $OPC in
		1) clear; python3 main.py;;
		2) clear; python3 cli.py;;
    3) clear; git pull; read -n1 -r -p 'Pressione uma tecla para voltar.';;
		4) clear; sudo apt install tmux; sudo apt install figlet; sudo pip3 install -r requirements.txt; read -n1 -r -p 'Pressione uma tecla para voltar.';;
		0) clear; break;;
		*) printf "\n\033[01;31mOpção Inválida\033[0m";;
	esac
done
