import os
import csv

script_dir = os.path.dirname(__file__)
input_file_path = os.path.join(script_dir, 'input.csv')


def read_csv_file_as_string():
    import os

    with open(input_file_path, "r") as csv_file:
        file_content:str = csv_file.read()
        
    print(f'script_dir: {script_dir}')
    print(f'input_file_path: {input_file_path}')
    print(f'file_content: {file_content}')
    

def read_csv_file_with_csv_reader():
    
    # create a list of list
    with open(input_file_path, "r") as csv_file:
        data_set = csv.reader(csv_file)
        data:list = []
        for row in data_set:
            data.append(row)
    
    print(data)

    # csv.reader is iterable, so can wrap it directly with (list())
    with open(input_file_path, "r") as csv_file:
        quick_data: list = list(csv.reader(csv_file))

    print(quick_data)
    
def remove_enclosure_from_csv_file():
    with open(input_file_path,"r" ) as csv_file:
        data:list = list(csv.reader(csv_file))
    
    # remove last item of list to transform the data
    transformed_data:list = []    
    for row in data:
        new_row = row[:len(row)-1]
        transformed_data.append(new_row)
    
    print(transformed_data)  
     
    # less verbose with a comprehension
    transformed: list = [row[:-1] for row in data]
    
    print(transformed)
        


remove_enclosure_from_csv_file()