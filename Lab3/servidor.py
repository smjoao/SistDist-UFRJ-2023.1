from dados import Dicionario
from rpyc.utils.server import ThreadedServer

import sys

if __name__ == '__main__':
    # Define os parametros padroes
    porta = 5016
    dict_path = 'dict.json'

    # Pega os parametros da linha de comando
    arg_len = len(sys.argv)
    if arg_len >= 2:
        porta = int(sys.argv[1])
    if arg_len >= 3:
        dict_path = sys.argv[2]

    # Executa o servidor
    serv = ThreadedServer(Dicionario(dict_path), port=porta)
    serv.start()
    