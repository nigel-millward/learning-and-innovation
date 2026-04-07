# Positional or Keyword Arguments
'''
- If / and * are not present in the function definition, arguments may be passed to a function by position or by keyword.
- If / is present, arguments to the left of / must be passed positionally and cannot be passed by keyword.
- If * is present, arguments to the right of * must be passed by keyword and cannot be passed positionally.
- If both / and * are present, positional arguments must be passed to the left of /, standard arguments may be passed either positionally or by keyword, and keyword-only arguments must be passed to the right of *.
'''

def standard_arg(arg):
    print(arg)

def pos_only_arg(arg, /):
    print(arg)

def kwd_only_arg(*, arg):
    print(arg)

def combined_example(pos_only, /, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)

# 1. The no names allowed (/)
def pos_only_arg(arg, /):
    print(arg)

pos_only_arg(5)              # Works
pos_only_arg(arg=5)          # Error! (TypeError)

# 2. The names required (*)
def kwd_only_arg(*, arg):
    print(arg)

kwd_only_arg(arg=5)          # Works
kwd_only_arg(5)              # Error! (TypeError)

# 3. Combined example
def combined_example(pos_only, /, standard, *, kwd_only):
    print(pos_only, standard, kwd_only)


combined_example(1, 2, kwd_only=3)      # Works!
combined_example(1, standard=2, kwd_only=3) # Also works!
combined_example(pos_only=1, standard=2, kwd_only=3)  # Error! (TypeError)