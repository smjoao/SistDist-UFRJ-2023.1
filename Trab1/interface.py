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
    
    # Lista de usuários online
    _online = []

    def on_disconnect(self, conn):
        self._online.remove(self.id)
        print(f'Usuário {self.id} desconectou.')

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: str) -> Topic:

        # Se o tópico não existe, adiciona ele à lista de tópicos e adiciona uma chave na lista de inscrições
        if not topicname in self._topics:
            self._topics.append(topicname)
            self._subscriptions[topicname] = []

        return topicname

    # Handshake
    @rpyc.exposed
    def login(self, id: UserId, callback: FnNotify) -> bool:
        self.id = id
        self.callback = callback
        self._online.append(id)

        # Verifica se tem alguma notificação pendente
        if id in self._queue.keys():
            callback(self._queue[id])
            del self._queue[id]

        return True

    # Query operations
    @rpyc.exposed
    def list_topics(self) -> list[Topic]:
        return self._topics

    # Publisher operations
    @rpyc.exposed
    def publish(self, id: UserId, topic: Topic, data: str) -> bool:
        """
        Função responde se Anúncio conseguiu ser publicado
        """
        assert False, "TO BE IMPLEMENTED"

    # Subscriber operations
    @rpyc.exposed
    def subscribe_to(self, id: UserId, topic: Topic) -> bool:
        """
        Função responde se `id` está inscrito no `topic`
        """
        
        # Se o tópico não existe, retorna False
        if not topic in self._topics:
            return False
        
        # Se o usuário ainda não estiver inscrito, adiciona ele à lista de inscrições do tópico
        if not id in self._subscriptions[topic]:
            self._subscriptions[topic].append(id)

        return True

    @rpyc.exposed
    def unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        """
        Função responde se `id` não está inscrito no `topic`
        """

        # Se o tópico não existe, retorna True
        if not topic in self._topics:
            return True
        
        # Se o usuário estiver inscrito, remove ele da lista de inscrições do tópico
        if id in self._subscriptions[topic]:
            self._subscriptions[topic].remove(id)

        return True
