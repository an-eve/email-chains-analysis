import numpy as np
import json
import hdbscan
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.manifold import MDS
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score
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

# distribution
plt.hist(dist_matrix.flatten(), bins=30, edgecolor='k', alpha=0.7)
plt.title('Distribution of Distance Values')
plt.xlabel('Distance')
plt.ylabel('Frequency')
plt.show()

# grid search
# Define a range of values for eps and min_samples
eps_values = np.linspace(0.1, 1.0, 4)
min_samples_values = range(2, 8)

best_score = -1
best_params = {'eps': None, 'min_samples': None}

for eps in eps_values:
    for min_samples in min_samples_values:
        db = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
        labels = db.fit_predict(dist_matrix)
        
        # Check if there are at least 2 clusters (excluding noise)
        unique_labels = set(labels)
        unique_labels.discard(-1)  # Remove noise label if present
        
        if len(unique_labels) > 1:
            # Mask noise points
            mask = labels != -1
            if np.sum(mask) > 1:  # Ensure there's more than one non-noise point
                score = silhouette_score(dist_matrix[mask][:, mask], labels[mask], metric='precomputed')
                if score > best_score:
                    best_score = score
                    best_params['eps'] = eps
                    best_params['min_samples'] = min_samples

print(f"Best params: eps = {best_params['eps']}, min_samples = {best_params['min_samples']}")
print(f"Best silhouette score: {best_score}")

# Optional: Run DBSCAN with best params and visualize the result
db = DBSCAN(eps=best_params['eps'], min_samples=best_params['min_samples'], metric='precomputed')
labels = db.fit_predict(dist_matrix)








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

print_chains(chains, '[15289] Lunch', '../' + paths.CHECK_CHAINS + 'cluster-5.txt')