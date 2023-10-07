from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Sensor(_message.Message):
    __slots__ = ["id", "type", "temperature", "oven_temperature", "presence", "is_on", "name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    OVEN_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    IS_ON_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    temperature: float
    oven_temperature: float
    presence: bool
    is_on: bool
    name: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., temperature: _Optional[float] = ..., oven_temperature: _Optional[float] = ..., presence: bool = ..., is_on: bool = ..., name: _Optional[str] = ...) -> None: ...

class SensorList(_message.Message):
    __slots__ = ["sensors"]
    SENSORS_FIELD_NUMBER: _ClassVar[int]
    sensors: _containers.RepeatedCompositeFieldContainer[Sensor]
    def __init__(self, sensors: _Optional[_Iterable[_Union[Sensor, _Mapping]]] = ...) -> None: ...

class Device(_message.Message):
    __slots__ = ["id", "type", "temperature", "desired_temperature", "is_on", "name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    DESIRED_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    IS_ON_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: str
    temperature: float
    desired_temperature: float
    is_on: bool
    name: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[str] = ..., temperature: _Optional[float] = ..., desired_temperature: _Optional[float] = ..., is_on: bool = ..., name: _Optional[str] = ...) -> None: ...

class DeviceList(_message.Message):
    __slots__ = ["devices"]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    devices: _containers.RepeatedCompositeFieldContainer[Device]
    def __init__(self, devices: _Optional[_Iterable[_Union[Device, _Mapping]]] = ...) -> None: ...

class Setter(_message.Message):
    __slots__ = ["device_id", "operation_type", "temperature", "desired_temperature", "is_on"]
    class OperationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        SET_TEMPERATURE: _ClassVar[Setter.OperationType]
        SET_DESIRED_TEMPERATURE: _ClassVar[Setter.OperationType]
        TURN_ON_OFF: _ClassVar[Setter.OperationType]
    SET_TEMPERATURE: Setter.OperationType
    SET_DESIRED_TEMPERATURE: Setter.OperationType
    TURN_ON_OFF: Setter.OperationType
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    DESIRED_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    IS_ON_FIELD_NUMBER: _ClassVar[int]
    device_id: str
    operation_type: str
    temperature: float
    desired_temperature: float
    is_on: bool
    def __init__(self, device_id: _Optional[str] = ..., operation_type: _Optional[str] = ..., temperature: _Optional[float] = ..., desired_temperature: _Optional[float] = ..., is_on: bool = ...) -> None: ...
