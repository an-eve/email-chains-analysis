import pandas as pd
import numpy as np
import json

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

def generate_key(email):
    participants = set(email['From'])
    for rec in email['To']:
        participants.add(rec)
    #Sorting participants list because as long as we have the same subject\
    #and same participants, it's the same chain, we don't mind who's the\
    #sender and who recieves the message
    participants = sorted(participants)
    key = ' '.join(participants)
    key = ' '.join([email['Subject'] + ' | ', key])
    # removing spaces and unwated char from beggining of the key
    #We remove "Re:" because we want the same identification for both send \
    #and reply
    while (key[0] == ' '):
        key = key[1:]
    return key

def chain_info_from_frame(frame):
    chain_identifier_vs_length = {}
    for index, mail in frame.iterrows():
        if not is_nan(mail["Subject"]):
            mail_key = generate_key(mail)
        else:
            continue
        if not "Re:" in mail_key[:5]:
            continue
        if mail_key in chain_identifier_vs_length:
            chain_identifier_vs_length[mail_key]["length"] += 1
            chain_identifier_vs_length[mail_key]["ids"].append(mail['file'])
        else:
            chain_identifier_vs_length[mail_key] = {}
            chain_identifier_vs_length[mail_key]["length"] = 2
            chain_identifier_vs_length[mail_key]["ids"] = [mail['file']]
    return chain_identifier_vs_length

##################################################################
if __name__ == "__main__":
    
    # Uploading data
    file_path = 'data/no-identical-mails-data.csv'
    df = pd.read_csv(file_path)

    # Impossible to build a chain without knowinf the recepients
    df = df.dropna(subset=['To'])
    print(f"Missing values in the dataframe:\n{df.isna().sum()}\n")

    # Splitting email adresses
    df['From'] = df['From'].map(split_email_addresses)
    df['To'] = df['To'].map(split_email_addresses)
    df['Cc'] = df['Cc'].map(split_email_addresses)
    df['Bcc'] = df['Bcc'].map(split_email_addresses)

    print(f"\nThe dataset's size after cleaning: {df.shape}\n")
    print(f"\nFirst rows after cleaning:\n{df.head()}\n")

    chains = chain_info_from_frame(df)

    print(f"Number of chains detected: {len(chains)}")

    # Savin results
    with open('data/chains.json', 'w') as file:
        json.dump(chains, file)

    # Filter the data for chains with length greater than 4
    filtered_chains = {key: value for key, value in chains.items() if value['length'] > 4}

    with open('data/chains_greater_4.json', "w") as json_file:
        json.dump(filtered_chains, json_file, indent=4)
        
    print("\nChains files created successfully!")