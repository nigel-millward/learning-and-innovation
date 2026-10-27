import os
import json
import logging

logger = logging.getLogger(__name__)


def import_json_file():
    script_dir = os.path.dirname(__file__)
    input_file_path = os.path.join(script_dir, 'input.json')
    
    try: 
        with open(input_file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        logger.error("File not found: %s", input_file_path)
        raise
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON at line %d, column %d: %s", e.lineno, e.colno, e.msg)
        raise
    else:
        logger.info('Json loaded successfully')
    

    # remove enclosure_id from each of the animals
    transformed = [{k: v for k, v in row.items() if k not in {'enclosure_id', 'scientific_name'}} for row in data]
    
    output_path: str = os.path.join(script_dir, 'out.json')
    try:
        with open(output_path, "w") as file:
            json.dump(transformed, file, indent=2)
    except OSError as e:
        logger.error("Failed to write output file: %s", e)
        raise


if __name__ == '__main__':
    import_json_file()
    