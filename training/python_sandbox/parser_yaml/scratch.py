## Experient with comprehensions, generators and exceptions

import logging

logging.basicConfig(level=logging.INFO)

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

COMPANIES = {
    "BBC": {
        "location": "London",
        "employess": 20000,
        "website": "https://www.bbc.co.uk",
        "phone": "118118",
    },
    "Sky": {
        "location": "Osterly Park",
        "employees": 8000,
        "website": "https://www.sky.com",
        "phone": "911",
    },
}

EMAIL_ADDRESS = {
    "nigel@bbc.com",
    "bob@gmail.com",
    "clive@gmail.com",
    "allan@outlook.com",
}


def list_comprehension_practice() -> None:
    user_names: list[str] = [user["name"] for user in USERS]
    logging.info(f"test list comprehension {user_names}")

    user_names_loop: list[str] = []
    for user in USERS:
        name = user["name"]
        user_names_loop.append(name)
    logging.info(f"test list loop: {user_names_loop}")


def dictionary_comprehension_practice() -> None:
    company_websites: dict[str] = {
        name: info["website"] for name, info in COMPANIES.items()
    }
    logging.info(f"test dict comprehension: {company_websites}")

    company_websites_loop: dict[str] = {}
    for name, info in COMPANIES.items():
        company_websites_loop[name] = info["website"]
    logging.info(f"test dict loop: {company_websites}")


def set_comprehension_practice() -> None:
    email_client: set[str] = {email.split("@")[1] for email in EMAIL_ADDRESS}
    logging.info(f"test set: {email_client}")

    email_client_loop: set[str] = set()
    for email in EMAIL_ADDRESS:
        domain = email.split("@")[1]
        email_client_loop.add(domain)
    logging.info(f"test set loop: {email_client_loop}")


def main():
    list_comprehension_practice()
    dictionary_comprehension_practice()
    set_comprehension_practice()


if __name__ == "__main__":
    main()
