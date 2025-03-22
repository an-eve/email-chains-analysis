import os
import csv
import paths

def extract_text_from_files(folder_path):
    """
    Extract text data from all files within a given folder and its subfolders.

    Args:
    - folder_path (str): The path to the folder containing files to extract text from.

    Returns:
    - file_data (list): A list of tuples, each containing file path and its corresponding text data.
    """
    file_data = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    file_text = f.read()
            except UnicodeDecodeError:
                # Handle files with other encodings
                with open(file_path, 'r', encoding='latin-1') as f:
                    file_text = f.read()
            file_data.append((file_path, file_text))
    return file_data

def write_to_csv(data, csv_file):
    """
    Write data to a CSV file.

    Args:
    - data (list): A list of tuples, each containing file path and its corresponding text data.
    - csv_file (str): The path to the CSV file to write data into.
    """
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Path', 'File Text'])
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":  
    file_data = extract_text_from_files(paths.DATA_FOLDER)
    write_to_csv(file_data, paths.CSV_DATA)
    print("CSV file created successfully!")
