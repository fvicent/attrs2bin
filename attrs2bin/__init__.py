from typing import Any
import collections
import struct
import typing

from zope.interface.interfaces import ComponentLookupError
from zope import component  # type: ignore
from zope import interface
import attr

from .exceptions import IncompleteOrCorruptedStreamError
from .exceptions import MissingSerializerError
from .dequebuffer import DequeBuffer
from .interfaces import IReadableSocket, ITypeSerializer
from .serializers import *


SignedInt = int
UnsignedInt = typing.NewType("UnsignedInt", int)
Float64 = float
Float32 = typing.NewType("Float32", float)


def _assert_is_attrs(cls: Any) -> None:
    if not attr.has(cls):
        raise TypeError(f"{cls} is not an attrs class.")


def register_serializer(tp: Any, serializer: ITypeSerializer) -> None:
    component.provideUtility(
        serializer, ITypeSerializer, f"serializer-{tp.__name__}"
    )


def get_serializer(tp: Any) -> ITypeSerializer:
    return component.getUtility(
        ITypeSerializer, f"serializer-{tp.__name__}"
    )


def _try_get_serializer(field: attr.Attribute) -> ITypeSerializer:
    if field.type is None:
        raise ValueError(f"Field «{field.name}» has no type annotation.")
    try:
        return get_serializer(field.type)
    except ComponentLookupError:
        raise MissingSerializerError(
            f"No serializer registered for type {field.type.__name__}"
        )


def serialize(obj: Any) -> bytearray:
    """
    Serialize `obj` into a byte stream.
    """
    cls = type(obj)
    _assert_is_attrs(cls)
    stream = bytearray()
    for field in attr.fields(cls):
        serializer = _try_get_serializer(field)
        stream.extend(serializer.serialize(getattr(obj, field.name)))
    return stream


def deserialize(stream: typing.Union[bytes, bytearray, DequeBuffer],
                cls: Any
                ) -> Any:
    """
    Deserialize the specified byte `stream` into an objet of type `cls`,
    which must be an `attrs` class.

    If `stream` is a `DequeBuffer`, it will be consumed in-place and no
    data duplication will take place at all.
    """
    _assert_is_attrs(cls)
    deserialized_values = []
    if not isinstance(stream, DequeBuffer):
        stream = DequeBuffer(stream)
    for field in attr.fields(cls):
        serializer = _try_get_serializer(field)
        deserialized_values.append(serializer.deserialize(stream))
    return cls(*deserialized_values)


def deserialize_from_socket(sck: IReadableSocket,
                            cls: Any,
                            chunksize: int = 4096) -> Any:
    """
    Like `deserialize()`, but reads the byte stream directly from the 
    specified socket `sck`. `chunksize` is passed directly to `sck.recv()`.
    """
    _assert_is_attrs(cls)
    deserialized_values = []
    stream = DequeBuffer()
    for field in attr.fields(cls):
        serializer = _try_get_serializer(field)
        while True:
            chunk = sck.recv(chunksize)
            if chunk:
                stream.extend(chunk)
            # Only break if the socket is no longer returning data and
            # the stream is empty.
            elif not stream:
                break
            try:
                deserialized_values.append(serializer.deserialize(stream))
            except IncompleteOrCorruptedStreamError as e:
                # Resotre bytes removed from the corrupted stream while trying
                # to deserialize it.
                # Since `extendleft` append items in reverse order, compensate
                # it via `reversed()`.
                stream.extendleft(reversed(e.popped_bytes))
            else:
                break
    return cls(*deserialized_values)


register_serializer(bytes, BytesSerializer())
register_serializer(UnsignedInt, UnsignedIntSerializer())
register_serializer(SignedInt, SignedIntSerializer())
register_serializer(str, StrSerializer())
register_serializer(bool, BoolSerializer())
register_serializer(Float32, Float32Serializer())
register_serializer(Float64, Float64Serializer())
