# f-strings were introduced in Python 3.6, and have become very popular.
# They might be the most common reason for Python libraries only being supported on version 3.6 and later.
# An f-string is a formatted string literal. You can recognize it by the leading f:
style = "formatted"
f"This is a {style} string"

# However, the real f-news in Python 3.8 is the new debugging specifier.
# You can now add = at the end of an expression, and it will print both the expression and its value:

# 3.7
python = 3.7
f"python={python}"
'python=3.7'

# 3.8
python = 3.8
f"{python=}"
'python=3.8'




