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
        
def add_clean_text(text):
    '''Cleans the text content for later processing, removing unnecessary characters and spaces.
    
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

def contains_specific_phrases(text):
    '''Checks if the text contains specific phrases case-insensitively using regular expressions.

    Args:
    - text (str): The text to be checked.

    Returns:
    - bool: True if the text contains any of the specified phrases (case-insensitive), False otherwise.
    '''
    return bool(re.search(r'Forwarded by|Original Message|\(Revision: \d\)', text, flags=re.IGNORECASE))

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
    
    with open('../'+paths.CHAINS_1, 'r') as file:
        chains_1 = json.load(file)
    with open('../'+paths.CHAINS_2, 'r') as file:
        chains_2 = json.load(file)
        
    with open('../'+paths.SUBJECT_GROUPS_3_PLUS, 'r') as file:
        groups = json.load(file)
        
    df = pd.read_csv('../'+paths.DATA_CLEAN_SUBJECT)
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

    with open('../'+paths.ORDERED_GROUPS, 'w') as file:
        json.dump(ordered_groups, file)
        
    chains = {}
    for key, value in list(ordered_groups.items()):
        chains[key]={}
        chains[key]['length'] = []
        chains[key]['chains'] = []
        emails_list = (ordered_groups[key]['ids']).copy()
        while len(emails_list) > 1:
            candidate = []
            candidate.append(emails_list.pop(0))
            emails_list_cpy = emails_list.copy()
            for email in emails_list_cpy:
                candidate_cpy = candidate.copy()
                for item in candidate_cpy:
                    if df.loc[email, 'From'].intersection(df.loc[item, 'recepients']):
                        if df.loc[item, 're'] or df.loc[item, 'fwd']:
                            if not (df.loc[email, 'fwd'] or df.loc[email, 're']):
                                continue
                        candidate.append(email)
                        emails_list.remove(email)
                        break
            if len(candidate) > 1:
                chains[key]['length'].append(len(candidate))
                chains[key]['chains'].append(candidate)
        if len(chains[key]['chains']) == 0:
            del chains[key]
                
        
    chains = {}
    for key, value in list(ordered_groups.items()):
        chains[key]={}
        chains[key]['length'] = []
        chains[key]['chains'] = []
        emails_list = (ordered_groups[key]['ids']).copy()
        while len(emails_list) > 1:
            candidate = []
            candidate.append(emails_list.pop(0))
            emails_list_cpy = emails_list.copy()
            for email in emails_list_cpy:
                candidate_cpy = candidate.copy()
                for item in candidate_cpy:
                    if df.loc[email, 'From'].intersection(df.loc[item, 'recepients']):
                        if not (df.loc[email, 'fwd'] or df.loc[email, 're']):
                            continue
                         # Reply or Forward
                        if not df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                            # Follow-up
                            if not ((df.loc[item, 'From'] == df.loc[email, 'From']) and ((df.loc[email, 'recepients'].difference(df.loc[email, 'From'])).intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])))):
                                continue
                        if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) > (60**2)*24*30*3:
                            continue
                        candidate.append(email)
                        emails_list.remove(email)
                        break
            if len(candidate) > 1:
                chains[key]['length'].append(len(candidate))
                chains[key]['chains'].append(candidate)
        if len(chains[key]['chains']) == 0:
            del chains[key]      
            
  
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
                for item in candidate_cpy:
                    # Time period regulation
                    if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) > (60**2)*24*30*2:
                        continue 
                    # Re/Fwd neither in the first email, nor in the second (follow-ups are difficult 
                    # to detect, they could be mixed up with 2 separate emails with the same subject)
                    if not (df.loc[email, 're'] or df.loc[item, 're'] or df.loc[email, 'fwd'] or df.loc[item, 'fwd']):
                        # Shorter time to make sure it's a chain
                        if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) > (60**2)*24*7:
                            continue
                        # Forward and (maybe?) Reply
                        if (df.loc[item, 'From'] == df.loc[email, 'From']) and (df.loc[item, 'content-clean'] in df.loc[email, 'content-clean']) and contains_specific_phrases(df.loc[email, 'content-clean']):
                            if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                        # Reply
                        if df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                            if df.loc[item, 'From'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                                candidate.append(email)
                                emails_list.remove(email)
                                break    
                    # Re/Fwd in the second email
                    elif (df.loc[email, 'fwd'] or df.loc[email, 're']):
                        # Reply
                        if df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                            if df.loc[item, 'From'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                        # Forward
                        if df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                            if df.loc[email, 'fwd']:
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                        # Another case of Forward
                        if (df.loc[item, 'From'] == df.loc[email, 'From']) and df.loc[email, 'fwd']:
                            if add_clean_text(df.loc[item, 'content']) != add_clean_text(df.loc[email, 'content']):
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                        # Follow-up
                        if (df.loc[item, 'From'] == df.loc[email, 'From']) and ((df.loc[email, 'recepients'].difference(df.loc[email, 'From'])).intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From']))):
                            if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                # Avoiding time errors emails
                                if (abs(df.loc[item, 'date-timestamp'] - df.loc[email, 'date-timestamp'])/(60*60)) % 1 == 0:
                                    if (add_clean_text(df.loc[item, 'content']) == add_clean_text(df.loc[email, 'content'])) or (df.loc[item, 'Content-Type'] != df.loc[email, 'Content-Type']):
                                        emails_list.remove(email)
                                        break 
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                    # Wrong Timing
                    elif (df.loc[item, 'fwd'] or df.loc[item, 're']):
                        # Shorter time to make sure it's a chain
                        if abs(df.loc[email, 'date-timestamp'] - df.loc[item, 'date-timestamp']) > (60**2)*24:
                            continue
                        # Reply
                        if df.loc[email, 'From'].intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From'])):
                            if df.loc[item, 'From'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                        # Forward
                        if df.loc[item, 'From'].intersection(df.loc[email, 'recepients'].difference(df.loc[email, 'From'])):
                            if df.loc[item, 'fwd']:
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                        # Another case of Forward
                        if (df.loc[item, 'From'] == df.loc[email, 'From']) and df.loc[item, 'fwd']:
                            if add_clean_text(df.loc[item, 'content']) != add_clean_text(df.loc[email, 'content']):
                                candidate.append(email)
                                emails_list.remove(email)
                                break
                        # Follow-up
                        if (df.loc[item, 'From'] == df.loc[email, 'From']) and ((df.loc[email, 'recepients'].difference(df.loc[email, 'From'])).intersection(df.loc[item, 'recepients'].difference(df.loc[item, 'From']))):
                            if df.loc[item, 'content-clean'] != df.loc[email, 'content-clean']:
                                # Avoiding time errors emails
                                if (abs(df.loc[item, 'date-timestamp'] - df.loc[email, 'date-timestamp'])/(60*60)) % 1 == 0:
                                    if (add_clean_text(df.loc[item, 'content']) == add_clean_text(df.loc[email, 'content'])) or (df.loc[item, 'Content-Type'] != df.loc[email, 'Content-Type']):
                                        emails_list.remove(email)
                                        break  
                                candidate.append(email)
                                emails_list.remove(email)
                                break
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

    print("Total number of chains:", total_chains + len(chains_1) + len(chains_2))

    length_counts = Counter(length_distribution)
    length_counts = sorted(length_counts.items())[:10]

    greater_than_10_count = sum(length_number for length, length_number in length_distribution.items() if isinstance(length, int) and length > 10)

    print("Length distribution:")
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
    length_1 = {}
    length_2 = {}
    length_2 = {}
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
                chains_1[f"[{len(chains_1)+1}] " + topic] = chains_list[ind]
            elif length == 2:
                chains_2[f"[{len(chains_2)+1}] " + topic] = chains_list[ind]
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
    

    with open('../' + paths.CHAINS_1_NEW, 'w') as file:
        json.dump(chains_1, file)
    with open('../' + paths.CHAINS_2_NEW, 'w') as file:
        json.dump(chains_2, file)
    with open('../' + paths.CHAINS_3, 'w') as file:
        json.dump(length_3, file)
    with open('../' + paths.CHAINS_4, 'w') as file:
        json.dump(length_4, file)
    with open('../' + paths.CHAINS_5, 'w') as file:
        json.dump(length_5, file)
    with open('../' + paths.CHAINS_6, 'w') as file:
        json.dump(length_6, file)
    with open('../' + paths.CHAINS_7, 'w') as file:
        json.dump(length_7, file)
    with open('../' + paths.CHAINS_8, 'w') as file:
        json.dump(length_8, file)
    with open('../' + paths.CHAINS_9, 'w') as file:
        json.dump(length_9, file)
    with open('../' + paths.CHAINS_10, 'w') as file:
        json.dump(length_10, file)
    with open('../' + paths.CHAINS_10_PLUS, 'w') as file:
        json.dump(length_10_plus, file)
    
    # For groups to compare with chains  
    with open('../'+paths.SUBJECT_GROUPS, 'r') as file:
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
    print(f"\nTo compare: \nTotal number of the subject groups: {len(groups)}\n\n")
    
    # Print the table
    print("Size distribution:")
    print("Size      | Number of Instances")
    print("-----------------------------")
    for length, count in length_counts:
        print(f"{length:<9} | {count:<18}")
    # Print count for lengths greater than 20
    if greater_than_10_count > 0:
        print(">10" + " "*7 + f"| {greater_than_10_count:<18}")
                    

# This exploration I performed to manually correct the automatic results

# Exploring the long chains
# Print distribution for lengths of the groups and their corresponding  chains to compare the results
for key, value in length_10_plus.items():
    print(extract_heading_name(key), ' ', ordered_groups[extract_heading_name(key)]['length'], ': ', len(value))

print_chains(chains, "WorldCom Calling Card", '../' + paths.CHECK_CHAINS + 'checking-chain.txt')
print_groups(ordered_groups, "WorldCom Calling Card", '../' + paths.CHECK_CHAINS + 'checking-ordered-group.txt')

# Results:
# Rebuild:
# 'apb checkout', 'natsource checkout', 'apb', 'natsource', 'tfs' -> text of one should be in another to build the chain, 
# father without RE and FWD, child with RE or FWD
#
# <no subject>  -> to remove
# 
# 'A Christmas Tasters', 'Enfolio Contract with CPS', -> take the whole order group instead of the chains result
#
# 'Centana', 'NETCO', "Master Netting Agreement Assignments", "WorldCom Calling Card" -> 1-2 days time gap instead of 2 months, father without RE and FWD, child with RE or FWD
#
# 'Cabot Oil & Gas Marketing Corporation', -> everything is ok
# 'One more try', 'Thanksgiving', 'Organization Announcement', 'How good is Temptation Island 2' -> everything is ok
# 'hi!', "I'm Leaving Enron"  -> everything is ok

# Same for the length of 10
for key, value in length_10.items():
    print(extract_heading_name(key), ' ', ordered_groups[extract_heading_name(key)]['length'], ': ', len(value))



for i, key in enumerate(list(ordered_groups.keys())[:60]):
    print_groups(ordered_groups, key, '../'+paths.CHECK_CHAINS+f'ordered-group-{i+1}.txt')
for i, key in enumerate(list(chains.keys())[:30]):
    print_chains(chains, key, '../'+paths.CHECK_CHAINS+f'chain-{i+1}.txt')
    

