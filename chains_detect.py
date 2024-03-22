import pandas as pd
import numpy as np
import json
import time
import re

def has_no_prefix(string):
    return not re.search(r'\b(?:Re:|RE:|FW:|Fw:|Fwd:|FWD:)\b', string)

def remove_prefixes(subject):
    # Define a regular expression pattern to match prefixes
    prefix_pattern = re.compile(r'(Re:|Fw:|Fwd:)', flags=re.IGNORECASE)
    # Replace prefixes and square brackets with an empty string
    subject = re.sub(prefix_pattern, '', subject)
    subject = re.sub(r'[\[\]]', '', subject)
    return subject

def remove_spaces(subject):
    subject = subject.strip()
    subject = ' '.join(subject.split())
    return subject

def is_nan(value):
    return isinstance(value, float) and np.isnan(value)

def split_email_addresses(line):
    '''To separate multiple email addresses or names'''
    if not is_nan(line):
        addrs = line.split(',')
        addrs = frozenset(map(lambda x: x.strip(), addrs))
    else:
        addrs = None
    return addrs

def generate_keys(email):
    participants = set(email['From'])
    for rec in email['To']:
        participants.add(rec)
    
    if is_nan(email["Subject"]):
        subject = ""
    else:
        subject = email['Subject']
    subject = remove_prefixes(subject)
    subject = remove_spaces(subject)
    return (subject, frozenset(participants))

# I don't like the function :( It took 40 min to run
def chain_info_from_frame(frame):
    chain_dict = {}
    for index, mail in frame.iterrows():
        mail_keys = generate_keys(mail)
        if mail_keys in chain_dict:
            chain_dict[mail_keys]["length"] += 1
            chain_dict[mail_keys]["ids"].add(mail['file'])
        else:
            flag = False
            chain_dict_cpy = chain_dict.copy()
            for key in chain_dict_cpy:
                if (key[0] == mail_keys[0]) and (mail_keys[0]!=""):
                    if key[1].intersection(mail_keys[1]):
                        new_key = (key[0], frozenset(key[1].union(mail_keys[1])))
                        chain_dict[new_key] = chain_dict.pop(key)
                        chain_dict[new_key]["length"] += 1
                        chain_dict[new_key]["ids"].add(mail['file'])  
                        flag = True
                        break                     
                elif (key[0] == mail_keys[0]) and (mail_keys[0]==""):
                    if len(key[1].intersection(mail_keys[1])) >= 2:
                        new_key = (key[0], frozenset(key[1].union(mail_keys[1])))
                        chain_dict[new_key] = chain_dict.pop(key)
                        chain_dict[new_key]["length"] += 1
                        chain_dict[new_key]["ids"].add(mail['file'])  
                        flag = True                     
                        break
            if not flag:
                chain_dict[mail_keys] = {}
                chain_dict[mail_keys]["length"] = 1
                chain_dict[mail_keys]["ids"] = {mail['file']}     
    return chain_dict

##################################################################
if __name__ == "__main__":
    
    # Uploading data
    file_path = 'data/no-identical-mails-data.csv' # 'data/clean-mails-data-allen-p.csv' 
    df = pd.read_csv(file_path)

    # Impossible to build a chain without knowinf the recepients
    df = df.dropna(subset=['To'])
    print(f"Missing values in the dataframe:\n{df.isna().sum()}\n")

    # Splitting email adresses
    df['From'] = df['From'].map(split_email_addresses)
    df['To'] = df['To'].map(split_email_addresses)
    df['Cc'] = df['Cc'].map(split_email_addresses)
    df['Bcc'] = df['Bcc'].map(split_email_addresses)

    print(f"\nThe dataset's size after cleaning: {df.shape}")
    print(f"First rows after cleaning:\n {df.head()}")
    
    # Without Re and Fw
    s = 0
    for index, mail in df.iterrows():
        if not is_nan(mail["Subject"]):
            s += int(has_no_prefix(mail["Subject"]))
    print(f"Number of emails without 'Re' and 'Fw': {s}\n")
    

    start_time = time.time()
    chains = chain_info_from_frame(df)
    end_time = time.time()

    print(f"\nNumber of chains detected: {len(chains)}\n")
    
    # Filter the data for chains with length greater than 1
    filtered_chains = {key: value for key, value in chains.items() if value['length'] > 1}
    print(f"\nNumber of chains longer than 1: {len(filtered_chains)}\n")
    
    # Filter the data for chains with length greater than 2
    filtered_chains = {key: value for key, value in chains.items() if value['length'] > 2}
    print(f"\nNumber of chains longer than 2: {len(filtered_chains)}\n")
        
    chains_to_json = {" | ".join([key[0], f"Participants: {len(key[1])}"]): {"length": value["length"], "ids": list(value["ids"])}  for key, value in chains.items()}

    # Saving results
    chains_path = 'data/chains.json'
    with open(chains_path, 'w') as file:
        json.dump(chains_to_json, file)


    print("\nChains file created successfully!")
    print("Time taken:", end_time - start_time, "seconds")

