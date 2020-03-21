from typing import Any
from zope import interface

from .dequebuffer import DequeBuffer


class ITypeSerializer(interface.Interface):

    def serialize(value: Any) -> bytes:
        """
        Serialize `value` into a byte stream.
        """
    
    def deserialize(stream: DequeBuffer) -> Any:
        """
        Deserialize and return value of a specific type from the `stream`.
        Note that this function will change `stream` in-place.

        Might raise `IncompleteOrCorruptedStreamError`.
        """


class IReadableSocket(interface.Interface):

    def recv(buffersize: int) -> bytes:
        """
        Receive up to `buffersize` bytes from the socket. When no data is
        available, block until at least one byte is available or until the
        remote end is closed. When the remote end is closed and all data is
        read, return the empty string.
        """
