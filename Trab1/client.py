import rpyc
from dataclasses import dataclass
from typing import Callable, TypeAlias

UserId: TypeAlias = str

Topic: TypeAlias = str

@dataclass(frozen=True, kw_only=True, slots=True)
class Cookie:
    userId: UserId
    conn: rpyc.core.stream.SocketStream
    serverName: str
    
@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str

def iniciaConexao(host, port=18812):
    '''Cria um conn RPyC com o servidor informado.
    Saida: conexão criada ou None caso o servidor não esteja disponível'''
    try:
        conn = rpyc.connect(host, port) # conecta-se com o servidor
    except:
        return None
    return conn

def finalizaConexao(cookies):
    for cookie in cookies: cookie.conn.close()

def conecta(host, port):
    conn = iniciaConexao(host, port) 
    if conn is None: # caso não exista o servidor, encerra o cliente
        print('Broker não encontrado :(')
        print('Tente novamente mais tarde ou entre em contato com o administrador do broker.')
        return None
    cookie = realizaLogin(conn)
    return cookie

def recebe_notificacao(msgs: [[list[Content]], None]):
    if not msgs: return
    for msg in msgs:
        print("Mensagem de ", msg.author, " recebida do tópico ", msg.topic)
        print(msg.data)

cookies = [] # lista dos cookies de conexões estabelecidas com os servidores remotos

def realizaLogin(conn):
    userId = input('Informe seu usuário (user): ') or 'user'
    if conn.root.login(userId, recebe_notificacao):
        serverName = input(f'Informe um nome para esse servidor (server{len(cookies)}): ') or f'server{len(cookies)}'
        return Cookie(userId = userId, conn = conn, serverName = serverName)
    print('Não foi possível fazer login, tente novamente mais tarde')
    return None

print('''
Boas Vindas ao Sistema de comunicação IC-UFRJ!
    s - Inscrever-se em tópico
    p - Publicar em um tópico
    l - Listar tópicos disponíveis
    u - Desinscrever-se de tópico
    c - Estabelecer nova conexão
    e - Sair
''')

while True:
    op = input('Informe a opção desejada: ').lower()
    try:
        if op == 'e':
            finalizaConexao(cookies) # encerra as conexões com os servidores remotos
            print('Tchau! Até a próxima!')
            exit()
            
        elif op == 'c':
            host = input('Informe o endereço do servidor (localhost): ') or 'localhost'
            port = input('Informe a porta do servidor (18812): ') or 18812
            cookie = conecta(host, port)
            if cookie is None: continue
            print("conexão estabelecida: ", cookie.conn)
            cookies.append(cookie)
            
        elif op == 's':
            server = input('Informe o servidor no qual deseja se inscrever (todos): ')
            topico = input('Informe o tópico ao qual deseja se inscrever (hello): ') or 'hello'
            for cookie in cookies:
                if cookie.serverName == server or not server:
                    am_I_sub = cookie.conn.root.subscribe_to(cookie.userId, topico)
                    if am_I_sub:
                        print(f"Inscrito ao tópico \'{topico}\' com sucesso em {cookie.serverName}")
                    else:
                        print(f"Não foi possível subescrever-se ao tópico \'{topico}\' em {cookie.serverName}")
                    
        elif op == 'p':
            server = input('Informe o servidor para onde realizar a publicação (todos): ')
            topic = input('Informe o topico da publicação (hello): ') or 'hello'
            data = input('informe o conteúdo da sua publicação (world): ') or 'world'
            for cookie in cookies:
                if cookie.serverName == server or not server:
                    did_it_pub = cookie.conn.root.publish(cookie.userId, topic, data)
                    if did_it_pub:
                        print(f"Publicado com sucesso em {cookie.serverName}")
                    else:
                        print(f"Não foi possível publicar em {cookie.serverName}")
                        
        elif op == 'l':
            server = input('Informe o servidor qual deseja listar os tópicos (todos): ')
            for cookie in cookies:
                if cookie.serverName == server or not server:
                    topic_list = cookie.conn.root.list_topics()
                    print(f'---------------{cookie.serverName}---------------')
                    print(*topic_list, sep='\n')
                    
        elif op == 'u':
            server = input('Informe o servidor no qual deseja se desinscrever (todos): ')
            topico = input('Informe o tópico ao qual deseja se desinscrever: ') or 'hello'
            for cookie in cookies:
                if cookie.serverName == server or not server:
                    am_I_uns = cookie.conn.root.unsubscribe_to(cookie.userId, topico)
                    if am_I_uns:
                        print(f"Desinscrito ao tópico \'{topico}\' com sucesso em {cookie.serverName}")
                    else:
                        print(f"Não foi possível desinscrever-se ao \'{topico}\' tópico em {cookie.serverName}")

        else:
            print('Opção inválida')
    except Exception as e:
        print("Erro:", e)
