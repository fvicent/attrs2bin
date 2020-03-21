# attrs2bin
`attrs2bin` is a Python library that lets you serialize/deserialize your [`attrs`](https://www.attrs.org/en/stable/)-based classes to/from a byte stream. It is compatible with Rust's [`bincode`](https://github.com/servo/bincode), so you can seralize objects in Python, send the resulting byte stream through a socket or any other transport and deserialize it back to a Rust object.
