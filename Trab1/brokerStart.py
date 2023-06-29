import rpyc
from rpyc.utils.server import ThreadedServer
from signal import signal, SIGINT, SIG_IGN
from brokerServer import BrokerService

if __name__ == '__main__':
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
    
    print("\033c", end="") # Limpa o terminal
    print('\033[96m\033[1m======================= SERVIDOR IC - UFRJ =======================\033[0m\nAperte Ctrl+C a qualquer momento para finalizar...\n')

    broker = BrokerService(topic_list)

    # dispara o servidor
    srv = ThreadedServer(broker, port = PORT, protocol_config={"allow_public_attrs": True})
    srv.start()


