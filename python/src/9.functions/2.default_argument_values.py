## This creates a function that can be called with fewer arguments than it is defined to allow
def calculate_total(price, tax_rate=0.20):
    total = price + (price * tax_rate)
    return f"Total: £{total:.2f}"

# Using default 20% rate
print(calculate_total(100))  # Total: £120.00

# Using a custom tax rate
print(calculate_total(100, tax_rate=0.10))  # Total: £
