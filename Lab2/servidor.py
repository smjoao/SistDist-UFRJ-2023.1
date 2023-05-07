from dicionario import Dicionario
from conexao import Conexao
from select import select

import sys
import time
import threading

class Servidor:

    _print_lock = threading.Lock()
    _dict_lock = threading.Lock()

    def __init__(self, end, porta, dict_path):
        self._conn = Conexao(end, porta)
        self._dict = Dicionario(dict_path)

    def inicia(self):
        self._conn.iniciaServidor(5)
        self._start_time = time.time()

        print("\033c", end="")
        print("\033[95m================== SERVIDOR INICIADO ==================\033[0m")

    def interpretaComando(self, comando, priv):
        comandos = comando.split(' ')

        if comandos[0] == "READ":
            if len(comandos) < 2:
                return "Uso do comando READ: READ [chave]"
            value = self.leEntrada(comandos[1])
            return str(value)
        elif comandos[0] == "WRITE":
            if len(comandos) < 3:
                return "Uso do comando WRITE: WRITE [chave] [valor]"
            res = self.escreveEntrada(comandos[1], comandos[2])
            return res
        elif comandos[0] == "REMOVE":
            if len(comandos) < 2:
                return "Uso do comando REMOVE: REMOVE [chave]"
            if priv != "admin":
                return "Apenas o administrador pode usar este comando!"
            res = self.removeEntrada(comandos[1])
            return res

        return "COMANDO '" + comandos[0] + "' INVALIDO"
    
    def atendeRequisicoes(self, sock, end):
        while True:
            comando = self._conn.recebeMensagem(sock)
            if not comando: break

            resp = self.interpretaComando(comando, 'cliente')
            self.print_log(str(end) + ": " + comando + " --- R: " + resp)
            self._conn.enviaMensagem(resp, sock=sock)
        
        self.print_log(str(end) + ": Conexão encerrada")
        self._conn.fechaConexao(sock)

    def encerraServidor(self):
        self._conn.fechaConexao()
        self._dict.saveDict()

    def leEntrada(self, key):
        self._dict_lock.acquire()
        val = self._dict.getItem(key)
        self._dict_lock.release()
        
        return val

    def escreveEntrada(self, key, value):
        self._dict_lock.acquire()
        res = self._dict.setItem(key, value)
        self._dict_lock.release()

        if res:
            return "Valor '" + value + "' adicionado na entrada '" + key + "' do dicionario."
        
        return "Entrada " + str((key,value)) + " adicionada ao dicionario."

    def removeEntrada(self, key):
        self._dict_lock.acquire()
        res = self._dict.removeItem(key)
        self._dict_lock.release()
        
        if res:
            return "Entrada '" + key + "' removida do dicionario."
        
        return "Entrada '" + key + "' não encontrada no dicionario."

    def print_log(self, msg):
        self._print_lock.acquire()
        timestamp = "{:7.2f}".format(time.time() - self._start_time)
        print("\r\033[K", end="")
        print("\033[94m[" + timestamp + "]\033[0m", msg)
        print("\r\033[92mS >> \033[0m", end="")
        self._print_lock.release()

    def handle_sock(self):
        sock, end = self._conn.aceitaConexao()

        self.print_log("Conexão estabelecida com: " + str(end))
        cliente = threading.Thread(target=self.atendeRequisicoes, args=[sock, end])
        cliente.start()

    def handle_stdin(self):
        comando = input()
        if comando.split(' ')[0] == 'QUIT': 
            if not self._conn.temConexoes():
                self.print_log("Encerrando servidor...")
                print("\r\033[K", end="")
                return False
            self.print_log("Não foi possível encerrar servidor - Ainda há conexões ativas!")
            return True

        resp = self.interpretaComando(comando, 'admin')
        self.print_log(resp)
        return True

    def multiplex_loop(self):
        leitura, _, _ = select([self._conn, sys.stdin], [], [])
        for pronto in leitura:
            if pronto == self._conn:
                self.handle_sock()
            elif pronto == sys.stdin:
                if not self.handle_stdin(): return False
        
        return True

    def main(self):
        serv.inicia()
        self.print_log("Aguardando conexão...")

        while self.multiplex_loop(): pass
            
        self.encerraServidor()

    
serv = Servidor('localhost', 5001, 'dict.json')
serv.main()