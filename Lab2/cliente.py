#!/usr/bin/python3.8 

from conexao import Conexao

import sys

class Cliente:
    """Componente Cliente - Implementa a interface de usuário e envia requisições para o lado do servidor através do componente Socket."""

    _conn = None
    """Objeto `Conexao` associado ao cliente"""

    def __init__(self, end, porta):
        """Recebe um endereco IP e um numero de porta e instancia um objeto `Cliente`. 

        Args:
            `end` (str): Endereco IP para a conexão do cliente.
            `porta` (int): Porta para a conexão do cliente.
        """
        self._conn = Conexao(end, porta)

    def conecta(self):
        """Tenta se conectar com um servidor através da conexão `_conn`"""
        self._conn.conecta()

    def enviaComando(self, comando):
        """Envia um comando para o servidor.

        Args:
            `comando` (str): Comando que sera enviado para o servidor

        Returns:
            str: Mensagem de resposta recebida do servidor.
        """
        self._conn.enviaMensagem(comando)

        # Aguarda uma resposta do servidor e retorna ela
        resp = self._conn.recebeMensagem()
        return resp

    def enviaRequisicoes(self):
        """Aceita entrada do usuário e envia como requisicao para o servidor.
        Continua aceitando entradas até que o usuário indique para parar o cliente.
        """

        # Loop para enviar requisicoes indeterminadamente
        while True:
            # Pega entrada do usuario
            comando = input("\033[92mC >>\033[0m ")

            # Valida o comando
            result = self.validaComando(comando)

            if result == 'encerra': break # Se o usuario pedir para encerrar o cliente, sai do loop
            elif result != 'valido':
                # Se o comando nao for valido, imprime as
                # instrucoes do comando e recomeca o loop
                print(result)
                continue
            
            # Se o comando e valido, envia para o servidor e aguarda uma resposta
            resp = self.enviaComando(comando)
            if not resp: break # Se a resposta for vazia (o servidor fechou a conexao) sai do loop

            # Imprime a resposta
            print("\033[94mS >>\033[0m " + resp)
        
        # Ao sair do loop, fecha a conexao
        self._conn.fechaConexao()

    def validaComando(self, comando):
        """Valida um comando enviado pelo cliente.

        Args:
            comando (str): O comando enviado pelo cliente.

        Returns:
            str: Retorna uma string dependendo se o comando é válido ou não

                Comando inválido: Retorna uma string indicando como usar o comando corretamente.
                
                Comando 'QUIT': Retorna a string `'encerra'`, indicando que deve encerrar o cliente.
                
                Qualquer outra string: Retorna a string `'valido'`, indicando que o comando pode ser enviado para o servidor.
        """

        # Separa as palavras do comando
        comandos = comando.split(' ')

        # Dependendo de como o comando comeca, retorna uma string diferente
        if comandos[0] == "READ" and len(comandos) < 2:
            return "Uso do comando READ: READ [chave]"
        elif comandos[0] == "WRITE" and len(comandos) < 3:
            return "Uso do comando WRITE: WRITE [chave] [valor]"
        elif comandos[0] == "REMOVE" and len(comandos) < 2:
            return "Uso do comando REMOVE: REMOVE [chave]"
        elif comandos[0] == "QUIT":
            return "encerra" # Indica que o cliente deve ser encerrado
        else:
            return "valido" # Indica que o comando pode ser enviado

    def main(self):
        """Função principal - Inicia a execução padrão do cliente."""
        
        print("\033c", end="") # Limpa o terminal
        
        # Imprime mensagem mostrando que o cliente iniciou e instruções dos comandos
        print("\033[95m================== CLIENTE INICIADO ==================\033[0m")
        print("\033[90mComandos disponíveis: \033[0m")
        print()
        print("\033[33mREAD [chave]          - \033[0mLê uma entrada do dicionário.")
        print("\033[33mWRITE [chave] [valor] - \033[0mEscreve uma nova entrada no dicionário.")
        print("\033[33mREMOVE [chave]        - \033[0mRemove uma entrada do dicionário. \033[91m(Apenas para administrador)\033[0m")
        print("\033[33mQUIT                  - \033[0mEncerra o cliente.")
        print()

        self.conecta() # Se conecta a um servidor
        self.enviaRequisicoes() # Começa a enviar requisições

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
    cli = Cliente(end, porta)
    cli.main()