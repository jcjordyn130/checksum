# checksum
A oneshot script to recursively verify two instances of a directory tree written using only Python stdlib.

## Usage
`checksum.py [--checksum checksum] [--verify] [--readsize readsize] [--statsfile statsfile] oldroot newroot`

`--checksum`: The checksum algorithm to use (currently supported: sha256 and sha512) (default: sha256)

`--verify`: Experimental feature to read and compare both files in addition to a checksum, due to implementation this results in a rough doubling of the time required.

`--readsize`: The amount of data (in bytes) to read and process at a time per file, cannot be less than or equal to 2048 bytes. (default: 16MB)

`--statsfile`: The path to the stats file (default: /tmp/checksum.json)

`oldroot`: First instance of the directory structure to compare, the files to compare are taken from this one.

`newroot`: Second instance of the directory structure to compare.