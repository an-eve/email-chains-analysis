import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import json
import paths
import ast

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

    all_chains = []

    # Iterate over the paths and load data from each file
    for path_key in paths.__dict__:
        if path_key.startswith('CHAINS_'):
            with open('../' + getattr(paths, path_key), 'r') as file:
                length_data = json.load(file)
                all_chains.append(length_data)

    chains = {}
    
    for chains_length in all_chains:
        for subject, emails_list in chains_length.items():
            chains[f"[{len(chains)+1}] " + extract_heading_name(subject)] = emails_list
    print(f"\nTotal number of chains: {len(chains)}")
    with open('../' +paths.CHAINS, 'w') as file:
        json.dump(chains, file)  

    with open('../' + paths.EMB_MAILS, 'r') as file:
        embedding_dict = json.load(file)

    # Initialize the resulting dictionary
    emb_chains = {}

    # Populate the resulting dictionary
    for chain, emails in chains.items():
        emb_chains[chain] = [embedding_dict[email] for email in emails]

    with open('../' +paths.EMB_CHAINS, 'w') as file:
        json.dump(emb_chains, file)  
