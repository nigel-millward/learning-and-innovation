import os

script_dir = os.path.dirname(__file__)
input_file_path = os.path.join(script_dir, 'input.csv')

with open(input_file_path, "r") as file:
    file_content = file.read()


print(f'script_dir: {script_dir}')
print(f'input_file_path: {input_file_path}')
print(f'file_content: {file_content}')



