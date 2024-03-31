import pandas as pd
import numpy as np
import json
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
    with open(paths.SUBJECT_GROUPS_2_TIME, 'r') as file:
        groups = json.load(file)
        
    df = pd.read_csv(paths.DATA_CLEAN_SUBJECT_TIME)
    df.set_index('file', inplace=True)

    # Split email addresses in the DataFrame
    df['From'] = df['From'].map(split_email_addresses)
    df['To'] = df['To'].map(split_email_addresses)
    df['Cc'] = df['Cc'].map(split_email_addresses)
    df['Bcc'] = df['Bcc'].map(split_email_addresses)

    df['recepients'] = df.apply(lambda row: compute_union(row, 'To', 'Cc').union(row['Bcc']), axis=1)
    df['participants'] = df.apply(lambda row: compute_union(row, 'From', 'recepients'), axis=1)

    df['re'] = df['Subject'].apply(has_re_prefix)
    df['fwd'] = df['Subject'].apply(has_fwd_prefix)

    chains = groups.copy()
    
    for key, value in groups.items():
        chains[key]['ids'] = sorted(chains[key]['ids'], key=lambda x: df.loc[x, 'date-timestamp'])
        if not df.loc[value['ids'][1], 'From'].intersection(df.loc[value['ids'][0], 'recepients']):
            del chains[key]
            continue  
        if df.loc[value['ids'][0], 're'] or df.loc[value['ids'][0], 'fwd']:
            if not (df.loc[value['ids'][1], 'fwd'] or df.loc[value['ids'][1], 're']):
                del chains[key]
                continue
        if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) > (60**2)*24*120:
            if df.loc[value['ids'][1], 're'] == False:
                if df.loc[value['ids'][1], 'fwd'] == False:
                    del chains[key]
    
    print(f"\nNumber of chains with the length 2: {len(chains)}")

    with open(paths.CHAINS_2, 'w') as file:
        json.dump(chains, file)


"""
with open('../'+paths.CHAINS_2, 'r') as file:
        chains = json.load(file)
for i, key in enumerate(list(chains.keys())[:100]):
    print_text_from_files(chains, key, '../'+paths.CHECK_CHAINS+f'chain_{i+1}')
"""
