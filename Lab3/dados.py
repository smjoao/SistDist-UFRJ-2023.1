import os
import json
import rpyc
import time

class Dicionario(rpyc.Service):
    """Componente Dicionário - Implementa o acesso, a remoção e a edição do dicionário
    assim como a leitura e escrita do arquivo que armazena o dicionário."""
    
    _DICT_FILE_PATH = ''
    """Caminho para o arquivo que guarda o dicionario"""

    _dict = {}
    """Dicionario que guarda os pares chave-valor."""

    def __init__(self, dict_path):
        """ Recebe um arquivo contendo o dicionario em json
        e inctancia um objeto `Dicionario`. Se o caminho de arquivo
        informado não existir, cria o arquivo.

        Args:
            `dict_path` (str): Caminho para o arquivo contendo o dicionario
        """
        super(Dicionario, self).__init__()
        self._DICT_FILE_PATH = dict_path

        # Marca o tempo inicial (serve para imprimir logs indicando o tempo)
        self._start_time = time.time()

        print("\033c", end="") # Limpa o terminal

        # Imprime mensagem mostrando que o servidor iniciou e instruções dos comandos
        print("\033[95m================== SERVIDOR INICIADO ==================\033[0m")
        print("\033[90mComandos disponíveis: \033[0m")
        print()
        print("\033[33mREAD [chave]          - \033[0mLê uma entrada do dicionário.")
        print("\033[33mWRITE [chave] [valor] - \033[0mEscreve uma nova entrada no dicionário.")
        print("\033[33mREMOVE [chave]        - \033[0mRemove uma entrada do dicionário. \033[91m(Apenas para administrador)\033[0m")
        print("\033[33mQUIT                  - \033[0mEncerra o servido se nenhuma conexão estiver ativa.")
        print()

        # Se o arquivo nao existir, ele chama saveDict, que cria um 
        # arquivo e escreve o dicionario vazio nele
        if not os.path.isfile(self._DICT_FILE_PATH):
            self.saveDict()
            return

        # Se o arquivo existe, le o dicionario dele
        with open(self._DICT_FILE_PATH, 'r') as f:
            self._dict = json.loads(f.read())

    def on_connect(self, conx):
        # Imprime log informando sobre a nova conexão
        self.print_log("Conexão estabelecida com: " + str(conx._channel.stream.sock.getpeername()))

    def on_disconnect(self, conx):
        # Informa que a conexão foi encerrada
        self.print_log("Uma conexão foi encerrada")
    
    def print_log(self, msg):
        """Imprime uma mensagem de log do servidor, indicando o tempo desde que o servidor iniciou.

        Args:
            `msg` (str): Mensagem de log.
        """

        # Calcula o tempo desde que o servidor iniciou usando _start_time
        timestamp = "{:7.2f}".format(time.time() - self._start_time)

        # print("\r\033[K", end="") # Limpa a última linha do terminal (evita que fique um 'S >>' solto no terminal)

        # Imprime o log, indicando o tempo
        print("\033[94m[" + timestamp + "]\033[0m", msg)

        # print("\r\033[92mS >> \033[0m", end="") # Imprime um 'S >>', indicando que o administrador pode enviar um comando

    def saveDict(self):
        """ Salva o dicionario para o arquivo json
        """
        
        # Salva o dicionario inteiro no arquivo em _DICT_FILE_PATH
        with open(self._DICT_FILE_PATH, 'w') as f:
            f.write(json.dumps(self._dict))

    def exposed_getItem(self, key):
        """ Acessa um valor associado a uma chave no dicionario.
        Se a chave não existir no dicionario, retorna uma lista vazia.

        Args:
            `key` (str): Chave a ser acessada no dicionario

        Returns:
            Any: O valor associado a chave `key`
        """
        # Se a chave ja existe no dicionario, retorna o valor
        if key in self._dict:
            self.print_log("getItem(" + key + ") ==> " + str(self._dict[key]))
            return self._dict[key]
        
        # Se a chave nao existe no dicionario, retorna None
        self.print_log("getItem(" + key + ") ==> []")
        return []

    def exposed_setItem(self, key, value):
        """ Adiciona um par chave-valor no dicionario.
        Se a chave já existe no dicionário, concatena 
        o valor novo na lista de valores associados a `key`

        Args:
            `key` (str): A chave do par chave-valor
            `value` (Any): O valor do par chave-valor
        """

        # Se a chave ja existe no dicionario,
        # concatena um valor novo na lista de valores
        if key in self._dict:
            self._dict[key].append(value)
            self._dict[key].sort()
            self.saveDict()
            self.print_log("setItem(" + key + "," + value + ") ==> True")
            return True
        
        # Se a chave nao existe no dicionario, 
        # cria uma lista com um unico valor
        self._dict[key] = [value]
        self.saveDict()
        self.print_log("setItem(" + key + "," + value + ") ==> False")
        return False

    def exposed_removeItem(self, key):
        """ Remove uma entrada do dicionario. Se a entrada 
        com chave `key` existir, remove-a e retorna True, 
        se nao existir, retorna False.

        Args:
            key (str): A chave da entrada que sera removida

        Returns:
            bool: 
                True - A entrada foi removida
                
                False - A entrada com chave `key` nao foi encontrada
        """

        # Se a chave ja existe no dicionario,
        # remove a entrada do dicionario e retorna True
        if key in self._dict:
            self._dict.pop(key)
            self.saveDict()
            self.print_log("removeItem(" + key + ") ==> True")
            return True
        
        # Se a chave nao existe no dicionario, 
        # nao remove nada e retorna False
        self.print_log("removeItem(" + key + ") ==> False")
        return False