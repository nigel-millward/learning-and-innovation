# =========================================
# 1. Data Compression and Archiving
# =========================================
"""
Python provides built-in modules for compressing, decompressing,
and archiving data.

These modules are useful for:
- Reducing file size
- Transferring data efficiently
- Storing data in portable formats

Common modules include:
- zlib → low-level compression
- gzip, bz2, lzma → compressed file formats
- zipfile → ZIP archives
- tarfile → TAR archives
"""


# =========================================
# 1.1 Basic Compression with zlib
# =========================================
"""
The zlib module provides fast compression for binary data.
"""

import zlib

s = b"witch which has which witches wrist watch"

print(len(s))  # Original size
# Outputs: 41

# Compress data
compressed = zlib.compress(s)

print(len(compressed))  # Compressed size
# Outputs: 37


# =========================================
# 1.2 Decompression
# =========================================
"""
Compressed data can be restored using decompress().
"""

original = zlib.decompress(compressed)

print(original)
# Outputs:
# b'witch which has which witches wrist watch'


# =========================================
# 1.3 Data Integrity (CRC)
# =========================================
"""
zlib can generate a checksum using CRC32.

This helps verify data integrity.
"""

checksum = zlib.crc32(s)

print(checksum)
# Outputs: 226805979


# =========================================
# 1.4 Working with Compressed Files (gzip)
# =========================================
"""
The gzip module works with .gz compressed files.
"""

import gzip

# Write compressed file
with gzip.open("example.txt.gz", "wb") as f:
    f.write(b"Hello compressed world")

# Read compressed file
with gzip.open("example.txt.gz", "rb") as f:
    data = f.read()

print(data)
# Outputs: b'Hello compressed world'


# =========================================
# 1.5 Other Compression Formats
# =========================================
"""
Python also supports:

- bz2 → bzip2 compression (higher compression)
- lzma → LZMA compression (very high compression)
"""

import bz2
import lzma

# Example (bz2)
compressed = bz2.compress(b"example data")
print(bz2.decompress(compressed))

# Example (lzma)
compressed = lzma.compress(b"example data")
print(lzma.decompress(compressed))


# =========================================
# 1.6 Creating ZIP Archives (zipfile)
# =========================================
"""
The zipfile module allows you to create and extract ZIP archives.
"""

import zipfile

# Create archive
with zipfile.ZipFile("archive.zip", "w") as z:
    z.write("example.txt")

# Read archive
with zipfile.ZipFile("archive.zip", "r") as z:
    print(z.namelist())


# =========================================
# 1.7 Working with TAR Archives (tarfile)
# =========================================
"""
The tarfile module works with TAR-based archives.
"""

import tarfile

# Create archive
with tarfile.open("archive.tar", "w") as tar:
    tar.add("example.txt")

# Extract archive
with tarfile.open("archive.tar", "r") as tar:
    tar.extractall()


# =========================================
# 1.8 Choosing a Compression Method
# =========================================
"""
Different tools serve different purposes:

- zlib → fast, low-level compression
- gzip → widely used compressed files (.gz)
- bz2 → better compression, slower
- lzma → highest compression, slower
- zipfile → archive multiple files (portable)
- tarfile → archive files (often combined with compression)
"""


# =========================================
# 1.9 Common Use Cases
# =========================================
"""
Compression and archiving are used for:

- Reducing storage size
- Sending files over networks
- Backups and packaging data
- Log compression
"""


# =========================================
# 1.10 Key Idea
# =========================================
"""
Compression reduces data size, while archiving groups files together.

Python provides tools for:
- Compressing raw data
- Working with compressed file formats
- Creating and extracting archives
"""


# =========================================
# 1.11 Summary
# =========================================
"""
Core tools:

- zlib.compress() / decompress()
- gzip.open() → compressed files
- bz2 / lzma → alternative compression methods
- zipfile → create and read ZIP archives
- tarfile → create and extract TAR archives

Best practices:
- Use gzip/zip for file storage and transfer
- Use zlib for in-memory compression
- Choose compression method based on speed vs size

Core idea:
"Reduce, store, and manage data efficiently"
"""