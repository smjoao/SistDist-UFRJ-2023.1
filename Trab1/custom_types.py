from __future__ import annotations

# Se não funcionar no lab rode:
# $ pip install --user typing_extensions
import sys
IS_NEW_PYTHON: bool = sys.version_info >= (3, 8)
if IS_NEW_PYTHON:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from typing import Callable, TYPE_CHECKING, Union
from dataclasses import dataclass

import rpyc

UserId: TypeAlias = str

Topic: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
if IS_NEW_PYTHON:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class Content:
        author: UserId
        topic: Topic
        data: str

    TopicList: TypeAlias = list[Topic]
elif not TYPE_CHECKING:
    @dataclass(frozen=True)
    class Content:
        author: UserId
        topic: Topic
        data: str

    TopicList: TypeAlias = list

if IS_NEW_PYTHON:
    @dataclass(frozen=True, kw_only=True, slots=True)
    class Cookie:
        userId: UserId
        conn: rpyc.core.stream.SocketStream
        bgsrv: rpyc.BgServingThread
        serverName: str
elif not TYPE_CHECKING:
    @dataclass(frozen=True)
    class Cookie:
        userId: UserId
        conn: rpyc.core.stream.SocketStream
        bgsrv: rpyc.BgServingThread
        serverName: str

if IS_NEW_PYTHON:
    FnNotify: TypeAlias = Callable[[list[Content]], None]
elif not TYPE_CHECKING:
    FnNotify: TypeAlias = Callable
