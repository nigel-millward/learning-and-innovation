import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

class YamlParseError(Exception):
    pass

class UserValidationError(Exception):
    """Raised when one or more users fail validation. Holds all messages."""
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s):\n  - " + "\n  - ".join(errors))


FILE_PATH = Path(__file__).parent / "test_data/user.yaml"
REQUIRED_FIELDS = {"id", "name", "age", "is_active", "score", "role"}



def parse_users(file_path) -> list:
    """Read yaml from relative file path and parse to a list

    Args:
        file_path (_type_): Relative path to the data file from the current python module

    Returns:
        list: user data 
    """
    try:
        with open(file_path, "r") as file:
            data: dict = yaml.safe_load(file)
    except FileNotFoundError as exc:
        raise YamlParseError(f"YAML file not found: {file_path}") from exc   
    except yaml.YAMLError as exc:
        raise YamlParseError(f"Invalid YAML in {file_path}: {exc}") from exc
    
    if not isinstance(data, dict): 
        raise YamlParseError(f"Expected a mapping at top level of {file_path}")
   
    return data.get("users", [])


def validate_required_fields(users: list) -> list[str]:
    
    errors = []
    
    for index, user in enumerate(users, start=1):
        user_ref = f"id={user['id']}" if "id" in user else f"index {index}"
        
        for field in sorted(REQUIRED_FIELDS - user.keys()):
            errors.append(f"User {user_ref}: missing field '{field}'")
    
    return errors


def validate_data_types(users: list) -> list[str]:
    errors = []
    
    expected = {"id": int, "name": str, "age": int,
                "is_active": bool, "score": float, "role": str}
    
    for index, user in enumerate(users, start=1):
        user_ref = f"id={user.get('id', f'index {index}')}"
        for field, expected_type in expected.items():
            if field in user and not isinstance(user[field], expected_type):
                errors.append(
                    f"User {user_ref}: field '{field}' should be {expected_type.__name__}, "
                    f"got {type(user[field]).__name__}"
                )
    
    return errors

def validate_ranges(users: list) -> list[str]:
    return []

def validate_business_rules(users: list) -> list[str]:
    return []

def validate(users: list) -> None:
    errors: list[str] = []

    for check in (validate_required_fields, validate_data_types,
                  validate_ranges, validate_business_rules):
        errors.extend(check(users))

    if errors:
        raise UserValidationError(errors)

def main():
    try:
        parsed_users = parse_users(FILE_PATH)
        validate(parsed_users)
    except (YamlParseError, UserValidationError):
        logging.exception("Could not process users")
        raise SystemExit(1)
    
    logging.info("Parsed %d valid users", len(parsed_users))

if __name__ == "__main__":
    main()



