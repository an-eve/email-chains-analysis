import numpy as np
import dask.array as da
import json
import hdbscan
from sklearn.cluster import DBSCAN
import paths

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
            for ind, file_path in enumerate(dictionary[key]):
                with open('../' + file_path, 'r') as file:
                    combined_file.write('\n'*3 + '#' * 10 + ' ' * 15 + f'Message {ind+1}' + ' ' * 16 + '#' * 10 + '\n'*3)
                    combined_file.write(file.read())
        print(f"Text from files combined and saved to {combined_path}")
    else:
        print("Key not found in the dictionary.")


dist_matrix = np.load('../' + paths.DIST_MATRIX)
dist_matrix.shape
np.fill_diagonal(dist_matrix, 0)

# Instantiate and fit DBSCAN with the precomputed distance matrix
dbscan = DBSCAN(eps=0.5, min_samples=5, metric='precomputed')
labels = dbscan.fit_predict(dist_matrix)

labels = np.array(labels)
unique_values, counts = np.unique(labels, return_counts=True)

for value, counts in zip(unique_values, counts):
    print(f"Label: {value}, Count: {counts}")

with open('../' + 'data/chains/chains.json', 'r') as file:
    chains = json.load(file)
    
chains_clusters = {}

for index, (key, values) in enumerate(chains.items()):
    chains_clusters[key]={}
    chains_clusters[key]['mails'] = values
    chains_clusters[key]['class'] = float(labels[index])
    
with open('../' +'data/distance_matrix/chains_clusters.json', 'w') as file:
    json.dump(chains_clusters, file)  

with open('../' +'data/distance_matrix/chains_clusters.json', 'r') as file:
    chains_clusters = json.load(file)  
    
chains_clusters = dict(sorted(chains_clusters.items(), key=lambda x: x[1]["class"], reverse=True))

print_chains(chains, '[11867] matching funds', '../' + paths.CHECK_CHAINS + 'cluster-3.txt')