from conexao import Conexao

class Cliente:

    def __init__(self, end, porta):
        self._conn = Conexao(end, porta)

    def conecta(self):
        self._conn.conecta()

    def enviaComando(self, comando):
        self._conn.enviaMensagem(comando)

        resp = self._conn.recebeMensagem()
        return resp

    def enviaRequisicoes(self):
        while True:
            comando = input("\033[92mC >>\033[0m ")

            result = self.validaComando(comando)
            if result == 'encerra': break
            elif result != 'valido':
                print(result)
                continue

            resp = self.enviaComando(comando)
            if not resp: break

            print("\033[94mS >>\033[0m " + resp)
        
        self._conn.fechaConexao()

    def validaComando(self, comando):
        comandos = comando.split(' ')

        if comandos[0] == "READ" and len(comandos) < 2:
            return "Uso do comando READ: READ [chave]"
        elif comandos[0] == "WRITE" and len(comandos) < 3:
            return "Uso do comando WRITE: WRITE [chave] [valor]"
        elif comandos[0] == "REMOVE" and len(comandos) < 2:
            return "Uso do comando REMOVE: REMOVE [chave]"
        elif comandos[0] == "QUIT":
            return "encerra"
        else:
            return "valido"

    def main(self):
        print("\033c", end="")
        self.conecta()
        self.enviaRequisicoes()
        

cli = Cliente('localhost', 5001)
cli.main()