from dicionario import Dicionario
from conexao import Conexao
from select import select

import sys
import time
import threading

class Servidor:
    """Componente Servidor - Recebe e processa as requisições do cliente e envia respostas com os valores do dicionário. Também implementa uma interface para o administrador do servidor."""

    _conn = None
    """Objeto `Conexao` associado ao servidor"""

    _dict = None
    """Objeto `Dicionario` associado ao servidor"""

    _print_lock = threading.Lock()
    """Lock para as chamadas de print."""

    _dict_lock = threading.Lock()
    """Lock para acesso ao dicionário."""

    def __init__(self, end, porta, dict_path):
        """Recebe uma máscara de endereco IP, um numero de porta e 
        um caminho para um arquivo de dicionário e instancia um objeto `Servidor`.

        Args:
            `end` (str): Uma máscara de endereço IP indicando os endreços aceitos para conexão.
            `porta` (int): A porta onde o servidor receberá conexões.
            `dict_path` (str): Caminho do arquivo que guardará o dicionário.
        """
        # Inicia os componentes Conexão e Dicionário
        self._conn = Conexao(end, porta)
        self._dict = Dicionario(dict_path)

    def inicia(self, n_conexoes):
        """Inicia o servidor, aceitando até `n_conexoes` conexoes.

        Args:
            `n_conexoes` (int): Número máximo de conexões simultâneas no servidor.
        """
        # Inicia a conexão do servidor
        self._conn.iniciaServidor(n_conexoes)

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

    def interpretaComando(self, comando, priv):
        """Interpreta um comando e executa a função apropriada.

        Args:
            comando (str): O comando recebido.
            priv (str): O privilégio de quem enviou o comando:
                'admin' - Administrador
                'cliente' - Cliente

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

            if priv != "admin": # Verifica se quem enviou o comando tem privilegio adequado
                return "Apenas o administrador pode usar este comando!"

            if len(comandos) < 2: # Verifica se o comando foi escrito corretamente
                return "Uso do comando REMOVE: REMOVE [chave]"

            # Remove a entrada do dicionario
            res = self.removeEntrada(comandos[1])
            return res

        # Se o camndo não for válido, retorna uma mensagem indicando isso
        return "COMANDO '" + comandos[0] + "' INVALIDO"
    
    def atendeRequisicoes(self, sock, end):
        """Atende requisições de uma conexão por tempo indeterminado.
        Função que será executada pela thread de cada conexão.

        Args:
            sock (socket): Socket da conexão que atenderá as requisições.
            end (Tuple): Tupla que indica o endereço de IP e a porta do outro lado da conexão.
        """

        # Executa por tempo indeterminado
        while True:
            # Recebe uma requisição do outro lado da conexão
            # Se vier vazio (o outro lado fechou a conexão), sai do loop
            comando = self._conn.recebeMensagem(sock)
            if not comando: break

            # Interpreta o comando da requisição enviada com privilegio de cliente
            resp = self.interpretaComando(comando, 'cliente')
            
            # Envia a resposta do comando
            self._conn.enviaMensagem(resp, sock=sock)

            # Imprime o comando recebido e a resposta enviada
            self.print_log(str(end) + ": " + comando + " --- R: " + resp)
        
        # Ao sair do loop, informa que a conexão foi encerrada e fecha o socket
        self.print_log(str(end) + ": Conexão encerrada")
        self._conn.fechaConexao(sock)

    def encerraServidor(self):
        """Desativa o servidor e salva o dicionário de volta no arquivo."""
        self._conn.fechaConexao()
        self._dict.saveDict()

    def leEntrada(self, key):
        """Busca os valores da entrada `key` do dicionário.

        Args:
            `key` (str): A chave da entrada que será lida.

        Returns:
            List: A lista de valores da entrada.
        """

        self._dict_lock.acquire() # Lock para impedir que as threads mexam no dicionário simultaneamente

        val = self._dict.getItem(key) # Busca os valores da entrada

        self._dict_lock.release() # Libera o lock do dicionário
        
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

        self._dict_lock.acquire() # Lock para impedir que as threads mexam no dicionário simultaneamente

        res = self._dict.setItem(key, value) # Adiciona um valor novo no dicionario 

        self._dict_lock.release() # Libera o lock do dicionário

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

        self._dict_lock.acquire() # Lock para impedir que as threads mexam no dicionário simultaneamente
        
        res = self._dict.removeItem(key) # Remove um item do dicionário

        self._dict_lock.release() # Libera o lock do dicionário
        
        # Retorna uma mensagem diferente dependendo se a entrada já existia no dicionário ou não
        if res:
            return "Entrada '" + key + "' removida do dicionario."
        
        return "Entrada '" + key + "' não encontrada no dicionario."

    def print_log(self, msg):
        """Imprime uma mensagem de log do servidor, indicando o tempo desde que o servidor iniciou.

        Args:
            `msg` (str): Mensagem de log.
        """

        self._print_lock.acquire() # Lock para que threads não imprimam ao mesmo tempo

        # Calcula o tempo desde que o servidor iniciou usando _start_time
        timestamp = "{:7.2f}".format(time.time() - self._start_time)

        print("\r\033[K", end="") # Limpa a última linha do terminal (evita que fique um 'S >>' solto no terminal)

        # Imprime o log, indicando o tempo
        print("\033[94m[" + timestamp + "]\033[0m", msg)

        print("\r\033[92mS >> \033[0m", end="") # Imprime um 'S >>', indicando que o administrador pode enviar um comando
        
        self._print_lock.release() # Libera o lock de impressão

    def handle_sock(self):
        """Função para lidar com nova conexão."""

        sock, end = self._conn.aceitaConexao() # Aceita uma nova conexão

        # Imprime log informando sobre a nova conexão
        self.print_log("Conexão estabelecida com: " + str(end))

        # Cria uma thread para atender as requisições da nova conexão
        cliente = threading.Thread(target=self.atendeRequisicoes, args=[sock, end])
        cliente.start()

    def handle_stdin(self):
        """Função para lidar com nova entrada do usuário.

        Returns:
            bool: 
                True - O usuário não pediu para encerrar o servidor ou ainda há conexões ativas.
                
                False - O usuário pediu para encerrar o servidor e não há conexões ativas.
        """

        comando = input() # Pega entrada do usuário
        
        if comando.split(' ')[0] == 'QUIT': 
            # Se o usuário indicou para encerrar o servidor, verifica se ainda há conexões ativas
            if not self._conn.temConexoes():
                # Indica que o servidor está encerrando
                self.print_log("Encerrando servidor...")
                
                # Apaga a última linha do terminal (evita que fique um 'S >>' solto após a execuçao do programa)
                print("\r\033[K", end="") 

                return False # Caso não existam conexões ativas, retorna False
            
            # Informa que ainda há conexões ativas e retorna True
            self.print_log("Não foi possível encerrar servidor - Ainda há conexões ativas!")
            return True

        # Se o usuário não pediu para encerrar o servidor, 
        # interpreta o comando com privilegio de administrador, 
        # imprime a resposta e retorna True
        resp = self.interpretaComando(comando, 'admin')
        self.print_log(resp)
        return True

    def multiplex(self):
        """Função de multiplexação. Usa o `select` para receber 
        entradas ou de uma nova conexão ou da entrada padrão do usuário.

        Returns:
            bool: 
                True - O usuário não pediu para encerrar o servidor ou ainda há conexões ativas.
                
                False - O usuário pediu para encerrar o servidor e não há conexões ativas.
        """

        # Verifica qual entrada deve ler usando o select
        leitura, _, _ = select([self._conn, sys.stdin], [], [])
        
        # Para cada entrada retornada pelo select, rodar uma função diferente, dependendo da entrada
        for pronto in leitura:
            if pronto == self._conn:
                self.handle_sock() # Função para lidar com nova conexão
            elif pronto == sys.stdin:
                if not self.handle_stdin(): return False # Função para lidar com entrada do usuário
        
        # Se o handle_stdin não retornou False, retorna True
        return True

    def main(self):
        """Função principal - Inicia a execução padrão do cliente."""

        # Inicia o servidor
        self.inicia(5)
        self.print_log("Aguardando conexão...")

        # Roda a função de multiplexação indeterminadamente 
        while self.multiplex(): pass
        
        # Após o loop de multiplexação, encerra o servidor
        self.encerraServidor()

if __name__ == '__main__':
    # Define os parametros padroes
    end = ''
    porta = 5016
    dict_path = 'dict.json'

    # Pega os parametros da linha de comando
    arg_len = len(sys.argv)
    if arg_len >= 2:
        end = sys.argv[1]
    if arg_len >= 3:
        porta = int(sys.argv[2])
    if arg_len >= 4:
        dict_path = sys.argv[3]

    # Executa o servidor
    serv = Servidor(end, porta, dict_path)
    serv.main()