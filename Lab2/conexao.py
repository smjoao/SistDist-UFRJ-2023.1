import socket

class Conexao:
    
    _ENDERECO = ''
    _PORTA = 5000
    _main_socket = socket.socket()

    _conexoes = []

    def __init__(self, end, porta):
        self._ENDERECO = end
        self._PORTA = porta

        # self._socket = socket.socket()

    def conecta(self):
        self._main_socket.connect((self._ENDERECO, self._PORTA))

    def iniciaServidor(self, n_conexoes):
        self._main_socket.bind((self._ENDERECO, self._PORTA))
        self._main_socket.listen(n_conexoes)

    def aceitaConexao(self):
        sock, end = self._main_socket.accept()
        self._conexoes.append(sock)
        return sock, end

    def recebeMensagem(self, sock=None):
        if not sock:
            sock = self._main_socket

        msg_len_raw = sock.recv(4)
        if not msg_len_raw:
            return None

        msg_len = int.from_bytes(msg_len_raw, byteorder='big', signed=False)
        msg_raw = sock.recv(msg_len)

        return str(msg_raw,  encoding='utf-8')

    def enviaMensagem(self, msg, sock=None):
        if not sock:
            sock = self._main_socket
        
        msg_raw = bytearray(len(msg).to_bytes(4, 'big')) + bytearray(msg, 'utf-8')

        sock.send(msg_raw)
    
    def fechaConexao(self, sock=None):
        if not sock:
            sock = self._main_socket
        else:
            self._conexoes.remove(sock)
        
        sock.close()
    
    def temConexoes(self):
        return len(self._conexoes) > 0

    def fileno(self):
        return self._main_socket.fileno()