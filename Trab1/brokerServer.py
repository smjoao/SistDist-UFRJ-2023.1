from custom_types import *
import time
@rpyc.service
class BrokerService(rpyc.Service): # type: ignore

    # Lista de tópicos
    _topics = []

    # Dict onde as chaves são os tópicos e os valores são informações do usuário
    _subscriptions = {}

    # Dict com as notificações pendentes. A chave é o usuário e o valor é uma lista de Content
    _queue = {}
    
    # Lista sem repetição de usuários online
    _online = set()

    # Callbacks dos usuarios. Chave é o usuário e o valor é a referência da função
    _callbacks = {}


    _start_time = 0.

    def initialize(topic_list):
        
        # Marca o tempo inicial (serve para imprimir logs indicando o tempo)
        BrokerService._start_time = time.time()

        for topic in topic_list:
            BrokerService.create_topic(topic)
    
    def print_log(*msg):
        # Calcula o tempo desde que o servidor iniciou usando _start_time
        timestamp = "{:7.2f}".format(time.time() - BrokerService._start_time)

        print('\033[32m[' + timestamp + ']\033[0m', *msg, flush=True)

    def on_connect(self, conn):
        self.conn = conn
    
    def on_disconnect(self, conn):
        if getattr(self, 'id', None):
            BrokerService._online.remove(self.id)
            BrokerService.print_log(f'Usuário {self.id} desconectou.')
        else:
            BrokerService.print_log(f'Usuário ???? desconectou. Algo de errado não está certo.')

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(topicname: str):
        BrokerService.print_log("Tópico", topicname, "adicionado!")
        # Se o tópico não existe, adiciona ele à lista de tópicos e adiciona uma chave na lista de inscrições
        if not topicname in BrokerService._topics:
            BrokerService._topics.append(topicname)
            BrokerService._subscriptions[topicname] = []

        return topicname

    # Handshake
    @rpyc.exposed
    def login(self, id: UserId, callback: FnNotify) -> bool:
        # Verifica se esse id já está logado
        if id in BrokerService._online:
            return False
        
        self.id = id
        BrokerService._online.add(id)
        BrokerService._callbacks[id] = rpyc.async_(callback)
        
        user_contet_list = BrokerService._queue.pop(id, None)
        # Verifica se tem alguma notificação pendente
        if user_contet_list:
            callback(user_contet_list)
        
        BrokerService.print_log(f'Usuário {id} conectou.')
        return True

    # Query operations
    @rpyc.exposed
    def list_topics(self) -> TopicList:
        return BrokerService._topics

    # Publisher operations
    def send(id: UserId, content: Content) -> None:
        """
        Envia a notificação para um usuário
        """
        BrokerService.print_log(f'Enviando publicação para {id}!')

        notify = BrokerService._callbacks[id]
        
        notify([content])

    def pending(id: UserId, content: Content) -> None:
        """
        Coloca a notificação na fila
        """

        BrokerService.print_log(f'Enfileirando publicação para {id}!')

        if id in BrokerService._queue.keys():
            BrokerService._queue[id].append(content)

        else:
            BrokerService._queue[id] = [content]

    @rpyc.exposed
    def publish(self, id: UserId, topic: Topic, data: str) -> bool:
        """
        Função responde se Anúncio conseguiu ser publicado
        """
        if not topic in BrokerService._topics:
            return False

        notification = Content(author=id, topic=topic, data=data)

        BrokerService.print_log(f'Nova publicação de {id} para o tópico {topic}!')

        for sub in BrokerService._subscriptions[topic]:
            if sub in BrokerService._online:
                BrokerService.send(sub, notification)
            else:
                BrokerService.pending(sub, notification)

        return True

    # Subscriber operations
    @rpyc.exposed
    def subscribe_to(self, id: UserId, topic: Topic) -> bool:
        """
        Função responde se `id` está inscrito no `topic`
        """
        
        # Se o tópico não existe, retorna False
        if not topic in BrokerService._topics:
            return False
        
        # Se o usuário ainda não estiver inscrito, adiciona ele à lista de inscrições do tópico
        if not id in BrokerService._subscriptions[topic]:
            BrokerService._subscriptions[topic].append(id)

        BrokerService.print_log(f'Usuário {id} se inscreveu no tópico {topic}!')
        return True

    @rpyc.exposed
    def unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        """
        Função responde se `id` não está inscrito no `topic`
        """

        # Se o tópico não existe, retorna True
        if not topic in BrokerService._topics:
            return True
        
        # Se o usuário estiver inscrito, remove ele da lista de inscrições do tópico
        if id in BrokerService._subscriptions[topic]:
            BrokerService._subscriptions[topic].remove(id)
            BrokerService.print_log(f'Usuário {id} se desinscreveu no tópico {topic}!')

        return True

