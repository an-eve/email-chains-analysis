import os
import csv

def extract_text_from_files(folder_path):
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
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Path', 'File Text'])
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    parent_path = 'data/maildir'  
    csv_file = 'data/mails-data.csv'  
    file_data = extract_text_from_files(parent_path)
    write_to_csv(file_data, csv_file)
    print("CSV file created successfully!")
