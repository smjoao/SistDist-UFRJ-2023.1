import socket

class Conexao:
    """Componente Conexão - Encapsula todo o código para enviar e receber mensagens através de um socket de rede."""

    _ENDERECO = ''
    """Endereco IP para o socket de conexão."""

    _PORTA = 5000
    """Porta do socket de conexão."""

    _main_socket = socket.socket()
    """Socket principal."""

    _conexoes = []
    """Lista de conexoes atualmente ativas."""

    def __init__(self, end, porta):
        """ Recebe um endereco IP e um numero de porta e instancia um objeto `Conexao`. 

        Args:
            `end` (str): Endereco IP para o socket de conexão.
            `porta` (int): Porta para o socket de conexão.
        """

        self._ENDERECO = end
        self._PORTA = porta

    def conecta(self):
        """Tenta se conectar com o endereço `_ENDERECO` na porta `_PORTA`"""

        self._main_socket.connect((self._ENDERECO, self._PORTA))

    def iniciaServidor(self, n_conexoes):
        """Inicia um servidor na porta `_PORTA` que aceita ate `n_conexoes` conexoes.

        Args:
            `n_conexoes` (int): Numero de conexoes que o socket pode aceitar.
        """

        self._main_socket.bind((self._ENDERECO, self._PORTA))
        self._main_socket.listen(n_conexoes)

    def aceitaConexao(self):
        """Aceita uma nova conexão e retorna o socket dela.

        Returns:
            socket: Objeto `socket` da nova conexão.
        """

        sock, end = self._main_socket.accept()
        self._conexoes.append(sock)
        return sock, end

    def recebeMensagem(self, sock=None):
        """Recebe uma nova mensagem da conexão `sock`. Se `sock` não  for informado, usa o `_main_socket`.

        Args:
            `sock` (socket, optional): Conexão que vai receber uma nova mensagem. Se não for informada usa `_main_socket`.

        Returns:
            str: A mensagem recebida. Se a mensagem for vazia (outro lado fechou a conexão) retorna `None`.
        """

        # Se sock for None, usa o _main_socket
        if not sock:
            sock = self._main_socket

        # Pega o tamanho da mensagem lendo os 4 primeiros bytes
        msg_len_raw = sock.recv(4)
        if not msg_len_raw:
            return None

        # Transforma os 4 primeiros bytes em int para saber o tamanho da mensagem
        msg_len = int.from_bytes(msg_len_raw, byteorder='big', signed=False)

        # Recebe a mensagem completa
        msg_raw = sock.recv(msg_len)

        # Transforma a mensagem recebida em string e retorna
        return str(msg_raw,  encoding='utf-8')

    def enviaMensagem(self, msg, sock=None):
        """Envia uma nova mensagem pela conexão `sock`. Se `sock` não  for informado, usa o `_main_socket`.

        Args:
            `msg` (str): A mensagem a ser enviada.
            `sock` (socket, optional): Conexão pela qual vai ser enviada uma nova mensagem. Se não for informada usa `_main_socket`.
        """

        # Se sock for None, usa o _main_socket
        if not sock:
            sock = self._main_socket
        
        # Transforma a string de mensagem em bytearray, colocando o tamanho da mensagem no inicio.
        msg_raw = bytearray(len(msg).to_bytes(4, 'big')) + bytearray(msg, 'utf-8')

        # Envia a mensagem
        sock.send(msg_raw)
    
    def fechaConexao(self, sock=None):
        """Fecha a conexão `sock`. Se `sock` não  for informado, usa o `_main_socket`.

        Args:
            `sock` (socket, optional): Conexão que sera fechada. Se não for informada usa `_main_socket`.
        """

        # Se sock for None, usa o _main_socket
        if not sock:
            sock = self._main_socket
        else:
            # Se sock nao for a conexao principal, remove da lista de conexoes
            self._conexoes.remove(sock)
        
        # Fecha a conexao sock
        sock.close()
    
    def temConexoes(self):
        """Informa se ainda existem conexoes ativas.

        Returns:
            bool: 
                True - Ainda existem conexoes ativas.
                
                False - Não ha nenhuma conexão ativa.
        """

        return len(self._conexoes) > 0

    def fileno(self):
        """Retorna o id do arquivo associado ao socket principal. 
        Esse método foi criado para que a classe `Conexao` seja 
        compatível com a função `select` do python.

        Returns:
            int: Id do arquivo associado ao `_main_socket`.
        """
        return self._main_socket.fileno()