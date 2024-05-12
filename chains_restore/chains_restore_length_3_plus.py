import pandas as pd
import numpy as np
from collections import Counter
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
        

def contains_specific_phrases(text):
    '''Checks if the text contains specific phrases case-insensitively using regular expressions.

    Args:
    - text (str): The text to be checked.

    Returns:
    - bool: True if the text contains any of the specified phrases (case-insensitive), False otherwise.
    '''
    return bool(re.search(r'Forwarded by|Original Message|\(Revision: \d\)|From:|To:|Sent by:', text, flags=re.IGNORECASE))

def print_groups(dictionary, key, combined_path):
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
        
def print_chains(dictionary, key, combined_path):
    '''
    Print and save the combined text from files associated with a given subject line.

    Args:
    - dictionary (dict): The dictionary containing email groups indexed by subject line.
    - key (str): The subject line for which the files need to be combined and printed.
    - combined_path (str): The path to save the combined text file.
    '''
    if key in dictionary:
        with open(combined_path, 'w') as combined_file:
            for i, chain in enumerate(dictionary[key]['chains']):
                combined_file.write('\n'*4 + '#' * 60 + '\n')
                combined_file.write('#' * 5 + ' ' * 20 + f'Chain {i+1}' + ' ' * 23 + '#' * 5 + '\n')
                combined_file.write('#' * 60 + '\n'*2)
                for ind, file_path in enumerate(chain):
                    with open('../' + file_path, 'r') as file:
                        combined_file.write('\n'*3 + '#' * 10 + ' ' * 15 + f'Message {ind+1}' + ' ' * 16 + '#' * 10 + '\n'*3)
                        combined_file.write(file.read())
        print(f"Text from files combined and saved to {combined_path}")
    else:
        print("Key not found in the dictionary.")
        

def extract_heading_name(heading):
    # Define a regular expression pattern to match the heading structure
    pattern = re.compile(r'\[\d+\]\s*(.*)')

    # Use the pattern to search for matches in the heading
    match = pattern.match(heading)

    # If there is a match, return the extracted heading name
    if match:
        return match.group(1).strip()
    else:
        # If no match is found, return None or raise an error, depending on your preference
        return None


