# =========================================
# 1. Saving Structured Data with JSON
# =========================================
"""
Saving simple data like strings is straightforward.

However, more complex data (lists, dictionaries, nested structures)
requires a structured format.

Python provides the json module for this purpose.
"""


# =========================================
# 1.1 What is JSON?
# =========================================
"""
JSON (JavaScript Object Notation) is a standard format for data exchange.

It is:
- Human-readable
- Language-independent
- Widely used in APIs and applications

Python can convert its data structures into JSON format.
"""


# =========================================
# 1.2 Serializing Data (dumps)
# =========================================
"""
Serializing means converting Python objects into a JSON string.
"""

import json

x = [1, "simple", "list"]

json_str = json.dumps(x)

print(json_str)
# Outputs: [1, "simple", "list"]


"""
Common serializable types:
- lists
- dictionaries
- strings
- numbers
- booleans
- None
"""


# =========================================
# 1.3 Writing JSON to a File (dump)
# =========================================
"""
Use json.dump() to write JSON data directly to a file.
"""

data = {
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "SQL"]
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f)


"""
Best practice:
- Always use encoding="utf-8"
"""


# =========================================
# 1.4 Deserializing Data (loads)
# =========================================
"""
Deserializing means converting a JSON string back into Python objects.
"""

json_str = '{"name": "Alice", "age": 30}'

data = json.loads(json_str)

print(data)
# Outputs: {'name': 'Alice', 'age': 30}


# =========================================
# 1.5 Reading JSON from a File (load)
# =========================================
"""
Use json.load() to read JSON data from a file.
"""

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

print(data)


# =========================================
# 1.6 JSON and File Encoding
# =========================================
"""
JSON files must use UTF-8 encoding.

Always specify encoding="utf-8" when reading and writing.
"""


# =========================================
# 1.7 Limitations of JSON
# =========================================
"""
JSON supports basic data types only.

It does NOT directly support:
- Custom class instances
- Complex Python objects

Additional work is needed to serialize such objects.
"""


# =========================================
# 1.8 JSON vs Pickle
# =========================================
"""
Python also provides the pickle module.

Key differences:

JSON:
- Language-independent
- Safe for data exchange
- Limited to basic types

pickle:
- Python-specific
- Can serialize complex objects
- Not safe for untrusted data
"""


# =========================================
# 1.9 When to Use JSON
# =========================================
"""
Use JSON when:
- Sharing data between systems
- Storing configuration files
- Working with APIs
- Saving structured data safely
"""


# =========================================
# 1.10 Key Idea
# =========================================
"""
JSON allows you to:

- Convert Python data into text form (serialization)
- Restore it later (deserialization)
- Store and transmit structured data easily
"""


# =========================================
# 1.11 Summary
# =========================================
"""
Core JSON functions:

- json.dumps(obj) → object → string
- json.dump(obj, file) → object → file
- json.loads(str) → string → object
- json.load(file) → file → object

Best practices:
- Use UTF-8 encoding
- Prefer JSON for interoperability
- Use pickle only for trusted Python-only use cases

Core idea:
"Store and exchange structured data safely and consistently"
"""