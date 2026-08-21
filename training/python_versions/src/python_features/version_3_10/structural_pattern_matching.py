# 1. Basics of the match-case syntax
# ================================
# The match keyword is a soft keyword whose expression evaluates to produce a value called the subject.
# The subject is then matched against the pattern of each case clause.
# The case block corresponding to the first match is executed; all subsequent case statements are ignored.
#
# The guard is an optional if condition in a case clause. It’s evaluated after a pattern matches the subject.
# The block of code associated with the case clause will execute only if the guard evaluates to True.
# Otherwise, the next pattern will be compared until there is another match with a guard that evaluates to True
# (if we specified a guard).

"""
match <expression>:
    case <pattern 1> [<if guard>]:
        <block to execute if pattern 1 matches>
    case <pattern n> [<if guard>]:
        <code block to execute if pattern n matches>

"""

# Example match case expression
book_data = ["Structural Pattern Matching", "DrA", 232113]

match book_data:
    case title, author:
        isbn = None
    case title, author, isbn if type(isbn) == 'int':
        pass

# 2. Classes of structural patterns that can be matched
# ============================================================
"""
Literal Patterns
As Patterns
Wildcard Patterns
OR Patterns
Value Patterns
Sequence Patterns
Mapping Patterns
Class Patterns
"""

# Literal pattern
#===================
# Literal patterns are constants (alphabetic, numeric, or boolean) that only match the exact values.
# They include a subject with one of the basic data types (integer, float, string, and Boolean) matched against
# a pattern of the same data type.

# match integer values
import requests

def main(response):
   status_code = response.status_code #200
   match status_code:
       case 200:
           print("The response is OK")
       case 400:
           print("The response is Bad")

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
main(response)

# matching string value
import requests

def main(response):
   encoding = response.encoding
   match encoding:
       case "utf-8":
           print("The encoding is utf-8")
       case "utf-16":
           print("The encoding is utf-16")

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
main(response)

# matching boolean value
import requests

def main(response):
    check = response.ok
    match check:
        case True:
            print("The response is ok")
        case False:
            print("The response is not ok")

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
main(response)

# The OR pattern
# =================
# The OR pattern is specified with a pipe ( | ) character in between the structurally equivalent alternatives.

def main(response):
    encoding = response.encoding
    match encoding:
        case "utf-8" | "utf-16" as encoding:
            print(f"The response was encoded with {encoding} \
           encoding scheme")
        case "base64" | "ascii" as encoding:
            print(f"The response was encoded with {encoding} \
           encoding scheme")
        case _:
            print("No pattern matches the response encoding !")

# As Pattern
# =============
# The As pattern allows us to specify a pattern to match the subject
# or individual elements in a subject against and also a name to bind the value of the subject.

# The As pattern uses the as keyword to bind a variable to the value after the structure of the subject
# matches the pattern.

# Let us modify the snippet above to match the number of elements in the sequence and the data-types of
# the individual elements.


def main(response):
    values = [response.status_code, response.encoding, response.json()]
    match values:
        case [int() as status_code, str() as encoding]:
            print("The first pattern matches the subject")
        case [int() as status_code, str() as encoding, str() as response_data]:
            print("The second pattern matches the subject")
        case [int() as status_code, str() as encoding, dict() as response_data]:
            print("The Third pattern matches the subject")
    print(f"status_code:{status_code}, encoding:{encoding}, response_data:{response_data}")

# when we run the code we'd see the following data
"""
The Third pattern matches the subject
status_code:200, encoding:utf-8, response_data: \
{'userId': 1, 'id': 1, 'title': 'sunt aut facere \
repellat provident occaecati excepturi optio reprehenderit', \
'body': 'quia et suscipit\nsuscipit recusandae consequuntur \
expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum \
rerum est autem sunt rem eveniet architecto'}
"""

# The Matching wildcard pattern
# ===============================
# The wildcard pattern, denoted by an underscore ( _ ) matches any structure but doesn’t bind the value.
# It is often used as a fallback pattern if no pattern matches the structure of the subject. Here’s an example:

def main(response):
   status_code = response.status_code
   match status_code:
       case 300:
           print("The response is 300")
       case 400:
           print("The response is 400")
       case _:
           print("No pattern matches the response status !")



# MATCHING DICTIONARY PATTERNS
# =============================
# You can match a dictionary by key or value

# key
import requests


def main(response):
    post_data = response.json()
    match post_data:
        case {"user_id": 1}:
            print("Pattern 1 matched")
        case {"userId": 1, "postId": 1}:
            print("pattern 2 matched")
        case {"userId": 1, "id": 1}:
            print("pattern 3 matched")
        case _:
            print("No pattern matched")


response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
main(response)

# value
import requests


def main(response):
    post_data = response.json()
    match post_data:
        case {"user_id": 1}:
            print("Pattern 1 matched")
        case {"userId": 1, "postId": 1}:
            print("pattern 2 matched")
        case {"userId": 1, "id": 1}:
            print("pattern 3 matched")
        case _:
            print("No pattern matched")


response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
main(response)

# Matching class pattern
# ======================
class Post:
    def __init__(self, userId, id, title, body):
        self.userId = userId
        self.title = title
        self.body = body
        self.post_id = id


class Post2:
    pass

import requests

def main(response):
    post = Post(**response.json())
    match post:
        case Post2():
            print("Pattern 1")
        case Post():
            print("Pattern 2")
        case _:
            print("No pattern matches the post class !")


response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
main(response)



# The matching sequence pattern
# ===========================
# Sequence patterns are patterns with comma-separated values enclosed within ( … ) or [ … ].
# Depending on whether or not the sequence pattern contains a wildcard,
# it could be a fixed-length or a variable-length sequence pattern.

# The fixed-length sequence pattern has to match the subject length-wise and element-wise.
# The pattern fails if the length of the subject sequence is not equal to the length of the sequence in the pattern.
#
# The variable-length sequence pattern uses the Python iterable packing and unpacking syntax ( the star character * )
# to pack a slice of the sequence into a variable.
# A variable-length sequence can contain at most one starred subpattern.

# As in iterable unpacking, the specification does not distinguish between ‘tuple’ and ‘list’ notation. [1, 2, 3] is equivalent to (1, 2, 3) as well as 1, 2, 3. If we need to match the sequence against its type, we need to wrap the sequence with the data type class: list([1,2,3]) or tuple(1,2,3).
#
# In the context of pattern matching, only the following are recognized as sequences:

"""
array.array
collections.deque
list
memoryview
range
tuple
"""

import requests

def main(response):
   match response.json():
       case [last_post]:
           print(last_post)
       case first_post, *_, last_post:
           print("first_post: ", first_post)
           print("last_post:", last_post)
       case _:
           print("No pattern matches the response status code !")


response = requests.get("https://jsonplaceholder.typicode.com/posts")
main(response)