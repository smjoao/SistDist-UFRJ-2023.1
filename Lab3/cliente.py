from interface import Interface

import rpyc
import sys

if __name__ == '__main__':
    # Define os parametros padroes    
    end = 'localhost'
    porta = 5016

    # Pega os parametros da linha de comando
    arg_len = len(sys.argv)
    if arg_len >= 2:
        end = sys.argv[1]
    if arg_len >= 3:
        porta = int(sys.argv[2])

    # Executa o cliente
    cli = Interface(end, porta)
    cli.main()