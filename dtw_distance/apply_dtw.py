import numpy as np
from dtw_numba import dtw_distance, _cosine
import time
import json
import paths

with open(paths.EMB_CHAINS, 'r') as file:
    emb_chains = json.load(file)
    
time_series_set = list(emb_chains.values())

# Convert the innermost lists to numpy arrays
time_series_set = [np.array([np.array(inner_list) for inner_list in outer_list]) for outer_list in time_series_set]


start_time = time.time()
res_numba = dtw_distance(time_series_set, time_series_set)
end_time = time.time()
time_taken = end_time - start_time
print(f"Time taken: {time_taken:.2f} seconds")

np.save('../' + paths.DIST_MATRIX, res_numba)

print("The result is saved in dist-matrix.npy file!")

#loaded_array = np.load('dist-matrix.npy')