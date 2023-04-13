# Laboratório 1 - Lado Ativo
# Nome: João Pedro Tavares Lima Seda
# DRE: 118161659

import socket

HOST = 'localhost'
PORTA = 5000

# Cria o socket
sock = socket.socket()

# Se conecta com o lado passivo
sock.connect((HOST, PORTA)) 

while True:
    # Pega o input do usuario
    print("Digite uma mensagem para enviar ao lado passivo (Digite 'fim' para finalizar a conexão):")
    msg_in = input()

    # Caso o usuário tenha digitado 'fim', sai do loop
    if msg_in == "fim":
        break

    # Envia a mensagem para o lado passivo
    sock.send(bytearray(msg_in, 'utf-8'))

    # Recebe a mensagem de volta
    msg_out = sock.recv(1024)
    print("Mensagem recebida:", str(msg_out,  encoding='utf-8'))


# Finaliza a conexão
sock.close() 