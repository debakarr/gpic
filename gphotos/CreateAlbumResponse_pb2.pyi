from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAlbumResponse(_message.Message):
    __slots__ = ("field1", "field2")
    class Field1Type(_message.Message):
        __slots__ = ("album_media_key",)
        ALBUM_MEDIA_KEY_FIELD_NUMBER: _ClassVar[int]
        album_media_key: str
        def __init__(self, album_media_key: _Optional[str] = ...) -> None: ...
    FIELD1_FIELD_NUMBER: _ClassVar[int]
    FIELD2_FIELD_NUMBER: _ClassVar[int]
    field1: CreateAlbumResponse.Field1Type
    field2: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, field1: _Optional[_Union[CreateAlbumResponse.Field1Type, _Mapping]] = ..., field2: _Optional[_Iterable[str]] = ...) -> None: ...