if __name__ == "__main__":
    
    with open(paths.CHAINS_1, 'r') as file:
        chains_1 = json.load(file)
    with open(paths.CHAINS_2, 'r') as file:
        chains_2 = json.load(file)
        
    with open(paths.SUBJECT_GROUPS_3_PLUS, 'r') as file:
        groups = json.load(file)
        
    df = pd.read_csv(paths.DATA_CLEAN_SUBJECT_INF)
    
    # File path is the index
    df.set_index('file', inplace=True)
    
    # Count the number of NaNs for each column
    nan_counts = df.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")
    df['content-clean'] = df['content-clean'].fillna('')
    df['content-extra-clean'] = df['content-extra-clean'].fillna('')

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
    
    ordered_groups = groups.copy()
    for key, value in groups.items():
        (ordered_groups[key]['ids']).sort(key=lambda x: df.loc[x, 'date-timestamp'])
    
    print(f"\nNumber of ordered groups: {len(ordered_groups)}")

    with open(paths.ORDERED_GROUPS, 'w') as file:
        json.dump(ordered_groups, file)
        
    chains = {}
    for key, value in list(ordered_groups.items()):
        chains[key]={}
        chains[key]['length'] = []
        chains[key]['chains'] = []
        emails_list = (ordered_groups[key]['ids']).copy()
        while len(emails_list) > 0:
            candidate = []
            candidate.append(emails_list.pop(0))
            emails_list_cpy = emails_list.copy()
            for email in emails_list_cpy:
                candidate_cpy = candidate.copy()
                # Avoiding time errors emails
                time_error = False
                for item in candidate_cpy:
                    if (df.loc[email, 're'] == df.loc[item, 're']) and (df.loc[email, 'fwd'] == df.loc[item, 'fwd']):
                        if (df.loc[item, 'From'] == df.loc[email, 'From']) and (df.loc[email, 'recepients'] == df.loc[item, 'recepients']):
                            if (abs(df.loc[item, 'date-timestamp'] - df.loc[email, 'date-timestamp'])/(60*60)) % 1 == 0:
                                if (df.loc[item, 'content-extra-clean'] == df.loc[email, 'content-extra-clean']) or (df.loc[item, 'Content-Type'] != df.loc[email, 'Content-Type']):
                                    emails_list.remove(email)
                                    time_error = True
                                    break 
                if not time_error:
                    for item in candidate_cpy:
                        # Time period regulation
                        if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) > (60**2)*24*30*3:
                            continue 
                        # Re/Fwd neither in the first email, nor in the second (follow-ups are difficult 
                        # to detect, they could be mixed up with 2 separate emails with the same subject)
                        if not (df.loc[email, 're'] or df.loc[item, 're'] or df.loc[email, 'fwd'] or df.loc[item, 'fwd']):
                            # Shorter time to make sure it's a chain
                            if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) > (60**2)*24*14:
                                continue
                            if df.loc[email, 'participants'].intersection(df.loc[item, 'participants']):
                                # Wrong time
                                if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) < (60**2)*24:
                                    if df.loc[email, 'content-extra-clean'] in df.loc[item, 'content-extra-clean']:
                                        if df.loc[item, 'content-extra-clean'] != df.loc[email, 'content-extra-clean']:
                                            candidate.append(email)
                                            emails_list.remove(email)
                                            break  
                                # Right time
                                if df.loc[item, 'content-extra-clean'] in df.loc[email, 'content-extra-clean']:
                                    if df.loc[item, 'content-extra-clean'] != df.loc[email, 'content-extra-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break  
                        # Re/Fwd in the second email
                        elif (df.loc[email, 'fwd'] or df.loc[email, 're']):
                            # All options: follow-ups, forward and reply
                            if df.loc[email, 'participants'].intersection(df.loc[item, 'participants']):
                                if df.loc[item, 'content-extra-clean'] in df.loc[email, 'content-extra-clean']:
                                    if df.loc[item, 'content-extra-clean'] != df.loc[email, 'content-extra-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            # Reply
                            if df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                                if df.loc[item, 'participants'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                                    if contains_specific_phrases(df.loc[email, 'content']):
                                        if df.loc[item, 'content-extra-clean'] in df.loc[email, 'content-extra-clean']:
                                            candidate.append(email)
                                            emails_list.remove(email)
                                            break
                                    else:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            """
                            # Forward(1)
                            if df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                                if df.loc[email, 'fwd']:
                                    candidate.append(email)
                                    emails_list.remove(email)
                                    break
                            # Forward(2)
                            if df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                                if df.loc[item, 'content-clean'] in df.loc[email, 'content-clean']:
                                    if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            # Follow-up 
                            if (df.loc[item, 'From'] == df.loc[email, 'From']) and ((df.loc[email, 'recepients'].difference(df.loc[email, 'From'])).intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From']))):
                                if df.loc[item, 'content-clean'] in df.loc[email, 'content-clean']:
                                    if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            # Follow-up or Forward
                            if (df.loc[item, 'From'] == df.loc[email, 'From']):
                                if df.loc[item, 'content-clean'] in df.loc[email, 'content-clean']:
                                    if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            """
                        # Wrong Timing or Deleted Re
                        elif (df.loc[item, 'fwd'] or df.loc[item, 're']):
                            # Deleted Re
                            if df.loc[email, 'participants'].intersection(df.loc[item, 'participants']):
                                if df.loc[item, 'content-extra-clean'] != df.loc[email, 'content-extra-clean']:
                                    if df.loc[item, 'content-extra-clean'] in df.loc[email, 'content-extra-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break                            
                            # Wrog timing -> Shorter time to make sure it's a chain
                            if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) > (60**2)*24:
                                continue
                            # All options: follow-ups, forward and reply
                            if df.loc[email, 'participants'].intersection(df.loc[item, 'participants']):
                                if df.loc[item, 'content-extra-clean'] != df.loc[email, 'content-extra-clean']:
                                    if df.loc[email, 'content-extra-clean'] in df.loc[item, 'content-extra-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            # Reply
                            if df.loc[email, 'participants'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                                if df.loc[item, 'From'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                                    if contains_specific_phrases(df.loc[item, 'content']):
                                        if df.loc[email, 'content-extra-clean'] in df.loc[item, 'content-extra-clean']:
                                            candidate.append(email)
                                            emails_list.remove(email)
                                            break
                                    else:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            """
                            # Forward(1)
                            if df.loc[item, 'From'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                                if df.loc[item, 'fwd']:
                                    candidate.append(email)
                                    emails_list.remove(email)
                                    break
                            # Forward(2)
                            if df.loc[item, 'From'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                                if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                    if df.loc[email, 'content-clean'] in df.loc[item, 'content-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            # Follow-up
                            if (df.loc[item, 'From'] == df.loc[email, 'From']) and ((df.loc[email, 'recepients'].difference(df.loc[email, 'From'])).intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From']))):
                                if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                    if df.loc[email, 'content-clean'] in df.loc[item, 'content-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            # Follow-up or Forward
                            if (df.loc[item, 'From'] == df.loc[email, 'From']):
                                if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                    if df.loc[email, 'content-clean'] in df.loc[item, 'content-clean']:
                                        candidate.append(email)
                                        emails_list.remove(email)
                                        break
                            """
                        else:
                            continue             
            chains[key]['length'].append(len(candidate))
            chains[key]['chains'].append(candidate)
        if len(chains[key]['chains']) == 0:
            del chains[key]                      
            
    total_chains = 0
    length_distribution = {}

    for topic, info in chains.items():
        length_list = info['length']
        total_chains += len(length_list)
        for length in length_list:
            if length in length_distribution:
                length_distribution[length] += 1
            else:
                length_distribution[length] = 1

    print("\nTotal number of chains:", total_chains + len(chains_1) + len(chains_2))

    length_counts = Counter(length_distribution)
    length_counts = sorted(length_counts.items())[:10]

    greater_than_10_count = sum(length_number for length, length_number in length_distribution.items() if isinstance(length, int) and length > 10)

    print("\nLength distribution:")
    print("Length    | Number of Instances")
    print("-----------------------------")
    for length, count in length_counts:
        if length == 1:
            print(f"{length:<9} | {count + len(chains_1):<18}")
        elif length == 2:
            print(f"{length:<9} | {count + len(chains_2):<18}") 
        else:
            print(f"{length:<9} | {count:<18}")
            
    if greater_than_10_count > 0:
        print(">10" + " "*7 + f"| {greater_than_10_count:<18}")

    # Separate dictionaries for different lengths
    length_1 = chains_1.copy()
    length_2 = chains_2.copy()
    length_3 = {}
    length_4 = {}
    length_5 = {}
    length_6 = {}
    length_7 = {}
    length_8 = {}
    length_9 = {}
    length_10 = {}
    # Dictionary for lengths 10+
    length_10_plus = {}

    for topic, info in chains.items():
        length_list = info['length']
        chains_list = info['chains']
        for ind, length in enumerate(length_list):
            if length == 1:
                length_1[f"[{len(length_1)+1}] " + topic] = chains_list[ind]
            elif length == 2:
                length_2[f"[{len(length_2)+1}] " + topic] = chains_list[ind]
            elif length == 3:
                length_3[f"[{len(length_3)+1}] " + topic] = chains_list[ind]
            elif length == 4:
                length_4[f"[{len(length_4)+1}] " + topic] = chains_list[ind]
            elif length == 5:
                length_5[f"[{len(length_5)+1}] " + topic] = chains_list[ind]
            elif length == 6:
                length_6[f"[{len(length_6)+1}] " + topic] = chains_list[ind]
            elif length == 7:
                length_7[f"[{len(length_7)+1}] " + topic] = chains_list[ind]
            elif length == 8:
                length_8[f"[{len(length_8)+1}] " + topic] = chains_list[ind]
            elif length == 9:
                length_9[f"[{len(length_9)+1}] " + topic] = chains_list[ind]
            elif length == 10:
                length_10[f"[{len(length_10)+1}] " + topic] = chains_list[ind]
            else:
                length_10_plus[f"[{len(length_10_plus)+1}] " + topic] = chains_list[ind]

    # Sort by length
    length_10_plus = dict(sorted(length_10_plus.items(), key=lambda x: len(x[1]), reverse=True))

    # Saving results
    with open(paths.CHAINS_1_NEW, 'w') as file:
        json.dump(length_1, file)
    with open(paths.CHAINS_2_NEW, 'w') as file:
        json.dump(length_2, file)
    with open(paths.CHAINS_3, 'w') as file:
        json.dump(length_3, file)
    with open(paths.CHAINS_4, 'w') as file:
        json.dump(length_4, file)
    with open(paths.CHAINS_5, 'w') as file:
        json.dump(length_5, file)
    with open(paths.CHAINS_6, 'w') as file:
        json.dump(length_6, file)
    with open(paths.CHAINS_7, 'w') as file:
        json.dump(length_7, file)
    with open(paths.CHAINS_8, 'w') as file:
        json.dump(length_8, file)
    with open(paths.CHAINS_9, 'w') as file:
        json.dump(length_9, file)
    with open(paths.CHAINS_10, 'w') as file:
        json.dump(length_10, file)
    with open(paths.CHAINS_10_PLUS, 'w') as file:
        json.dump(length_10_plus, file)
        
    print('\nChains are created and stored in the json files!\n')
    
    # For groups to compare with chains  
    with open(paths.SUBJECT_GROUPS, 'r') as file:
        groups = json.load(file)
    # Get length values from alphabetical groups
    length_values = [entry['length'] for entry in groups.values()]

    # Count the occurrences of each length value
    length_counts = Counter(length_values)

    # Create a dictionary to hold the counts of lengths less than or equal to 20
    length_counts = sorted(length_counts.items())[:10]

    # Get count for lengths greater than 20
    greater_than_10_count = sum(1 for length in length_values if isinstance(length, int) and length > 10)

    # Total number
    print(f"\nTo compare: \nTotal number of the subject groups: {len(groups)}\n")
    
    # Print the table
    print("Size distribution:")
    print("Size      | Number of Instances")
    print("-----------------------------")
    for length, count in length_counts:
        print(f"{length:<9} | {count:<18}")
    # Print count for lengths greater than 20
    if greater_than_10_count > 0:
        print(">10" + " "*7 + f"| {greater_than_10_count:<18}")
                    


# For exploration to manually correct the results
"""
# Exploring the long chains
# Print distribution for lengths of the groups and their corresponding  chains to compare the results
for key, value in length_10_plus.items():
    print(extract_heading_name(key), ': ', ordered_groups[extract_heading_name(key)]['length'], ' vs ', len(value))

# Print the distriburion for lengths of the groups and their corresponding  chains to compare the results
import random
checks = random.sample(list(length_10.keys()), 50)
for key in checks:
    print(extract_heading_name(key), ': ', ordered_groups[extract_heading_name(key)]['length'])

# Write chains and groups in a file
for i, key in enumerate(checks):
    print_chains(chains, extract_heading_name(key), '../' + paths.CHECK_CHAINS + f'checking-chain-{i+1}.txt')
    print_groups(ordered_groups, extract_heading_name(key), '../' + paths.CHECK_CHAINS + f'checking-ordered-group-{+1}.txt')  

# Write a chain or a group in a file
print_chains(chains, 'New Mexico Power Plant Project', '../' + paths.CHECK_CHAINS + 'checking-chain.txt')
print_groups(ordered_groups, "Revised ETS Risk Management Procedures and Controls", '../' + paths.CHECK_CHAINS + 'checking-ordered-group.txt')
"""