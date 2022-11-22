# checksum
A oneshot script to recursively verify two instances of a directory tree written using only Python stdlib.

## Usage
`checksum.py [--checksum checksum] [--verify] oldroot newroot`

`--checksum`: The checksum algorithm to use (currently supported: sha256 and sha512) (default: sha256)

`--verify`: Experimental feature to read and compare both files in addition to a checksum, due to implementation this results in a rough doubling of the time required.

`oldroot`: First instance of the directory structure to compare, the files to compare are taken from this one.

`newroot`: Second instance of the directory structure to compare.