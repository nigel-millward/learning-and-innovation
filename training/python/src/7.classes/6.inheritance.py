# =========================================
# 1. Inheritance: The Basics
# =========================================
"""
Inheritance allows one class (child) to reuse the behaviour of another class (parent).

This helps to:
- Reduce code duplication
- Organise related classes
- Build more complex systems from simpler ones

The child class automatically gains access to the parent's attributes and methods.
"""


# =========================================
# 1.1 Basic Inheritance Syntax
# =========================================
"""
To create a child class, pass the parent class name in parentheses.
"""

class Animal:
    def speak(self):
        return "Some generic sound"

# Dog inherits from Animal
class Dog(Animal):
    pass

d = Dog()

print(d.speak())  # Outputs: Some generic sound


# =========================================
# 1.2 Adding New Behaviour (Extending)
# =========================================
"""
A child class can define its own methods in addition to inherited ones.
"""

class Animal:
    def speak(self):
        return "Some generic sound"

class Dog(Animal):
    def wag_tail(self):
        return "Tail wagging"

d = Dog()

print(d.speak())     # Inherited → Some generic sound
print(d.wag_tail())  # New → Tail wagging


# =========================================
# 1.3 Overriding Parent Methods
# =========================================
"""
A child class can replace a method from the parent class.

This is called method overriding.
"""

class Animal:
    def speak(self):
        return "Some generic sound"

class Dog(Animal):
    def speak(self):
        return "Bark"

class Cat(Animal):
    def speak(self):
        return "Meow"

d = Dog()
c = Cat()

print(d.speak())  # Outputs: Bark
print(c.speak())  # Outputs: Meow


# =========================================
# 1.4 Using super() to Access Parent Methods
# =========================================
"""
The super() function allows you to call a method from the parent class.

This is useful when you want to:
- Extend behaviour instead of replacing it
"""

class Animal:
    def speak(self):
        return "Some generic sound"

class Dog(Animal):
    def speak(self):
        parent_sound = super().speak()
        return parent_sound + " + Bark"

d = Dog()

print(d.speak())  # Outputs: Some generic sound + Bark


# =========================================
# 1.5 Inheriting and Extending __init__
# =========================================
"""
A child class can reuse and extend the parent's constructor (__init__).

Use super().__init__() to initialise parent attributes.
"""

class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

d = Dog("Rex", "Labrador")

print(d.name)   # Outputs: Rex
print(d.breed)  # Outputs: Labrador


# =========================================
# 1.6 Checking Relationships
# =========================================
"""
Python provides built-in functions to verify relationships between 
classes and objects.
"""

print(isinstance(d, Dog))     # Outputs: True
print(isinstance(d, Animal))  # Outputs: True

print(issubclass(Dog, Animal))  # Outputs: True



# =========================================
# 1.7 Multiple Inheritance
# =========================================

"""
A class can inherit from more than one parent.

This allows combining behaviours from different sources.
"""

class Flyer:
    def fly(self):
        return "Flying"

class Swimmer:
    def swim(self):
        return "Swimming"

class Duck(Flyer, Swimmer):
    pass

duck = Duck()

print(duck.fly())   # Outputs: Flying
print(duck.swim())  # Outputs: Swimming


# =========================================
# 1.8 Method Resolution Order (MRO)
# =========================================
"""
When multiple inheritance is used, Python follows a specific order to find methods.

This is called the Method Resolution Order (MRO).
"""

class A:
    def action(self):
        return "A"

class B(A):
    def action(self):
        return "B"

class C(A):
    def action(self):
        return "C"

class D(B, C):
    pass

d = D()

print(d.action())  # Outputs: B
print(D.__mro__)  # Shows the lookup order
"""
The reason it outputs "B" is due to Python’s Method Resolution Order (MRO) — the rule Python 
uses to decide which method gets called first in multiple inheritance.

The MRO for my class - if I print with print(D.__mro__)
Then following is output:
(<class '__main__.D'>,
 <class '__main__.B'>,
 <class '__main__.C'>,
 <class '__main__.A'>,
 <class 'object'>)

How Python resolves d.action()
Python checks classes in this exact order:
D → no action()
B → found action() here
C → (never reached)
A → (never reached)

Even though both B and C override action(), Python does not try both — it stops at the first match in the MRO.
"""


# =========================================
# 1.9 Summary
# =========================================
"""
Inheritance allows a class to:
- Reuse behaviour from another class
- Add new functionality
- Override existing behaviour

Key tools:
- class Child(Parent)
- super()
- isinstance()
- issubclass()
"""
