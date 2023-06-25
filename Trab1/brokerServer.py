from __future__ import annotations

from typing import Callable, TypeAlias
from dataclasses import dataclass

import rpyc # type: ignore

UserId: TypeAlias = str

Topic: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str

FnNotify: TypeAlias = Callable[[list[Content]], None]

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

    def __init__(self, topic_list):
        for topic in topic_list:
            self.create_topic(topic)
    
    def on_connect(self, conn):
        self.conn = conn
    
    def on_disconnect(self, conn):
        BrokerService._online.remove(self.id)
        print(f'Usuário {self.id} desconectou.')

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, topicname: str):
        print(topicname)
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
            return True
        
        self.id = id
        BrokerService._online.add(id)
        BrokerService._callbacks[id] = callback
        
        user_contet_list = BrokerService._queue.pop(id, None)
        # Verifica se tem alguma notificação pendente
        if user_contet_list:
            callback(user_contet_list)
        
        print(f'Usuário {id} conectou.')
        return True

    # Query operations
    @rpyc.exposed
    def list_topics(self) -> list[Topic]:
        return BrokerService._topics

    # Publisher operations
    def send(self, id: UserId, content: Content) -> None:
        """
        Envia a notificação para um usuário
        """
        notify = BrokerService._callbacks[id]
        
        notify([content])

    def pending(self, id: UserId, content: Content) -> None:
        """
        Coloca a notificação na fila
        """
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

        for sub in BrokerService._subscriptions[topic]:
            if sub in BrokerService._online:
                self.send(sub, notification)
            else:
                self.pending(sub, notification)

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

        return True

