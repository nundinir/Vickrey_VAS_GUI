from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Null(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Input(_message.Message):
    __slots__ = ("torque",)
    TORQUE_FIELD_NUMBER: _ClassVar[int]
    torque: float
    def __init__(self, torque: _Optional[float] = ...) -> None: ...
