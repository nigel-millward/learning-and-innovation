# =========================================
# 1. Internet Access
# =========================================
"""
Python provides modules for working with internet resources and protocols.

Common use cases:
- Downloading data from websites
- Interacting with web APIs
- Sending emails

Two useful standard modules:
- urllib.request → retrieve data from URLs
- smtplib → send emails
"""


# =========================================
# 1.1 Retrieving Data from URLs (urllib)
# =========================================
"""
The urllib.request module allows you to open and read data from a URL.
"""

from urllib.request import urlopen

with urlopen("https://docs.python.org/3/") as response:
    for line in response:
        line = line.decode()  # Convert bytes to string
        if "updated" in line:
            print(line.rstrip())  # Remove newline


"""
Key steps:
- urlopen() → opens a network connection
- response → iterable of byte lines
- decode() → converts bytes to string
"""


# =========================================
# 1.2 Understanding Byte Data
# =========================================
"""
Data from the internet is returned as bytes.

You must convert it to a string using decode().
"""

with urlopen("https://example.com") as response:
    data = response.read()

print(type(data))        # <class 'bytes'>
print(data.decode())     # Convert to string


# =========================================
# 1.3 Reading Full Response vs Line-by-Line
# =========================================
"""
Two approaches for reading data:

- response.read() → entire content
- iteration → line by line
"""

# Full content
# content = response.read()

# Line-by-line (more memory efficient)
# for line in response:
#     ...


# =========================================
# 1.4 Sending Emails (smtplib)
# =========================================
"""
The smtplib module allows you to send emails using SMTP.
"""

import smtplib

server = smtplib.SMTP("localhost")

server.sendmail(
    "soothsayer@example.org",
    "jcaesar@example.org",
    """To: jcaesar@example.org
From: soothsayer@example.org

Beware the Ides of March.
"""
)

server.quit()


"""
Note:
- Requires a mail server running (e.g. localhost SMTP server)
"""


# =========================================
# 1.5 Email Structure
# =========================================
"""
Basic email format includes:

- To: recipient
- From: sender
- Body: message content

All are included in the message string.
"""


# =========================================
# 1.6 Common Use Cases
# =========================================
"""
Internet modules are used for:

- Downloading web pages
- Accessing APIs
- Sending automated emails
- Data collection (web scraping)
"""


# =========================================
# 1.7 Limitations and Notes
# =========================================
"""
- urllib is simple but limited for complex HTTP tasks
- smtplib requires access to an SMTP server
- Data from URLs is always returned as bytes
"""

# For advanced usage, external libraries are often used:
# - requests (HTTP requests)
# - aiohttp (async HTTP)


# =========================================
# 1.8 Key Idea
# =========================================
"""
Python allows interaction with network resources:

- urllib → fetch data from the internet
- smtplib → send email messages

Data is transferred as bytes and must be decoded when needed.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Core tools:

- urlopen(url) → access web data
- response.read() → read content
- decode() → convert bytes to string
- smtplib.SMTP → send emails

Best practices:
- Use 'with' to manage connections
- Decode response data properly
- Ensure SMTP servers are available

Core idea:
"Fetch and send data over networks using built-in Python tools"
"""