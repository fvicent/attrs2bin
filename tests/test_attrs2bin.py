import math

from attrs2bin.dequebuffer import DequeBuffer
from attrs2bin.exceptions import MissingSerializerError
from attrs2bin.interfaces import ITypeSerializer
from attrs2bin.serializers import *
from zope import interface
from zope.interface.verify import verifyObject
import attr
import attrs2bin
import pytest


@attr.s(auto_attribs=True)
class MyClass:
    some_bytes: bytes
    number: attrs2bin.UnsignedInt
    negative_number: int
    text: str
    boolean: bool
    another_boolean: bool
    f64: float


@attr.s(auto_attribs=True)
class MyFloatClass:
    f32: attrs2bin.Float32


INSTANCE = MyClass(
    b"some bytes",
    1234,
    -1234,
    "¡Hello, world! Random greek word: σωφροσῠ́νη",
    True,
    False,
    1.23456789
)
INSTANCE_FLOAT32 = MyFloatClass(1.234)


def test_serialize_and_deserialize():
    serialized = attrs2bin.serialize(INSTANCE)
    assert attrs2bin.deserialize(serialized, MyClass) == INSTANCE


def test_serialize_and_deserialize_float32():
    """
    Floats require a special test because of a little precission is lost
    during serialization of 32-bit floats.
    """
    serialized = attrs2bin.serialize(INSTANCE_FLOAT32)
    deserialized = attrs2bin.deserialize(serialized, MyFloatClass)
    assert math.isclose(deserialized.f32, INSTANCE_FLOAT32.f32, rel_tol=3e-08)


@attr.s(auto_attribs=True)
class MockSocket:
    stream: bytes

    def __attrs_post_init__(self):
        self._buffer = DequeBuffer(self.stream)

    def recv(self, n):
        try:
            return self._buffer.popnleft(n)
        except IndexError:
            return self._buffer.popnleft(len(self._buffer))


def test_deserialize_from_socket():
    serialized = attrs2bin.serialize(INSTANCE)
    for chunksize in (1, 1024):
        deserialized = attrs2bin.deserialize_from_socket(
            MockSocket(serialized),
            MyClass,
            chunksize=chunksize
        )
        assert INSTANCE == deserialized


def test_interfaces():
    serializers = (
        BytesSerializer,
        UnsignedIntSerializer,
        SignedIntSerializer,
        StrSerializer,
        BoolSerializer,
        Float32Serializer,
        Float64Serializer
    )
    for serializer in serializers:
        assert verifyObject(ITypeSerializer, serializer())


def test_rust_compatibility():
    bytes_serialized_by_rust = bytes([
        6, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 210, 4, 0, 0, 0, 0, 0, 0, 46,
        251, 255, 255, 255, 255, 255, 255, 21, 0, 0, 0, 0, 0, 0, 0, 207, 131,
        207, 137, 207, 134, 207, 129, 206, 191, 207, 131, 225, 191, 160, 204,
        129, 206, 189, 206, 183, 1, 0, 122, 0, 139, 252, 250, 33, 9, 64
    ])
    deserialized = attrs2bin.deserialize(bytes_serialized_by_rust, MyClass)
    obj = MyClass(
        bytes([0, 1, 2, 3, 4, 5]),
        1234,
        -1234,
        "σωφροσῠ́νη",
        True,
        False,
        3.141592
    )
    assert deserialized == obj


@attr.s(auto_attribs=True)
class Point3D:
    x: float
    y: float
    z: float


@attr.s(auto_attribs=True)
class Sprite:
    name: str
    position: Point3D


@interface.implementer(ITypeSerializer)
class PointSerializer:

    def __init__(self):
        self._float_serializer = Float64Serializer()

    def serialize(self, point: Point3D) -> bytes:
        return b"".join(
            self._float_serializer.serialize(getattr(point, field))
            for field in "xyz"
        )

    def deserialize(self, stream: DequeBuffer) -> Point3D:
        return Point3D(**{
            field: self._float_serializer.deserialize(stream)
            for field in "xyz"
        })


def test_custom_serializer():
    sprite = Sprite("Test sprite", Point3D(1.8, 3.5, 9.4))
    with pytest.raises(MissingSerializerError):
        attrs2bin.serialize(sprite)
    attrs2bin.register_serializer(Point3D, PointSerializer())
    serialized = attrs2bin.serialize(sprite)
    assert sprite == attrs2bin.deserialize(serialized, Sprite)
