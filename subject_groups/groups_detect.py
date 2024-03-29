import pandas as pd
import numpy as np
import json
import time
import re
import paths

def has_no_prefix(string):
    '''
    Check if the given string has no common email prefixes ('Re:', 'Fw:', 'Fwd:').

    Args:
    - string (str): The input string to check.

    Returns:
    - bool: True if the string has no common email prefixes, False otherwise.
    '''
    prefix_pattern = re.compile(r'(Fw:|Re:|Fwd:)', flags=re.IGNORECASE)
    match = re.search(prefix_pattern, string)
    return not match

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
        addrs = None
    return addrs

def group_info_from_frame(frame):
    '''
    Group email information from a DataFrame by the subject line.

    Args:
    - frame (pandas.DataFrame): The input DataFrame containing email information.

    Returns:
    - dict: A dictionary containing groups of emails indexed by the subject line.
    '''
    chain_dict = {}
    for index, mail in frame.iterrows():
        mail_key = mail['subject-clean']
        if mail_key in chain_dict:
            chain_dict[mail_key]["length"] += 1
            chain_dict[mail_key]["ids"].add(mail['file'])
        else:
            chain_dict[mail_key] = {}
            chain_dict[mail_key]["length"] = 1
            chain_dict[mail_key]["ids"] = {mail['file']}     
    return chain_dict


if __name__ == "__main__":
    
    # Read the DataFrame from the CSV file
    df = pd.read_csv(paths.DATA_CLEAN_SUBJECT)

    # Split email addresses in the DataFrame
    df['From'] = df['From'].map(split_email_addresses)
    df['To'] = df['To'].map(split_email_addresses)
    df['Cc'] = df['Cc'].map(split_email_addresses)
    df['Bcc'] = df['Bcc'].map(split_email_addresses)

    # Display dataset size and first rows
    print(f"\nThe dataset's size: {df.shape}")
    print(f"First rows:\n {df.head()}")

    # Count emails without 'Re' and 'Fw' prefixes
    s = 0
    for index, mail in df.iterrows():
        if not is_nan(mail["Subject"]):
            s += int(has_no_prefix(mail["Subject"]))
    print(f"Number of emails without 'Re' and 'Fw': {s}\n")
    
    # Group email information by subject line
    start_time = time.time()
    groups = group_info_from_frame(df)
    end_time = time.time()

    # Display the number of groups detected
    print(f"\nNumber of groups detected: {len(groups)}\n")
    
    # Filter the data for groups with size greater than 1
    filtered_groups = {key: value for key, value in groups.items() if value['length'] > 1}
    print(f"\nNumber of groups bigger than 1: {len(filtered_groups)}\n")
    
    # Filter the data for groups with size greater than 2
    filtered_groups = {key: value for key, value in groups.items() if value['length'] > 2}
    print(f"\nNumber of groups bigger than 2: {len(filtered_groups)}\n")
        
    # Convert groups to JSON format and save to file
    groups_to_json = {key: {"length": value["length"], "ids": list(value["ids"])}  for key, value in groups.items()}
    with open(paths.SUBJECT_GROUPS, 'w') as file:
        json.dump(groups_to_json, file)

    # Display completion message and execution time
    print("\nGroups file created successfully!")
    print("Time taken:", end_time - start_time, "seconds")


