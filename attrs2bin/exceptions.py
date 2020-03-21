from typing import Optional, Union


__all__ = ["MissingSerializerError", "IncompleteOrCorruptedStreamError"]


class MissingSerializerError(Exception):
    """
    Raised when trying to serialize a value whose type is not registered
    with a serializer.
    """


class IncompleteOrCorruptedStreamError(Exception):
    """
    Raised when trying to deserialize a value from a stream, but the stream
    is incomplete or corrupted.
    """
    
    def __init__(self, popped_bytes: Optional[Union[bytes, bytearray]] = None):
        self.popped_bytes = popped_bytes or bytes()
