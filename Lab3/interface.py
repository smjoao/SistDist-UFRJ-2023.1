#!/usr/bin/python3.8 

from processamento import Processamento

import sys

class Interface:
    """Componente Interface - Implementa a interface de usuário e envia requisições para o componente de processamento."""

    def __init__(self, end, porta):
        """Recebe um endereco IP e um numero de porta e instancia um objeto `Interface`. 

        Args:
            `end` (str): Endereco IP para a conexão do cliente.
            `porta` (int): Porta para a conexão do cliente.
        """
        self._proc = Processamento(end, porta)

    def enviaRequisicoes(self):
        """Aceita entrada do usuário e envia para o componente de processamento.
        Continua aceitando entradas até que o usuário indique para parar o cliente.
        """

        # Loop para enviar requisicoes indeterminadamente
        while True:
            # Pega entrada do usuario
            comando = input("\033[92mC >>\033[0m ")

            # Envia o comando para o processamento
            resp = self._proc.enviaComando(comando)

            if not resp: break # Se o usuario pedir para encerrar o cliente, sai do loop

            # Imprime a resposta
            print("\033[94mS >>\033[0m " + resp)
        
        # Ao sair do loop, encerra o componente de processamento
        self._proc.encerra()

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

        self.enviaRequisicoes() # Começa a enviar requisições