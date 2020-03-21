from abc import ABCMeta, abstractmethod
from typing import Any
import struct

from zope import interface

from .dequebuffer import DequeBuffer
from .exceptions import IncompleteOrCorruptedStreamError
from .interfaces import ITypeSerializer


__all__ = ["BytesSerializer", "UnsignedIntSerializer", "StrSerializer",
           "BoolSerializer", "SignedIntSerializer", "Float64Serializer",
           "Float32Serializer"]


@interface.implementer(ITypeSerializer)
class BytesSerializer:
    """
    Serializer for the built-in `bytes` type.
    """

    def serialize(self, value: bytes) -> bytes:
        stream = bytearray()
        # The first bytes indicate the length of the value being serialized.
        stream.extend(struct.pack("<Q", len(value)))
        stream.extend(value)
        return stream
    
    def deserialize(self, stream: DequeBuffer) -> bytes:
        popped_bytes = bytearray()
        try:
            popped_bytes.extend(stream.popnleft(struct.calcsize("<Q")))
            (length,) = struct.unpack("<Q", popped_bytes)
            return stream.popnleft(length)
        except (struct.error, IndexError):
            raise IncompleteOrCorruptedStreamError(popped_bytes)


@interface.implementer(ITypeSerializer)
class _AbstractSimpleSerializer(metaclass=ABCMeta):
    """
    Base serializer that just calls `struct.pack()` and `struct.unpack()`
    using the configured `format`.
    """

    @property
    @abstractmethod
    def format(self) -> str:
        """
        Format string to be passed to `struct.pack()` and `unpack()`.
        """

    def serialize(self, value: Any) -> bytes:
        return struct.pack(self.format, value)
    
    def deserialize(self, stream: DequeBuffer) -> Any:
        popped_bytes = bytearray()
        try:
            popped_bytes.extend(stream.popnleft(struct.calcsize(self.format)))
            (value,) = struct.unpack(self.format, popped_bytes)
        except (struct.error, IndexError):
            raise IncompleteOrCorruptedStreamError(popped_bytes)
        return value


@interface.implementer(ITypeSerializer)
class UnsignedIntSerializer(_AbstractSimpleSerializer):
    """
    Serializer for the built-in `int` type (only unsigned values).
    """
    format = "<Q"


@interface.implementer(ITypeSerializer)
class SignedIntSerializer(_AbstractSimpleSerializer):
    """
    Serializer for the built-in `int` type (both signed and unsigned).
    """
    format = "<q"


@interface.implementer(ITypeSerializer)
class Float64Serializer(_AbstractSimpleSerializer):
    """
    Serializer for the built-in `float` type. Works with 64-bit floats.
    """
    format = "d"


@interface.implementer(ITypeSerializer)
class Float32Serializer(_AbstractSimpleSerializer):
    """
    Serializer for the built-in `float` type. Works with 32-bit floats.
    """
    format = "f"


@interface.implementer(ITypeSerializer)
class StrSerializer:
    """
    Serializer for the built-in `str` type. Text is encoded using UTF-8.
    """

    def serialize(self, value: str) -> bytes:
        return BytesSerializer().serialize(value.encode("utf-8"))
    
    def deserialize(self, stream: DequeBuffer) -> str:
        return BytesSerializer().deserialize(stream).decode("utf-8")


@interface.implementer(ITypeSerializer)
class BoolSerializer:
    """
    Serializer for the built-in `bool` type.
    """

    def serialize(self, value: bool) -> bytes:
        return bytes([value])
    
    def deserialize(self, stream: DequeBuffer) -> bool:
        try:
            return bool(stream.popleft())
        except IndexError:
            raise IncompleteOrCorruptedStreamError()
