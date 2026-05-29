from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetUploadToken(_message.Message):
    __slots__ = ("f1", "f2", "f3", "f4", "file_size_bytes")
    F1_FIELD_NUMBER: _ClassVar[int]
    F2_FIELD_NUMBER: _ClassVar[int]
    F3_FIELD_NUMBER: _ClassVar[int]
    F4_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    f1: int
    f2: int
    f3: int
    f4: int
    file_size_bytes: int
    def __init__(self, f1: _Optional[int] = ..., f2: _Optional[int] = ..., f3: _Optional[int] = ..., f4: _Optional[int] = ..., file_size_bytes: _Optional[int] = ...) -> None: ...
