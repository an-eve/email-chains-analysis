import pandas as pd
import numpy as np
import json
import random
import re
import paths


def is_nan(value):
    '''
    Check if the given string is NaN (Not a Number).

    Args:
    - value: The input value to check.

    Returns:
    - bool: True if the value is NaN, False otherwise.
    '''
    return isinstance(value, float) and np.isnan(value)

def split_email_addresses(line):
    '''
    Split a line containing multiple email addresses or names into a set of individual addresses or names.

    Args:
    - line (str): The input line containing multiple email addresses or names separated by commas.

    Returns:
    - set or None: A set containing individual email addresses or names if the input is not NaN, else None.
    '''
    if not is_nan(line):
        addrs = line.split(',')
        addrs = frozenset(map(lambda x: x.strip(), addrs))
    else:
        addrs = frozenset()
    return addrs

# Function to compute union of two columns in a DataFrame row
def compute_union(row, column1, column2):
    return row[column1].union(row[column2])

def has_re_prefix(string):
    '''
    Check if the given string has a 'Re:' prefix.

    Args:
    - string (str): The input string to check.

    Returns:
    - bool: True if the string has an email prefix, False otherwise.
    '''
    prefix_pattern = re.compile(r'Re:', flags=re.IGNORECASE)
    match = re.search(prefix_pattern, string)
    return bool(match)

def has_fwd_prefix(string):
    '''
    Check if the given string has common email prefixes ('Fw:', 'Fwd:').

    Args:
    - string (str): The input string to check.

    Returns:
    - bool: True if the string has email prefixes, False otherwise.
    '''
    prefix_pattern = re.compile(r'(Fw:|Fwd:)', flags=re.IGNORECASE)
    match = re.search(prefix_pattern, string)
    return bool(match)

def contains_specific_phrases(text):
    '''Checks if the text contains specific phrases case-insensitively using regular expressions.

    Args:
    - text (str): The text to be checked.

    Returns:
    - bool: True if the text contains any of the specified phrases (case-insensitive), False otherwise.
    '''
    return bool(re.search(r'Forwarded by|Original Message|\(Revision: \d\)', text, flags=re.IGNORECASE))


