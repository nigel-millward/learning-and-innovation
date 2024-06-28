import random
import string

def generate_password(length, chars=string.ascii_letters + string.digits):
    """
    Generates a random password of the specified length using the provided character set.

    Args:
        length (int): The desired length of the password.
        chars (str, optional): The set of characters to choose from. Defaults to a combination of
            ASCII letters and digits.

    Returns:
        str: The generated password.
    """
    return ''.join(random.choice(chars) for _ in range(length))

# Example usage
password = generate_password(12)
print(f"Generated password: {password}")
