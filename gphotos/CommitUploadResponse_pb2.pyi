from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommitUploadResponse(_message.Message):
    __slots__ = ("field1",)
    class Field1Type(_message.Message):
        __slots__ = ("field1", "field2", "field3", "field5")
        class Field1Type(_message.Message):
            __slots__ = ("field1", "field2")
            FIELD1_FIELD_NUMBER: _ClassVar[int]
            FIELD2_FIELD_NUMBER: _ClassVar[int]
            field1: int
            field2: bytes
            def __init__(self, field1: _Optional[int] = ..., field2: _Optional[bytes] = ...) -> None: ...
        class Field3Type(_message.Message):
            __slots__ = ("media_key",)
            MEDIA_KEY_FIELD_NUMBER: _ClassVar[int]
            media_key: str
            def __init__(self, media_key: _Optional[str] = ...) -> None: ...
        class Field5Type(_message.Message):
            __slots__ = ("field1",)
            FIELD1_FIELD_NUMBER: _ClassVar[int]
            field1: int
            def __init__(self, field1: _Optional[int] = ...) -> None: ...
        FIELD1_FIELD_NUMBER: _ClassVar[int]
        FIELD2_FIELD_NUMBER: _ClassVar[int]
        FIELD3_FIELD_NUMBER: _ClassVar[int]
        FIELD5_FIELD_NUMBER: _ClassVar[int]
        field1: CommitUploadResponse.Field1Type.Field1Type
        field2: int
        field3: CommitUploadResponse.Field1Type.Field3Type
        field5: CommitUploadResponse.Field1Type.Field5Type
        def __init__(self, field1: _Optional[_Union[CommitUploadResponse.Field1Type.Field1Type, _Mapping]] = ..., field2: _Optional[int] = ..., field3: _Optional[_Union[CommitUploadResponse.Field1Type.Field3Type, _Mapping]] = ..., field5: _Optional[_Union[CommitUploadResponse.Field1Type.Field5Type, _Mapping]] = ...) -> None: ...
    FIELD1_FIELD_NUMBER: _ClassVar[int]
    field1: CommitUploadResponse.Field1Type
    def __init__(self, field1: _Optional[_Union[CommitUploadResponse.Field1Type, _Mapping]] = ...) -> None: ...
