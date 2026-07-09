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
        logger.info(f"Error: {e}")
        logger.info(f'File not found: {input_file_path}')
    except json.JSONDecodeError as e:
        logger.info(f'Invalid JSON.')
        logger.info(f"Line {e.lineno}, column {e.colno}: {e.msg}")
    else:
        logger.info('Json loaded successfully')
    

    
    # remove enclosure_id from each of the animals
    transformed = [{k: v for k, v in row.items() if k not in {'enclosure_id', 'scientific_name'}} for row in data]
    
    output_path = os.path.join(script_dir, 'out.json')
    with open(output_path, "w") as file:
        json.dump(transformed, file, indent=2)


if __name__ == '__main__':
    import_json_file()
    