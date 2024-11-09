from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Null(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Request(_message.Message):
    __slots__ = ("torque_profile",)
    TORQUE_PROFILE_FIELD_NUMBER: _ClassVar[int]
    torque_profile: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, torque_profile: _Optional[_Iterable[float]] = ...) -> None: ...
