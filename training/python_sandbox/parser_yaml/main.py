import yaml
import path
import logging

logging.basicConfig(level=logging.INFO)

FILE_PATH = path.Path(__file__).parent / "test_data/user.yaml"

def parse_users(file_path) -> list:
    with open(file_path, "r") as file:
        data: dict = yaml.safe_load(file)
    return data.get("users", [])

def main():
    parsed_users = parse_users(FILE_PATH)
    logging.info("Parsed users: %s", parsed_users)

if __name__ == "__main__":
    main()
    