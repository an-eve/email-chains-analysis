import numpy as np
import json
import hdbscan
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.manifold import MDS
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score
import seaborn as sns
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

submatrix = np.load('submatrix.npy')

# distribution
distances = submatrix.flatten()

plt.hist(distances, bins=30, edgecolor='k', alpha=0.7)
plt.title('Distribution of Distance Values')
plt.xlabel('Distance')
plt.ylabel('Frequency')
plt.show()

#heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(submatrix, cmap='viridis')
plt.title('Distance Matrix Heatmap')
plt.show()

#dendrogram
linked = linkage(submatrix, 'single')

plt.figure(figsize=(10, 7))
dendrogram(linked, orientation='top', distance_sort='descending', show_leaf_counts=True)
plt.title('Hierarchical Clustering Dendrogram')
plt.show()

# MDS
mds = MDS(n_components=2, dissimilarity='precomputed')
mds_coords = mds.fit_transform(submatrix)

plt.scatter(mds_coords[:, 0], mds_coords[:, 1])
plt.title('MDS Plot')
plt.xlabel('Component 1')
plt.ylabel('Component 2')
plt.show()


#dbscan
db = DBSCAN(metric='precomputed')
labels = db.fit_predict(submatrix)

# Plotting clusters using MDS for visualization
mds_coords = mds.fit_transform(submatrix)
plt.scatter(mds_coords[:, 0], mds_coords[:, 1], c=labels)
plt.title('DBSCAN Clustering')
plt.xlabel('Component 1')
plt.ylabel('Component 2')
plt.show()

# nn
k = 3  # For DBSCAN, the value of k is typically set to min_samples-1
neighbors = NearestNeighbors(n_neighbors=k)
neighbors_fit = neighbors.fit(submatrix)
distances, indices = neighbors_fit.kneighbors(submatrix)

# Sort the distances to the k-th nearest neighbor
distances = np.sort(distances[:, k-1])[:100]

plt.plot(distances)
plt.title('k-Distance Graph')
plt.xlabel('Points sorted by distance')
plt.ylabel(f'Distance to {k}-th nearest neighbor')
plt.show()

from sklearn.cluster import DBSCAN

# Selected parameters
eps = 0.6  # replace with the value you found suitable
min_samples = 5

# Run DBSCAN
db = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
labels = db.fit_predict(submatrix)

# Plotting clusters using MDS for visualization
from sklearn.manifold import MDS
mds = MDS(n_components=2, dissimilarity='precomputed')
mds_coords = mds.fit_transform(submatrix)

plt.scatter(mds_coords[:, 0], mds_coords[:, 1], c=labels, cmap='rainbow')
plt.title('DBSCAN Clustering')
plt.xlabel('Component 1')
plt.ylabel('Component 2')
plt.show()

# grid search
# Define a range of values for eps and min_samples
eps_values = np.linspace(0.01, 1.0, 10)
min_samples_values = range(2, 10)

best_score = -1
best_params = {'eps': None, 'min_samples': None}

for eps in eps_values:
    for min_samples in min_samples_values:
        db = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
        labels = db.fit_predict(submatrix)
        
        # Check if there are at least 2 clusters (excluding noise)
        unique_labels = set(labels)
        unique_labels.discard(-1)  # Remove noise label if present
        
        if len(unique_labels) > 1:
            # Mask noise points
            mask = labels != -1
            if np.sum(mask) > 1:  # Ensure there's more than one non-noise point
                score = silhouette_score(submatrix[mask][:, mask], labels[mask], metric='precomputed')
                if score > best_score:
                    best_score = score
                    best_params['eps'] = eps
                    best_params['min_samples'] = min_samples

print(f"Best params: eps = {best_params['eps']}, min_samples = {best_params['min_samples']}")
print(f"Best silhouette score: {best_score}")

# Optional: Run DBSCAN with best params and visualize the result
db = DBSCAN(eps=best_params['eps'], min_samples=best_params['min_samples'], metric='precomputed')
labels = db.fit_predict(submatrix)

mds = MDS(n_components=2, dissimilarity='precomputed')
mds_coords = mds.fit_transform(submatrix)

plt.scatter(mds_coords[:, 0], mds_coords[:, 1], c=labels, cmap='rainbow')
plt.title('DBSCAN Clustering with Best Params')
plt.xlabel('Component 1')
plt.ylabel('Component 2')
plt.show()


# Instantiate and fit DBSCAN with the precomputed distance matrix
dbscan = DBSCAN(eps=1, min_samples=7, metric='precomputed')
labels = dbscan.fit_predict(submatrix)

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