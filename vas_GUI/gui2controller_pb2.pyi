from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Null(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class data_stream(_message.Message):
    __slots__ = ("time", "current_torque_selected", "adjusted_slider_btn", "adjusted_slider_value", "confirm_btn_pressed")
    TIME_FIELD_NUMBER: _ClassVar[int]
    CURRENT_TORQUE_SELECTED_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_SLIDER_BTN_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_SLIDER_VALUE_FIELD_NUMBER: _ClassVar[int]
    CONFIRM_BTN_PRESSED_FIELD_NUMBER: _ClassVar[int]
    time: float
    current_torque_selected: float
    adjusted_slider_btn: str
    adjusted_slider_value: float
    confirm_btn_pressed: str
    def __init__(self, time: _Optional[float] = ..., current_torque_selected: _Optional[float] = ..., adjusted_slider_btn: _Optional[str] = ..., adjusted_slider_value: _Optional[float] = ..., confirm_btn_pressed: _Optional[str] = ...) -> None: ...
