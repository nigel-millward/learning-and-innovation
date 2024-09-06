"""
One of the coolest features of Python 3.9 is one that you won’t notice in your daily coding life.
A fundamental component of the Python interpreter is the parser.
In the latest version, the parser has been reimplemented.

Since its inception, Python has used a basic LL(1) parser to parse source code into parse trees.
You can think of an LL(1) parser as one that reads one character at a time
and figures out how to interpret the source code without backtracking.

One advantage of using a simple parser is that it’s fairly straightforward to implement and reason about.
A disadvantage is that there are hard cases that you need to circumvent with special hacks.

In a series of blog posts, Guido van Rossum—Python’s creator—investigated PEG (parsing expression grammar) parsers.
PEG parsers are more powerful than LL(1) parsers and avoid the need for special hacks. As a result of Guido’s research,
a PEG parser was implemented in Python 3.9. See PEP 617 for more details.

The goal is for the new PEG parser to produce the same abstract syntax tree (AST) as the old LL(1) parser.
"""