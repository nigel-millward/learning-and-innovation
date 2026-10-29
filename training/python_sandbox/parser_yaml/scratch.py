## Experient with comprehensions, generators and exceptions

import logging
logging.basicConfig(level=logging.INFO)

def comprehension_practice() -> None: 
  
  user_names: list[str] = [user["name"] for user in USERS ]
  logging.info(f"test comprehension {user_names}")


USERS = [
    {
        "id": 1,
        "name": "Jane Doe",
        "age": "28",
        "is_active": "true",
        "score": "95.5",
        "role": "Developer",
    },
    {
        "id": 2,
        "name": "John Smith",
        "age": "35",
        "is_active": "false",
        "score": "88.0",
        "role": "Developer",
    },
    {
        "id": 3,
        "name": "Alice Johnson",
        "age": "30",
        "is_active": "true",
        "score": "92.0",
        "role": "Designer",
    },
    {
        "id": 4,
        "name": "Bob Brown",
        "age": "40",
        "is_active": "false",
        "score": "85.0",
        "role": "Analyst",
    },
]

def main():
  comprehension_practice()


if __name__ == "__main__":
  main()

