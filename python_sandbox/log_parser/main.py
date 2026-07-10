import os
import json
import logging

logger = logging.getLogger(__name__)

script_dir = os.path.dirname(__file__)
input_file_path = os.path.join(script_dir, 'application.log')

"""
+-------------------------------+---------------+----------------------------------+
| Approach                      | Type          | Best for                         |
+-------------------------------+---------------+----------------------------------+
| read()                        | str           | Regex across multi-line spans    |
| readlines()                   | list[str]     | Small files, random access       |
| for line in file / generator  | Iterator[str] | Large files, streaming processing|
+-------------------------------+---------------+----------------------------------+
"""

def import_log_file(file_path) -> iter[str]:
    """Generator: yields one stripped log line at a time. Memory-efficient for large files.
    
    A file object is iterable, and iterating over it yields one line at a time, reading from disk as it goes. 
    This is what makes it memory-efficient: it never loads the whole file into memory.
    """

    try:
        with open(file_path, 'r') as file:
            for line in file:
                stripped = line.rstrip('\n')
                if stripped:
                    yield stripped
    except FileNotFoundError:
        logger.error("Log file not found: %s", file_path)
        raise


def load_log_file(file_path) -> list[str]:
    """Materialise all log lines into a list for multi-pass analysis."""
    return list(import_log_file(file_path))

def write_log_file(data, file_name): 
    output_path = os.path.join(script_dir, file_name)
    try:
        json.dump(data, open(output_path, 'w'))
    except OSError as e:
        logger.error("Failed to write output file: %s", e)
        raise

#Count messages by log level.
def count_messages_by_level(log_file: list[str]) -> dict[str, int]:
    """Count the number of log messages for each log level.

    Assumes each line follows the format:
        <date> <time> <level> <service> <message>
        e.g. '2026-07-08 08:00:01 INFO auth-service User login successful'

    The log level is extracted from index 2 of each whitespace-split line
    (e.g. 'INFO', 'ERROR', 'WARNING', 'DEBUG').

    Args:
        log_file: A list of log line strings, as returned by load_log_file().

    Returns:
        A dict mapping each log level to the number of times it appears.
        e.g. {'INFO': 42, 'ERROR': 5, 'WARNING': 3, 'DEBUG': 10}
    """
    from collections import Counter
    levels: list[str] = [line.split()[2] for line in log_file if line]
    levels_count: dict[str, int] = dict(Counter(levels))

    output_path: str= os.path.join(script_dir, 'count_messages_by_log_level.json')
    write_log_file(levels_count, output_path)

#Count messages by service.



#Find all ERROR events.




#Extract IP addresses.





#Calculate average request duration.




#Find slow requests (>1000ms).




#Group events by session ID.




#Detect malformed log lines.




#Produce hourly summaries.




#Export results to CSV



if __name__ == '__main__':
    log_file = load_log_file(input_file_path)
    count_messages_by_level(log_file)