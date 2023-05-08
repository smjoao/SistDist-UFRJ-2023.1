import os
import json

class Dicionario:
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
        self._DICT_FILE_PATH = dict_path

        # Se o arquivo nao existir, ele chama saveDict, que cria um 
        # arquivo e escreve o dicionario vazio nele
        if not os.path.isfile(self._DICT_FILE_PATH):
            self.saveDict()
            return

        # Se o arquivo existe, le o dicionario dele
        with open(self._DICT_FILE_PATH, 'r') as f:
            self._dict = json.loads(f.read())

    def saveDict(self):
        """ Salva o dicionario para o arquivo json
        """
        
        # Salva o dicionario inteiro no arquivo em _DICT_FILE_PATH
        with open(self._DICT_FILE_PATH, 'w') as f:
            f.write(json.dumps(self._dict))

    def getItem(self, key):
        """ Acessa um valor associado a uma chave no dicionario.
        Se a chave não existir no dicionario, retorna uma lista vazia.

        Args:
            `key` (str): Chave a ser acessada no dicionario

        Returns:
            Any: O valor associado a chave `key`
        """
        # Se a chave ja existe no dicionario, retorna o valor
        if key in self._dict:
            return self._dict[key]
        
        # Se a chave nao existe no dicionario, retorna None
        return []

    def setItem(self, key, value):
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
            return True
        
        # Se a chave nao existe no dicionario, 
        # cria uma lista com um unico valor
        self._dict[key] = [value]
        return False

    def removeItem(self, key):
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
            return True
        
        # Se a chave nao existe no dicionario, 
        # nao remove nada e retorna False
        return False