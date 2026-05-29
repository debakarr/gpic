from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommitUpload(_message.Message):
    __slots__ = ("field1", "field2", "field3")
    class Field1Type(_message.Message):
        __slots__ = ("field1", "file_name", "sha1_hash", "field4", "quality", "field10", "field17")
        class Field1Type(_message.Message):
            __slots__ = ("field1", "field2")
            FIELD1_FIELD_NUMBER: _ClassVar[int]
            FIELD2_FIELD_NUMBER: _ClassVar[int]
            field1: int
            field2: bytes
            def __init__(self, field1: _Optional[int] = ..., field2: _Optional[bytes] = ...) -> None: ...
        class Field4Type(_message.Message):
            __slots__ = ("file_last_modified_timestamp", "field2")
            FILE_LAST_MODIFIED_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
            FIELD2_FIELD_NUMBER: _ClassVar[int]
            file_last_modified_timestamp: int
            field2: int
            def __init__(self, file_last_modified_timestamp: _Optional[int] = ..., field2: _Optional[int] = ...) -> None: ...
        FIELD1_FIELD_NUMBER: _ClassVar[int]
        FILE_NAME_FIELD_NUMBER: _ClassVar[int]
        SHA1_HASH_FIELD_NUMBER: _ClassVar[int]
        FIELD4_FIELD_NUMBER: _ClassVar[int]
        QUALITY_FIELD_NUMBER: _ClassVar[int]
        FIELD10_FIELD_NUMBER: _ClassVar[int]
        FIELD17_FIELD_NUMBER: _ClassVar[int]
        field1: CommitUpload.Field1Type.Field1Type
        file_name: str
        sha1_hash: bytes
        field4: CommitUpload.Field1Type.Field4Type
        quality: int
        field10: int
        field17: int
        def __init__(self, field1: _Optional[_Union[CommitUpload.Field1Type.Field1Type, _Mapping]] = ..., file_name: _Optional[str] = ..., sha1_hash: _Optional[bytes] = ..., field4: _Optional[_Union[CommitUpload.Field1Type.Field4Type, _Mapping]] = ..., quality: _Optional[int] = ..., field10: _Optional[int] = ..., field17: _Optional[int] = ...) -> None: ...
    class Field2Type(_message.Message):
        __slots__ = ("model", "make", "android_api_version")
        MODEL_FIELD_NUMBER: _ClassVar[int]
        MAKE_FIELD_NUMBER: _ClassVar[int]
        ANDROID_API_VERSION_FIELD_NUMBER: _ClassVar[int]
        model: str
        make: str
        android_api_version: int
        def __init__(self, model: _Optional[str] = ..., make: _Optional[str] = ..., android_api_version: _Optional[int] = ...) -> None: ...
    FIELD1_FIELD_NUMBER: _ClassVar[int]
    FIELD2_FIELD_NUMBER: _ClassVar[int]
    FIELD3_FIELD_NUMBER: _ClassVar[int]
    field1: CommitUpload.Field1Type
    field2: CommitUpload.Field2Type
    field3: bytes
    def __init__(self, field1: _Optional[_Union[CommitUpload.Field1Type, _Mapping]] = ..., field2: _Optional[_Union[CommitUpload.Field2Type, _Mapping]] = ..., field3: _Optional[bytes] = ...) -> None: ...
