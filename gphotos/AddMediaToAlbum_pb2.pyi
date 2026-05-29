from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddMediaToAlbum(_message.Message):
    __slots__ = ("media_keys", "album_media_key", "field5", "device_info", "timestamp")
    class Field5Type(_message.Message):
        __slots__ = ("field1",)
        FIELD1_FIELD_NUMBER: _ClassVar[int]
        field1: int
        def __init__(self, field1: _Optional[int] = ...) -> None: ...
    class Field6Type(_message.Message):
        __slots__ = ("model", "make", "android_api_version")
        MODEL_FIELD_NUMBER: _ClassVar[int]
        MAKE_FIELD_NUMBER: _ClassVar[int]
        ANDROID_API_VERSION_FIELD_NUMBER: _ClassVar[int]
        model: str
        make: str
        android_api_version: int
        def __init__(self, model: _Optional[str] = ..., make: _Optional[str] = ..., android_api_version: _Optional[int] = ...) -> None: ...
    MEDIA_KEYS_FIELD_NUMBER: _ClassVar[int]
    ALBUM_MEDIA_KEY_FIELD_NUMBER: _ClassVar[int]
    FIELD5_FIELD_NUMBER: _ClassVar[int]
    DEVICE_INFO_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    media_keys: _containers.RepeatedScalarFieldContainer[str]
    album_media_key: str
    field5: AddMediaToAlbum.Field5Type
    device_info: AddMediaToAlbum.Field6Type
    timestamp: int
    def __init__(self, media_keys: _Optional[_Iterable[str]] = ..., album_media_key: _Optional[str] = ..., field5: _Optional[_Union[AddMediaToAlbum.Field5Type, _Mapping]] = ..., device_info: _Optional[_Union[AddMediaToAlbum.Field6Type, _Mapping]] = ..., timestamp: _Optional[int] = ...) -> None: ...
