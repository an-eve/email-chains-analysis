import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import time
from tqdm import tqdm
import paths


def find_identical_rows(df, row_index):
    """
    Find indices of rows in a DataFrame that are identical to a specified row.

    Args:
    - df (pandas.DataFrame): The DataFrame to search for identical rows.
    - row_index (int): The index of the row to compare against.

    Returns:
    - list: A list of indices of rows in the DataFrame that are identical to the specified row.
    """
    identical_rows_indices = df[df.eq(df.loc[row_index])].dropna().index.tolist()
    identical_rows_indices.remove(row_index)
    return identical_rows_indices


def main():
    df = pd.read_csv(paths.PARSED_DATA) 
    
    # Count the number of NaNs for each column
    nan_counts = df.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")
    
    identical_mapping_exist = True
    
    if not identical_mapping_exist:
        df = df.fillna('')

        # First Approach: Take time into consideration when searching for duplicate rows
        columns_to_ignore_with_time = ['file', 'Message-ID', 'date-timestamp', 'X-From', 'X-To', 'X-cc', 'X-bcc','X-Folder', 'X-Origin', 'X-FileName', 'user', 'content']
        df_subset_with_time = df.drop(columns=columns_to_ignore_with_time)
        df_subset_no_identical_with_time = df_subset_with_time.drop_duplicates()
        df_no_identical_with_time = df[df.index.isin(df_subset_no_identical_with_time.index)]
        dropped_rows_indices_with_time = df.index.difference(df_subset_no_identical_with_time.index)

        # Second Approach: Don't take time into consideration when searching for duplicate rows
        columns_to_ignore_without_time = ['file', 'Message-ID', 'date-timestamp', 'Date', 'X-From', 'X-To', 'X-cc', 'X-bcc','X-Folder', 'X-Origin', 'X-FileName', 'user', 'content']
        df_subset_without_time = df.drop(columns=columns_to_ignore_without_time)
        df_subset_no_identical_without_time = df_subset_without_time.drop_duplicates()
        df_no_identical_without_time = df[df.index.isin(df_subset_no_identical_without_time.index)]
        dropped_rows_indices_without_time = df.index.difference(df_subset_no_identical_without_time.index)

        # Exploring which rows should be removed
        dropped_rows_indices_to_explore = list(set(dropped_rows_indices_without_time).difference(set(dropped_rows_indices_with_time)))
        df_subset_to_explore = df_subset_without_time[df_subset_without_time.index.isin(df_subset_no_identical_with_time.index)]

        # Create a dictionary to map dropped rows indices to identical rows indices
        dropped_to_identical_mapping = {}
        start_time = time.time()
        for dropped_index in tqdm(dropped_rows_indices_to_explore, desc="Processing"):
            dropped_to_identical_mapping[dropped_index] = find_identical_rows(df_subset_to_explore, dropped_index)
            # Calculate the remaining time
            remaining_iterations = len(dropped_rows_indices_to_explore) - (dropped_rows_indices_to_explore.index(dropped_index) + 1)
            if remaining_iterations % 100 == 0:
                time_per_iteration = (time.time() - start_time)/(len(dropped_rows_indices_to_explore)-remaining_iterations)  
                remaining_time = remaining_iterations * time_per_iteration
                print(f"Estimated time remaining: {remaining_time/60:.2f} minutes")

        # Saving results
        with open(paths.IDENTICAL_MAPPING, 'w') as file:
            json.dump(dropped_to_identical_mapping, file)
        print("Mapping between dropped rows and identical rows is created!")
        end_time = time.time()
        print("Time taken:", end_time - start_time, "seconds")

    else:
        with open(paths.IDENTICAL_MAPPING, 'r') as file:
            dropped_to_identical_mapping = json.load(file)

    abs_diff_list = []
    for key, value_list in dropped_to_identical_mapping.items():
        diff_list = []
        for value in value_list:
            diff_list.append(abs(df.loc[int(key), 'date-timestamp']-df.loc[int(value), 'date-timestamp']) / (60 * 60 ))
        abs_diff_list.append(np.min(diff_list))

    # Explore distribution for the difference smaller than 24 hours
    elem_smaller_than_24 = [elem for elem in abs_diff_list if elem < 24]
    count_smaller_than_24 = len(elem_smaller_than_24)
    print("Number of elements smaller than 24:", count_smaller_than_24)

    # Plot the overall distribution
    plt.hist(elem_smaller_than_24, bins=50)
    plt.title('Overall Distribution of Absolute Differences')
    plt.xlabel('Hours')
    plt.ylabel('Frequency')
    plt.savefig(paths.IMAGES + 'Diff_Smaller_24_Dist.png')
    print("Distribution plot for time differences is saved in the image folder!")

    # Keep those which are either greater than 10 hours and don't have the difference with a zero fractional part or just greater than 20 hours (almost one day)
    indexes_to_keep = [index for index, value in enumerate(abs_diff_list) if (value % 1 != 0 and value > 10) or value > 20]
    count_to_keep = len(indexes_to_keep)
    print("Number of elements to keep:", count_to_keep)

    indexed_df = list(dropped_to_identical_mapping.keys())
    indexes_df_to_keep = [int(indexed_df[index]) for index in indexes_to_keep]

    with open(paths.INDEXES_KEEP, 'w') as file:
        json.dump(indexes_df_to_keep, file)

    print("Indexes to keep are saved!")

if __name__ == "__main__":
    main()
    
  
# To print the messages with an error in time after creating the "dropped_to_identical_mapping" dictionary
"""
example_path = '../' + paths.EXAMPLE_IDENTICAL_DIFFERENT_TIME

with open(example_path, 'w') as combined_file:
    combined_file.write('FIRST EXAMPLE:' + '\n'*3)
    with open('../' + df.loc[393217, 'file'], 'r') as file:
        combined_file.write('Message:' + '\n'*2)
        combined_file.write(file.read())
    with open('../' + df.loc[380661, 'file'], 'r') as file:
        combined_file.write('\n'*3 + 'Identical Message:' + '\n'*2)
        combined_file.write(file.read())
    combined_file.write('\n'*3+ '#'*60 + '\n'*2)
    combined_file.write('\n'*2 + 'SECOND EXAMPLE:' + '\n'*3)
    with open('../' + df.loc[491537, 'file'], 'r') as file:
        combined_file.write('Message:' + '\n'*2)
        combined_file.write(file.read())
    with open('../' + df.loc[491442, 'file'], 'r') as file:
        combined_file.write('\n'*3 + 'Identical Message:' + '\n'*2)
        combined_file.write(file.read())
        combined_file.write('\n'*3+ '#'*60 + '\n'*2)
    combined_file.write('\n'*2 + 'THIRD EXAMPLE:' + '\n'*3)
    with open('../' + df.loc[393235, 'file'], 'r') as file:
        combined_file.write('Message:' + '\n'*2)
        combined_file.write(file.read())
    with open('../' + df.loc[374765, 'file'], 'r') as file:
        combined_file.write('\n'*3 + 'Identical Message:' + '\n'*2)
        combined_file.write(file.read())
    combined_file.write('\n'*2 + 'Foorth EXAMPLE:' + '\n'*3)
    with open('../' + df.loc[491548, 'file'], 'r') as file:
        combined_file.write('Message:' + '\n'*2)
        combined_file.write(file.read())
    with open('../' + df.loc[491481, 'file'], 'r') as file:
        combined_file.write('\n'*3 + 'Identical Message:' + '\n'*2)
        combined_file.write(file.read())
""" 

