from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAlbum(_message.Message):
    __slots__ = ("album_name", "timestamp", "field3", "media_keys", "field7", "device_info")
    class Field4Type(_message.Message):
        __slots__ = ("field1",)
        class Field1Type(_message.Message):
            __slots__ = ("media_key",)
            MEDIA_KEY_FIELD_NUMBER: _ClassVar[int]
            media_key: str
            def __init__(self, media_key: _Optional[str] = ...) -> None: ...
        FIELD1_FIELD_NUMBER: _ClassVar[int]
        field1: CreateAlbum.Field4Type.Field1Type
        def __init__(self, field1: _Optional[_Union[CreateAlbum.Field4Type.Field1Type, _Mapping]] = ...) -> None: ...
    class Field7Type(_message.Message):
        __slots__ = ("field1",)
        FIELD1_FIELD_NUMBER: _ClassVar[int]
        field1: int
        def __init__(self, field1: _Optional[int] = ...) -> None: ...
    class Field8Type(_message.Message):
        __slots__ = ("model", "make", "android_api_version")
        MODEL_FIELD_NUMBER: _ClassVar[int]
        MAKE_FIELD_NUMBER: _ClassVar[int]
        ANDROID_API_VERSION_FIELD_NUMBER: _ClassVar[int]
        model: str
        make: str
        android_api_version: int
        def __init__(self, model: _Optional[str] = ..., make: _Optional[str] = ..., android_api_version: _Optional[int] = ...) -> None: ...
    ALBUM_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FIELD3_FIELD_NUMBER: _ClassVar[int]
    MEDIA_KEYS_FIELD_NUMBER: _ClassVar[int]
    FIELD7_FIELD_NUMBER: _ClassVar[int]
    DEVICE_INFO_FIELD_NUMBER: _ClassVar[int]
    album_name: str
    timestamp: int
    field3: int
    media_keys: _containers.RepeatedCompositeFieldContainer[CreateAlbum.Field4Type]
    field7: CreateAlbum.Field7Type
    device_info: CreateAlbum.Field8Type
    def __init__(self, album_name: _Optional[str] = ..., timestamp: _Optional[int] = ..., field3: _Optional[int] = ..., media_keys: _Optional[_Iterable[_Union[CreateAlbum.Field4Type, _Mapping]]] = ..., field7: _Optional[_Union[CreateAlbum.Field7Type, _Mapping]] = ..., device_info: _Optional[_Union[CreateAlbum.Field8Type, _Mapping]] = ...) -> None: ...
