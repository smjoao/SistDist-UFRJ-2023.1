import rpyc
from rpyc.utils.server import ForkingServer
from signal import signal, SIGINT, SIG_IGN
from brokerServer import BrokerService

PORT = input("Informe a porta onde este servidor deve escutar (18812): ") or 18812
topic_list = []

while True:
    t = input('Informe os tópicos, aperte \'Enter\' para finalizar (hello): ')
    if t == '':
        t = 'hello'
    break

while True:
    topic_list.append(t)
    t = input()
    if t == '':
        break

broker = BrokerService(topic_list)

# dispara o servidor
srv = ForkingServer(broker, port = PORT)
print('Servidor iniciado. Aperte Ctrl+C a qualquer momento para finalizar...')
srv.start()


