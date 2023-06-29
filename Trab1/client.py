from custom_types import *
from io import StringIO

user = ''
new_notif = 0
size_to_read = 0

notif_buffer = StringIO()

def iniciaConexao(host, port=18812):
    '''Cria um conn RPyC com o servidor informado.
    Saida: conexão criada ou None caso o servidor não esteja disponível'''
    try:
        conn = rpyc.connect(host, port) # conecta-se com o servidor
    except:
        return None
    return conn

def finalizaConexao(cookies):
    for cookie in cookies: 
        cookie.bgsrv.stop()
        cookie.conn.close()

def conecta(host, port):
    conn = iniciaConexao(host, port) 
    if conn is None: # caso não exista o servidor, encerra o cliente
        print('Broker não encontrado :(')
        print('Tente novamente mais tarde ou entre em contato com o administrador do broker.')
        return None
    cookie = realizaLogin(conn)
    return cookie

def recebe_notificacao(msgs):
    global size_to_read
    global new_notif
    global notif_buffer

    if not msgs: return
    for msg in msgs:
        size_to_read += notif_buffer.write(f"\033[91m[{msg.topic}] \033[96mAutor: {msg.author}\033[0m\n{msg.data}\n\n")
        new_notif += 1

cookies = [] # lista dos cookies de conexões estabelecidas com os servidores remotos

def realizaLogin(conn):
    userId = input('Informe seu usuário (user): ') or 'user'
    if conn.root.login(userId, recebe_notificacao):
        serverName = input(f'Informe um nome para esse servidor (server{len(cookies)}): ') or f'server{len(cookies)}'
        bgsrv = rpyc.BgServingThread(conn) # Cria thread para lidar com chamadas de callbacks
        return Cookie(userId = userId, conn = conn, bgsrv=bgsrv, serverName = serverName)
    conn.close()
    print('Não foi possível fazer login, tente novamente mais tarde')
    return None

def handle_input(op):
    if op == 'e':
        finalizaConexao(cookies) # encerra as conexões com os servidores remotos
        if new_notif != 0:
            read_new_notifs()
        notif_buffer.close()
        print('Tchau! Até a próxima!')
        exit()
        
    elif op == 'c':
        host = input('Informe o endereço do servidor (localhost): ') or 'localhost'
        port = input('Informe a porta do servidor (18812): ') or 18812
        cookie = conecta(host, port)
        if cookie is None: return
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
                print(f'\033[91m---------------{cookie.serverName}---------------\033[0m')
                print(*topic_list, sep='\n')
                print()
                
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
    elif op == 'n':
        read_all_notifs()
    else:
        print('Opção inválida')

def read_new_notifs():
    global size_to_read
    global new_notif
    global notif_buffer

    notif_buffer.seek(notif_buffer.tell() - size_to_read)
    notifications_str = notif_buffer.read()
    print(f"\033[92m{new_notif} novas notificações!\033[0m")
    print(notifications_str, end="")
    new_notif = 0
    size_to_read = 0

def read_all_notifs():
    global size_to_read
    global new_notif
    global notif_buffer

    notif_buffer.seek(0)
    notifications_str = notif_buffer.read()
    if size_to_read != 0: 
        print(f"\033[92m{new_notif} nova(s) notificação(ões)!\033[0m")
    else:
        print()
    print(notifications_str, end="")
    new_notif = 0
    size_to_read = 0

def print_menu():
    print('''\033[96m\033[1m========================== IC - UFRJ ============================\033[0m
        \033[32mBoas Vindas ao Sistema de comunicação IC-UFRJ!\033[0m
            \033[91ms - Inscrever-se em tópico
            p - Publicar em um tópico
            l - Listar tópicos disponíveis
            u - Desinscrever-se de tópico
            n - Ver todas as notificações
            c - Estabelecer nova conexão
            e - Sair\033[0m
        ''')

if __name__ == '__main__':
    print("\033c", end="") # Limpa o terminal
    print_menu()
    while True:
        if new_notif != 0:
            read_new_notifs()
        print('Informe a opção desejada: ', end='')
        op = input().lower()
        print("\033c", end="") # Limpa o terminal
        print_menu()
        try:
            last_response = handle_input(op)
        except Exception as e:
            print("Erro:", e)
