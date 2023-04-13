# Laboratório 1 - Lado Passivo
# Nome: João Pedro Tavares Lima Seda
# DRE: 118161659

import socket

HOST = ''
PORTA = 5000

# Cria o socket
sock = socket.socket() 

# Vincula o host e a porta
sock.bind((HOST, PORTA))
sock.listen(5) 

# Se conecta com o lado ativo
print("Execute o lado ativo para iniciar a conexão")
novoSock, endereco = sock.accept()
print ('Conectado com: ', endereco)

while True:
	# Espera a mensagem do lado ativo
    msg = novoSock.recv(1024)

    # Caso nao receba uma mensagem (conexão finalizada), sai do loop
    if not msg: 
        break 
    else: 
        print("Mensagem recebida:", str(msg,  encoding='utf-8'))
	
    # Envia a mensagem de volta
    novoSock.send(msg) 

# Fecha os sockets da conexao
novoSock.close() 
sock.close() 