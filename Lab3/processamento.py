import sys
import time
import threading
import rpyc

class Processamento:
    """Componente Processamento - Recebe e processa as requisições do cliente e envia para o servidor."""

    _dict = None
    """Objeto `Dicionario` implementado no servidor, acessado através do RPC"""

    def __init__(self, end, porta):
        """Recebe um endereco IP e um numero de porta e instancia um objeto `Processamento`.

        Args:
            `end` (str): Endereco IP para a conexão com o servidor.
            `porta` (int): Porta para a conexão com o servidor.
        """
        # Inicia a conexão com o servidor
        self._dict = rpyc.connect(end, porta)

    def encerra(self):
        """Finaliza a conexão com o servidor RPC"""

        self._dict.close()

    def enviaComando(self, comando):
        """Processa um comando e envia ao servidor se ele for válido.

        Args:
            comando (str): O comando recebido.

        Returns:
            str: Mensagem de resposta do comando.
        """

        comandos = comando.split(' ') # Separa a string do comando

        # Avalia qual a primeira palavra do comando
        if comandos[0] == "READ":
            # Comando de leitura

            if len(comandos) < 2: # Verifica se o comando foi escrito corretamente
                return "Uso do comando READ: READ [chave]"

            # Le a entrada do dicionario
            value = self.leEntrada(comandos[1])
            return str(value)

        elif comandos[0] == "WRITE":
            # Comando de escrita

            if len(comandos) < 3: # Verifica se o comando foi escrito corretamente
                return "Uso do comando WRITE: WRITE [chave] [valor]"

            # Escreve na entrada do dicionario
            res = self.escreveEntrada(comandos[1], comandos[2])
            return res

        elif comandos[0] == "REMOVE":
            # Comando de remoção

            if len(comandos) < 2: # Verifica se o comando foi escrito corretamente
                return "Uso do comando REMOVE: REMOVE [chave]"

            # Remove a entrada do dicionario
            res = self.removeEntrada(comandos[1])
            return res
        elif comandos[0] == "QUIT":
            # Comando de encerrar

            # Encerra a conexão
            self._dict.close()
            return None

        # Se o comando não for válido, retorna uma mensagem indicando isso
        return "COMANDO '" + comandos[0] + "' INVALIDO"

    def leEntrada(self, key):
        """Busca os valores da entrada `key` do dicionário.

        Args:
            `key` (str): A chave da entrada que será lida.

        Returns:
            List: A lista de valores da entrada.
        """

        val = self._dict.root.getItem(key) # Busca os valores da entrada
        
        # Retorna a lista de valores da entrada
        return val

    def escreveEntrada(self, key, value):
        """Adiciona um novo valor `value` na entrada `key` do dicionário.

        Args:
            `key` (str): A chave da entrada que terá um novo valor adicionado.
            `value` (str): O valor que será adicionado no dicionário.

        Returns:
            str: Mensagem de resposta para a adição da entrada.
        """

        res = self._dict.root.setItem(key, value) # Adiciona um valor novo no dicionario 

        # Retorna uma mensagem diferente dependendo se a entrada já existia no dicionário ou não
        if res:
            return "Valor '" + value + "' adicionado na entrada '" + key + "' do dicionario."
        
        return "Entrada " + str((key,value)) + " adicionada ao dicionario."

    def removeEntrada(self, key):
        """Remove a entrada `key` do dicionário.

        Args:
            `key` (str): A chave da entrada que será removida.

        Returns:
            str: Mensagem de resposta para remoção da entrada.
        """
        
        res = self._dict.root.removeItem(key) # Remove um item do dicionário

        # Retorna uma mensagem diferente dependendo se a entrada já existia no dicionário ou não
        if res:
            return "Entrada '" + key + "' removida do dicionario."
        
        return "Entrada '" + key + "' não encontrada no dicionario."