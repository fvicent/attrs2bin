# attrs2bin
`attrs2bin` is a Python library that lets you serialize/deserialize your [`attrs`](https://www.attrs.org/en/stable/)-based classes to/from a byte stream. It is compatible with Rust's [`bincode`](https://github.com/servo/bincode), so you can seralize objects in Python, send the resulting byte stream through a socket or any other transport and deserialize it back to a Rust object. It can also deserialize objects from a socket (see below).

# Installation

`attrs2bin` is [hosted on PyPI](https://pypi.org/project/attrs2bin/), to install it just run:

`python -m pip install attrs2bin`

# Example

`attrs2bin` provides just two simple funcions: `serialize()`, which takes an object and returns a byte stream, and `deserialize()`, that takes a byte stream and an `attrs`-based class and returns an object.

```import attr
import attrs2bin

@attr.s(auto_attribs=True)
class Sprite:
    name: str
    x: int
    y: int

my_sprite = Sprite("My sprite", 35, 70)
serialized = attrs2bin.serialize(my_sprite)
deserialized = attrs2bin.deserialize(serialized, Sprite)
assert my_sprite == deserialized
```

# What can be serialized?

Objects of any `attrs`-based class can be serialized, as long as all their fields have a type (using type annotations or `attr.ib(type=...)`). `attrs2bin` ships with serializer for the following types:

* `int`
* `float`
* `bytes`
* `str`
* `bool`

You can create and register your own serializers for specific types by creating a class that implements `attrs2bin.interfaces.ITypeSerializer` and calling `attrs2bin.register_serializer()`.

# Deserializing from a socket

Instead of `deserialize(bytes, cls)`, you can use `deserialize_from_socket(sck, cls)`, which will read the necessary bytes from a socket and return a Python object. `sck` must be any object that implements `attrs2bin.interfaces.IReadableSocket`.

# Rust compatibility

The serializers that ships with `attrs2bin` are all compatible with Rust's [`bincode`](https://github.com/servo/bincode) library. Keep under your pillow the following table in order to create compatible types between Python and Rust:

| Python type                   | Rust type     |
| ---------------------------   |:-------------:|
| `int` / `attrs2bin.SignedInt` | `i64`         |
| `attrs2bin.UnsignedInt`       | `u64`         |
| `float` / `attrs2bin.Float64` | `f64`         |
| `attrs2bin.Float32`           | `f32`         |
| `bytes`                       | `Vec<u8>`     |
| `str`                         | `String`      |
| `bool`                        | `bool`        |