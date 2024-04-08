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
    with open("../"+paths.SUBJECT_GROUPS_2, 'r') as file:
        groups = json.load(file)
        
    print(f"Number of the subject groups of the length 2: {len(groups)}")
        
    df = pd.read_csv("../"+paths.DATA_CLEAN_SUBJECT)
    df.set_index('file', inplace=True)
    
    # Count the number of NaNs for each column
    nan_counts = df.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")
    df['content-clean'] = df['content-clean'].fillna('')

    # Split email addresses in the DataFrame
    df['From'] = df['From'].map(split_email_addresses)
    df['To'] = df['To'].map(split_email_addresses)
    df['Cc'] = df['Cc'].map(split_email_addresses)
    df['Bcc'] = df['Bcc'].map(split_email_addresses)

    df['recepients'] = df.apply(lambda row: compute_union(row, 'To', 'Cc').union(row['Bcc']), axis=1)
    df['participants'] = df.apply(lambda row: compute_union(row, 'From', 'recepients'), axis=1)

    df['re'] = df['Subject'].apply(has_re_prefix)
    df['fwd'] = df['Subject'].apply(has_fwd_prefix)

    ordered_groups = groups.copy()
    for key, value in ordered_groups.items():
        ordered_groups[key]['ids'] = sorted(ordered_groups[key]['ids'], key=lambda x: df.loc[x, 'date-timestamp'])


    chains = ordered_groups.copy()
    new = []
    for key, value in ordered_groups.items():
        # Time period regulation
        if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) > (60**2)*24*30*2:
            del chains[key]
            continue      
        # Re/Fwd neither in the first email, nor in the second (follow-ups are difficult 
        # to detect, they could be mixed up with 2 separate emails with the same subject)
        if not (df.loc[value['ids'][0], 're'] or df.loc[value['ids'][1], 're'] or df.loc[value['ids'][0], 'fwd'] or df.loc[value['ids'][1], 'fwd']):
            # Shorter time to make sure it's a chain
            if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) > (60**2)*24*7:
                del chains[key]
                continue
            # Forward and (maybe?) Reply
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and (df.loc[value['ids'][0], 'content-clean'] in df.loc[value['ids'][1], 'content-clean']) and contains_specific_phrases(df.loc[value['ids'][1], 'content-clean']):
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    continue
            # Reply or Forward
            if df.loc[value['ids'][1], 'From'].intersection(df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From'])):
                continue
            del chains[key]
            continue
        # Re/Fwd neither in the second email
        elif (df.loc[value['ids'][1], 'fwd'] or df.loc[value['ids'][1], 're']):
            # Reply or Forward
            if df.loc[value['ids'][1], 'From'].intersection(df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From'])):
                continue
            # Another case of Forward
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and df.loc[value['ids'][1], 'fwd']:
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    #new.append(key)
                    continue
            # Follow-up
            if (df.loc[value['ids'][0], 'From'] == df.loc[value['ids'][1], 'From']) and ((df.loc[value['ids'][1], 'recepients'].difference(df.loc[value['ids'][1], 'From'])).intersection(df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From']))):
                if df.loc[value['ids'][0], 'content-clean'] != df.loc[value['ids'][1], 'content-clean']:
                    #new.append(key)
                    continue
            #new.append(key)
            del chains[key]
            continue    
        else:
            new.append(key)
            del chains[key]
                  

    print(f"\nNumber of chains with the length 2: {len(chains)}")
    
    # Some data exploration 
    # Make sense for timing
    s=0
    new =[]
    for key, value in groups.items():
        if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) > (60**2)*24*30*2:
            if (df.loc[value['ids'][0], 're'] or df.loc[value['ids'][1], 're'] or df.loc[value['ids'][0], 'fwd'] or df.loc[value['ids'][1], 'fwd']):
                new.append(key)
                s += 1
    s
    for i, key in enumerate(new):
        print_text_from_files(groups, key, '../'+paths.CHECK_CHAINS+f'aa_{i+1}')
    
 
     # no Re or Fwd for the first, but re or fwd for the second
    s=0
    for key, value in groups.items():
        if (df.loc[value['ids'][0], 're'] or df.loc[value['ids'][0], 'fwd']) and not(df.loc[value['ids'][1], 're'] or df.loc[value['ids'][1], 'fwd']):
            s += 1
    s #few instances, 800, so not important
    
    # no Re or Fwd at all
    s=0
    for key, value in groups.items():
        if not (df.loc[value['ids'][0], 're'] or df.loc[value['ids'][1], 're'] or df.loc[value['ids'][0], 'fwd'] or df.loc[value['ids'][1], 'fwd']):
            s += 1
    s
    # still Looks like reply
    s=0
    new =[]
    for key, value in ordered_groups.items():
        if not (df.loc[value['ids'][0], 're'] or df.loc[value['ids'][1], 're'] or df.loc[value['ids'][0], 'fwd'] or df.loc[value['ids'][1], 'fwd']):
            if df.loc[value['ids'][1], 'From'].intersection(df.loc[value['ids'][0], 'recepients'].difference(df.loc[value['ids'][0], 'From'])):
                # Shortertime to make sure
                if abs(df.loc[value['ids'][0], 'date-timestamp'] - df.loc[value['ids'][1], 'date-timestamp']) < (60**2)*24*7:
                    s += 1
                    new.append(key)
        # Cannot check follow up here, impossible to distincct from repeating email
        # fwd difficult, it could be the same person receiving one, sending another email
    s
    for i, key in enumerate(new):
        print_text_from_files(ordered_groups, key, '../'+paths.CHECK_CHAINS+f'aa_{i+1}')
    
    
    # Number of fathters without Re or Fwd
    fathers_proper = len(chains)
    for chain in chains.values():
        fathers_proper -= int(has_re_prefix(df.loc[chain['ids'][0], 'Subject']) or has_fwd_prefix(df.loc[chain['ids'][0], 'Subject']))
    print(f"\n Percentage of fathers without Re or Fwd: {fathers_proper/len(chains)*100:.1f} %")




    with open(paths.CHAINS_2, 'w') as file:
        json.dump(chains, file)


"""
with open('../'+paths.CHAINS_2, 'r') as file:
        chains = json.load(file)
for i, key in enumerate(list(chains.keys())[:100]):
    print_text_from_files(chains, key, '../'+paths.CHECK_CHAINS+f'chain_{i+1}')
"""

for i, key in enumerate(new[:200]):
    print_text_from_files(groups, key, '../'+paths.CHECK_CHAINS+f'aa_{i+1}')
    
random_new = random.sample(new, 100)
for i, key in enumerate(random_new):
    print_text_from_files(ordered_groups, key, '../'+paths.CHECK_CHAINS+f'aa_{i+1}')
    
for i, key in enumerate(new):
    print_text_from_files(ordered_groups, key, '../'+paths.CHECK_CHAINS+f'aa_{i+1}')