def add_clean_text(text):
    '''Cleans the text content for later processing, removing unnecessary characters, phrases and spaces.
    
    Args:
    - text (str): Text content to be cleaned.
    
    Returns:
    - str: Cleaned text content.
    '''
    # Remove the symbols
    text = re.sub(r'=20', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=09', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=018', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=01', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'3D', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\?', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=\n', '', text, flags=re.IGNORECASE)
    
    # Emails
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  
    text = re.sub(email_pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(r'mailto:', '', text, flags=re.IGNORECASE)
    
    
    # Remove the phrase "Please respond to" from each line
    text = re.sub(r'Please respond to', '', text, flags=re.IGNORECASE)
    # URLs
    text = re.sub(r"(https?://[^<>|\s]+)", " ", text, flags = re.IGNORECASE)
    # Remove lines similar to "- filename.extension"
    text = re.sub(r'- .*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif)', '', text, flags=re.IGNORECASE)  
    # Remove document names enclosed within double angle brackets
    text = re.sub(r'<<.*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif)>>', '', text, flags=re.IGNORECASE)   
    
    # Remove <Embedded StdOleLink>, <Embedded Picture (Metafile)>, ect.
    text = re.sub(r'<Embedded StdOleLink>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[IMAGE\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Microsoft Excel Worksheet>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Device Independent Bitmap\)>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Metafile\)>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded >', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Device Independent Bitmap\)>', ' ', text, flags=re.IGNORECASE)
    
    # Remove the symbols
    text = re.sub(r'_!', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'!_', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'_', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'~', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'-', ' ', text, flags=re.IGNORECASE)

    text = re.sub(r'[\[\]]', '', text)
    text = re.sub(r'[\(\)]', '', text)
    text = re.sub(r'\'', ' ', text, flags=re.IGNORECASE)  
    text = re.sub(r',', '', text, flags=re.IGNORECASE)
    text = re.sub(r'>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\;', '', text, flags=re.IGNORECASE)   
    text = re.sub(r'\+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'"', '', text, flags=re.IGNORECASE)
    text = re.sub(r'&', '', text, flags=re.IGNORECASE)
    text = re.sub(r'=', '', text, flags=re.IGNORECASE)
    text = re.sub(r'=', '', text, flags=re.IGNORECASE)

    # Clean up other unnecessary characters and spaces
    text = re.sub(r'[\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    
    return text.lower()

def print_text_from_files(dictionary, key, combined_path):
    '''
    Print and save the combined text from files associated with a given subject line.

    Args:
    - dictionary (dict): The dictionary containing email groups indexed by subject line.
    - key (str): The subject line for which the files need to be combined and printed.
    - combined_path (str): The path to save the combined text file.
    '''
    if key in dictionary:
        ids = dictionary[key]['ids']
        with open(combined_path, 'w') as combined_file:
            for ind, file_path in enumerate(ids):
                with open('../' + file_path, 'r') as file:
                    combined_file.write('\n'*4 + '#' * 60 + '\n')
                    combined_file.write('#' * 5 + ' ' * 20 + f'Message {ind+1}' + ' ' * 20 + '#' * 5 + '\n')
                    combined_file.write('#' * 60 + '\n'*4)
                    combined_file.write(file.read())
        print(f"Text from files combined and saved to {combined_path}")
    else:
        print("Key not found in the dictionary.")


if __name__ == "__main__":
    with open(paths.SUBJECT_GROUPS_1, 'r') as file:
        groups_1 = json.load(file)
    with open(paths.SUBJECT_GROUPS_2, 'r') as file:
        groups_2 = json.load(file)

    print(f"Number of the subject groups of the length 1: {len(groups_1)}")       
    print(f"Number of the subject groups of the length 2: {len(groups_2)}")
        
    df = pd.read_csv(paths.DATA_CLEAN_SUBJECT)
    # File name set as index
    df.set_index('file', inplace=True)
    
    # Count the number of NaNs for each column
    nan_counts = df.isna().sum()
    print(f"\nNumber of NaNs for every column:\n{nan_counts}")
    df['content-clean'] = df['content-clean'].fillna('')

    # Split email addresses in the DataFrame
    df['From'] = df['From'].map(split_email_addresses)
    df['To'] = df['To'].map(split_email_addresses)
    df['Cc'] = df['Cc'].map(split_email_addresses)
    df['Bcc'] = df['Bcc'].map(split_email_addresses)

    # Compute union of 'To' and 'Cc' columns
    df['recepients'] = df.apply(lambda row: compute_union(row, 'To', 'Cc').union(row['Bcc']), axis=1)
    df['participants'] = df.apply(lambda row: compute_union(row, 'From', 'recepients'), axis=1)
   
    # Check for 'Re:' and 'Fwd:' prefixes in 'Subject' column
    df['re'] = df['Subject'].apply(has_re_prefix)
    df['fwd'] = df['Subject'].apply(has_fwd_prefix)

    ordered_groups = groups_2.copy()
    for key, value in ordered_groups.items():
        ordered_groups[key]['ids'] = sorted(ordered_groups[key]['ids'], key=lambda x: df.loc[x, 'date-timestamp'])

    # Remove raw html emails
    for key, value in groups_2.items():
        if '</html>' in df.loc[ordered_groups[key]['ids'][0], 'content'] or '</html>' in df.loc[ordered_groups[key]['ids'][1], 'content']:
            del ordered_groups[key]
   
    chains_1 = {}
    for key, value in groups_1.items():
        chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"]
    
    chains_2 = ordered_groups.copy()
    for key, value in ordered_groups.items():
        # Time period regulation
        if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) > (60**2)*24*30*2:
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][1]
            del chains_2[key]
            continue      
        # Re/Fwd neither in the first email, nor in the second (follow-ups are difficult 
        # to detect, they could be mixed up with 2 separate emails with the same subject)
        if not (df.loc[value['ids'][0], 're'] or df.loc[value['ids'][1], 're'] or df.loc[value['ids'][0], 'fwd'] or df.loc[value['ids'][1], 'fwd']):
            # Shorter time to make sure it's a chain
            if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) > (60**2)*24*7:
                chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
                chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][1]
                del chains_2[key]
                continue
            # Forward and (maybe?) Reply
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and (df.loc[value['ids'][0], 'content-clean'] in df.loc[value['ids'][1], 'content-clean']) and contains_specific_phrases(df.loc[value['ids'][1], 'content-clean']):
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    continue
            # Reply or Forward
            if df.loc[value['ids'][1], 'From'].intersection(df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From'])):
                continue
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][1]
            del chains_2[key]
        # Re/Fwd in the second email
        elif (df.loc[value['ids'][1], 'fwd'] or df.loc[value['ids'][1], 're']):
            # Reply or Forward
            if df.loc[value['ids'][1], 'From'].intersection(df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From'])):
                continue
            # Another case of Forward
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and df.loc[value['ids'][1], 'fwd']:
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    continue
            # Follow-up
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and ((df.loc[value['ids'][1], 'recepients'].difference(df.loc[value['ids'][1], 'From'])).intersection(df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From']))):
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    # Avoiding time errors emails
                    if (abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp'])/(60*60)) % 1 == 0:
                        if (add_clean_text(df.loc[value['ids'][0], 'content']) == add_clean_text(df.loc[value['ids'][1], 'content'])) or (df.loc[value['ids'][0], 'Content-Type'] != df.loc[value['ids'][1], 'Content-Type']):
                            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
                            del chains_2[key]
                            continue  
                    continue
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][1]
            del chains_2[key]  
        # Wrong Timing
        elif (df.loc[value['ids'][0], 'fwd'] or df.loc[value['ids'][0], 're']):
            # Shorter time to make sure it's a chain
            if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) > (60**2)*8:
                chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
                chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][1]
                del chains_2[key]
                continue
            # Reply or Forward
            if df.loc[value['ids'][0], 'From'].intersection(df.loc[value['ids'][1], 'recepients'].difference(df.loc[value['ids'][1], 'From'])):
                continue
            # Another case of Forward
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and df.loc[value['ids'][0], 'fwd']:
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    continue
            # Follow-up
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and ((df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From'])).intersection(df.loc[value['ids'][1], 'recepients'].difference(df.loc[value['ids'][1], 'From']))):
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    # Avoiding time errors emails
                    if (abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp'])/(60*60)) % 1 == 0:
                        if (add_clean_text(df.loc[value['ids'][0], 'content']) == add_clean_text(df.loc[value['ids'][1], 'content'])) or (df.loc[value['ids'][0], 'Content-Type'] != df.loc[value['ids'][1], 'Content-Type']):
                            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
                            del chains_2[key]
                            continue  
                    continue
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][1]
            del chains_2[key]  
        else:
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][0]
            chains_1[f"[{len(chains_1)+1}] " + key] = value["ids"][1]
            del chains_2[key]
        
    print(f"\nNumber of chains with the length 1: {len(chains_1)}")
    print(f"Number of chains with the length 2: {len(chains_2)}")
    
    chains_2_modified = {}
    for key, value in chains_2.items():
        chains_2_modified[f"[{len(chains_2_modified)+1}] " + key] = value["ids"]
        
    # Save chains to JSON files
    with open(paths.CHAINS_1, 'w') as file:
        json.dump(chains_1, file)  
    with open(paths.CHAINS_2, 'w') as file:
        json.dump(chains_2_modified, file)


"""
with open('../'+paths.CHAINS_2, 'r') as file:
        chains_2 = json.load(file)
for i, key in enumerate(list(chains_2.keys())[:100]):
    print_text_from_files(chains_2, key, '../' + paths.CHECK_CHAINS + f'chain_{i+1}')
"""




