from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CommitToken(_message.Message):
    __slots__ = ("field1", "field2")
    FIELD1_FIELD_NUMBER: _ClassVar[int]
    FIELD2_FIELD_NUMBER: _ClassVar[int]
    field1: int
    field2: bytes
    def __init__(self, field1: _Optional[int] = ..., field2: _Optional[bytes] = ...) -> None: ...
