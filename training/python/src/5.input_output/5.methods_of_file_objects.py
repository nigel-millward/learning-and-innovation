# =========================================
# 1. Methods of File Objects (Detailed)
# =========================================
"""
File objects provide methods for reading, writing, and navigating files.

These examples assume a file object 'f' has already been created.
"""


# =========================================
# 1.1 Reading Data with read()
# =========================================
"""
read(size) reads data from the file.

- If size is omitted or negative → reads entire file
- If size is provided → reads up to that many characters/bytes
- Returns:
    - string (text mode)
    - bytes (binary mode)
"""

# Assume file contains: "This is the entire file.\n"

print(f.read())
# Outputs: 'This is the entire file.\n'

print(f.read())
# Outputs: '' (empty string → end of file reached)


"""
Once the end of the file is reached:
- read() returns an empty string ('')
"""


# =========================================
# 1.2 Reading Single Lines (readline)
# =========================================
"""
readline() reads one line at a time.

- Includes newline '\n'
- Returns '' when end of file is reached
"""

print(f.readline())
# 'This is the first line of the file.\n'

print(f.readline())
# 'Second line of the file\n'

print(f.readline())
# '' (EOF)


"""
Important:
- Blank line → '\n'
- End of file → '' (empty string)
"""


# =========================================
# 1.3 Iterating Over File (Best Practice)
# =========================================
"""
The most efficient way to read lines is to loop over the file.
"""

for line in f:
    print(line, end="")


"""
Advantages:
- Memory efficient
- Simple syntax
- Preferred for large files
"""


# =========================================
# 1.4 Reading All Lines (readlines, list)
# =========================================
"""
You can read all lines into a list.
"""

lines = f.readlines()
# or
lines = list(f)

print(lines)


"""
Each item includes the newline character.
"""


# =========================================
# 1.5 Writing Data (write)
# =========================================
"""
write(string) writes data to the file.

- Returns number of characters written
"""

count = f.write("This is a test\n")

print(count)  # Outputs: 15


# =========================================
# 1.6 Writing Non-String Data
# =========================================
"""
Non-string data must be converted before writing.
"""

value = ("the answer", 42)

s = str(value)   # Convert to string

f.write(s)

# Outputs: 18 (characters written)


# =========================================
# 1.7 File Position (tell)
# =========================================
"""
tell() returns the current position in the file.

- Binary mode → exact byte position
- Text mode → opaque position (do not interpret)
"""

position = f.tell()

print(position)


# =========================================
# 1.8 Moving the File Cursor (seek)
# =========================================
"""
seek(offset, whence) changes the file position.

whence:
- 0 → beginning of file (default)
- 1 → current position
- 2 → end of file
"""

# Example (binary mode)
f = open("workfile", "rb+")

f.write(b"0123456789abcdef")

f.seek(5)        # Move to 6th byte
print(f.read(1))  # Outputs: b'5'

f.seek(-3, 2)     # 3 bytes before end
print(f.read(1))  # Outputs: b'd'


# =========================================
# 1.9 Text Mode Limitations (seek)
# =========================================
"""
In text mode:

- Only seek(0) or positions returned by tell() are safe
- Arbitrary offsets may cause undefined behaviour
- seek(0, 2) (to end) is allowed
"""


# =========================================
# 1.10 End-of-File Behaviour
# =========================================
"""
End-of-file (EOF) conditions:

- read() → returns ''
- readline() → returns ''
- iterator → stops automatically
"""


# =========================================
# 1.11 Additional File Methods
# =========================================
"""
File objects also support less common methods:

- isatty() → True if file is a terminal
- truncate() → resize file
- flush() → force write to disk

These are used in more specialised cases.
"""


# =========================================
# 1.12 Key Idea
# =========================================
"""
File methods allow you to:

- Read data in chunks or lines
- Write and update files
- Control file position precisely

Different use cases require different methods.
"""


# =========================================
# 1.13 Summary
# =========================================
"""
Core file methods:

- read(size) → read data
- readline() → read one line
- readlines() / list(f) → read all lines
- write() → write string
- tell() → get position
- seek() → move position

Key behaviours:
- EOF returns empty string
- seek() behaviour differs in text vs binary mode

Best practices:
- Use iteration for large files
- Convert non-string data before writing
- Be careful with seek() in text mode

Core idea:
"Understand how file data is read, written, and navigated"
"""