"""Traditionally, a decorator has had to be a named, callable object, usually a function or a class.
PEP 614 allows decorators to be any callable expression.

Most people don’t consider the old decorator syntax to be limiting.
Indeed, loosening up the grammar for decorators mainly helps in a few niche use cases.
According to the PEP, the motivating use case relates to callbacks in GUI frameworks.
"""

# MORE FLEXIBLE DECORATORS
# ===========================
# PyQT uses signals and slots to connect widgets with callbacks.
# Conceptually, you can do something like the following to connect the clicked signal of button to the slot say_hello():
# This will display the text Hello World when you click the button Say hello"
"""
button = QPushButton("Say hello")

@button.clicked.connect
def say_hello():
    message.setText("Hello, World!")
"""


# Now assume that you have several buttons, and to keep track of them, you store them in a dictionary:

"""
buttons = {
  "hello": QPushButton("Say hello"),
  "leave": QPushButton("Goodbye"),
  "calculate": QPushButton("3 + 9 = 12"),
}
"""

#This is all fine. However, it creates a challenge for you if you want to use a decorator to connect a button to a slot. In earlier versions of Python, you couldn’t access items using square brackets when using a decorator. You would need to do something like the following:
"""
hello_button = buttons["hello"]

@hello_button.clicked.connect
def say_hello():
    message.setText("Hello, World!")
"""

#In Python 3.9, these restrictions are lifted and you can now use any expression, including one accessing items in a dictionary:

"""
@buttons["hello"].clicked.connect
def say_hello():
    message.setText("Hello, World!")
"""