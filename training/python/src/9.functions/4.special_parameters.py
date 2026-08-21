# =========================================
# 1. Special Parameters
# =========================================
"""
Special parameters let you control how arguments may be passed to a function, using the / and
* markers in the function definition.

Positional or Keyword Arguments:
- If / and * are not present in the function definition, arguments may be passed to a function by position or by keyword.
- If / is present, arguments to the left of / must be passed positionally and cannot be passed by keyword.
- If * is present, arguments to the right of * must be passed by keyword and cannot be passed positionally.
- If both / and * are present, positional arguments must be passed to the left of /, standard arguments may be passed either positionally or by keyword, and keyword-only arguments must be passed to the right of *.

This module covers:
- Positional-only parameters (/)
- Keyword-only parameters (*)
- Combining both
"""

def standard_arg(arg):
    print(arg)

def pos_only_arg(arg, /):
    print(arg)

def kwd_only_arg(*, arg):
    print(arg)

def combined_example(pos_only, /, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)


# =========================================
# 1.1 The No Names Allowed (/)
# =========================================
"""
Arguments to the left of / are positional-only and cannot be passed by keyword.
"""

def pos_only_arg(arg, /):
    print(arg)

pos_only_arg(5)              # Works
pos_only_arg(arg=5)          # Error! (TypeError)


# =========================================
# 1.2 The Names Required (*)
# =========================================
"""
Arguments to the right of * are keyword-only and cannot be passed positionally.
"""

def kwd_only_arg(*, arg):
    print(arg)

kwd_only_arg(arg=5)          # Works
kwd_only_arg(5)              # Error! (TypeError)


# =========================================
# 1.3 Combined Example
# =========================================
"""
Both / and * can be combined to control exactly how each argument must be passed.
"""

def combined_example(pos_only, /, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)


combined_example(1, 2, kwd_only=3)      # Works!
combined_example(1, standard=2, kwd_only=3) # Also works!
combined_example(pos_only=1, standard=2, kwd_only=3)  # Error! (TypeError)
