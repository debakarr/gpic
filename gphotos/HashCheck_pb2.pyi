from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HashCheck(_message.Message):
    __slots__ = ("field1",)
    class Field1Type(_message.Message):
        __slots__ = ("field1", "field2")
        class Field1Type(_message.Message):
            __slots__ = ("sha1_hash",)
            SHA1_HASH_FIELD_NUMBER: _ClassVar[int]
            sha1_hash: bytes
            def __init__(self, sha1_hash: _Optional[bytes] = ...) -> None: ...
        class Field2Type(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        FIELD1_FIELD_NUMBER: _ClassVar[int]
        FIELD2_FIELD_NUMBER: _ClassVar[int]
        field1: HashCheck.Field1Type.Field1Type
        field2: HashCheck.Field1Type.Field2Type
        def __init__(self, field1: _Optional[_Union[HashCheck.Field1Type.Field1Type, _Mapping]] = ..., field2: _Optional[_Union[HashCheck.Field1Type.Field2Type, _Mapping]] = ...) -> None: ...
    FIELD1_FIELD_NUMBER: _ClassVar[int]
    field1: HashCheck.Field1Type
    def __init__(self, field1: _Optional[_Union[HashCheck.Field1Type, _Mapping]] = ...) -> None: ...
