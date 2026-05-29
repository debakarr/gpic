from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RemoteMatches(_message.Message):
    __slots__ = ("field1",)
    class Field1Type(_message.Message):
        __slots__ = ("field2",)
        class Field2Type(_message.Message):
            __slots__ = ("field1", "field2")
            class Field1Type(_message.Message):
                __slots__ = ("sha1_hash",)
                SHA1_HASH_FIELD_NUMBER: _ClassVar[int]
                sha1_hash: bytes
                def __init__(self, sha1_hash: _Optional[bytes] = ...) -> None: ...
            class Field2Type(_message.Message):
                __slots__ = ("media_key", "field6")
                class Field6Type(_message.Message):
                    __slots__ = ("media_key", "field2")
                    class Field2Type(_message.Message):
                        __slots__ = ("field1", "field3")
                        FIELD1_FIELD_NUMBER: _ClassVar[int]
                        FIELD3_FIELD_NUMBER: _ClassVar[int]
                        field1: str
                        field3: str
                        def __init__(self, field1: _Optional[str] = ..., field3: _Optional[str] = ...) -> None: ...
                    MEDIA_KEY_FIELD_NUMBER: _ClassVar[int]
                    FIELD2_FIELD_NUMBER: _ClassVar[int]
                    media_key: str
                    field2: RemoteMatches.Field1Type.Field2Type.Field2Type.Field6Type.Field2Type
                    def __init__(self, media_key: _Optional[str] = ..., field2: _Optional[_Union[RemoteMatches.Field1Type.Field2Type.Field2Type.Field6Type.Field2Type, _Mapping]] = ...) -> None: ...
                MEDIA_KEY_FIELD_NUMBER: _ClassVar[int]
                FIELD6_FIELD_NUMBER: _ClassVar[int]
                media_key: str
                field6: RemoteMatches.Field1Type.Field2Type.Field2Type.Field6Type
                def __init__(self, media_key: _Optional[str] = ..., field6: _Optional[_Union[RemoteMatches.Field1Type.Field2Type.Field2Type.Field6Type, _Mapping]] = ...) -> None: ...
            FIELD1_FIELD_NUMBER: _ClassVar[int]
            FIELD2_FIELD_NUMBER: _ClassVar[int]
            field1: RemoteMatches.Field1Type.Field2Type.Field1Type
            field2: RemoteMatches.Field1Type.Field2Type.Field2Type
            def __init__(self, field1: _Optional[_Union[RemoteMatches.Field1Type.Field2Type.Field1Type, _Mapping]] = ..., field2: _Optional[_Union[RemoteMatches.Field1Type.Field2Type.Field2Type, _Mapping]] = ...) -> None: ...
        FIELD2_FIELD_NUMBER: _ClassVar[int]
        field2: RemoteMatches.Field1Type.Field2Type
        def __init__(self, field2: _Optional[_Union[RemoteMatches.Field1Type.Field2Type, _Mapping]] = ...) -> None: ...
    FIELD1_FIELD_NUMBER: _ClassVar[int]
    field1: RemoteMatches.Field1Type
    def __init__(self, field1: _Optional[_Union[RemoteMatches.Field1Type, _Mapping]] = ...) -> None: ...
