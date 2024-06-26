import pandas as pd
import json
import paths

def remove_duplicates_and_merge():
    # Shows if time is taken into consideration or not 
    time_flag = True
    
    # Read the DataFrame from the CSV file
    df = pd.read_csv(paths.PARSED_DATA)

    # Display the size of the dataset with duplicates
    print(f"\nThe dataset's size with duplicates: {df.shape}\n")
    
    # Count the number of NaNs for each column
    nan_counts = df.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")
    df = df.fillna('')

    if time_flag:
        # Columns to ignore when identifying duplicates
        columns_to_ignore = ['file', 'Message-ID', 'date-timestamp', 'Date', 'X-From', 'X-To', 'X-cc', 'X-bcc','X-Folder', 'X-Origin', 'X-FileName', 'user', 'content']
        
        # Remove duplicates based on a subset of columns
        df_subset = df.drop(columns=columns_to_ignore)
        df_subset_no_identical = df_subset.drop_duplicates()

        # Filter the original DataFrame to keep only non-duplicate rows
        df_no_identical = df[df.index.isin(df_subset_no_identical.index)]

        # Load indexes of rows to keep from the identification process
        with open(paths.INDEXES_KEEP, 'r') as f:
            indexes_to_keep = json.load(f)

        # Filter rows to keep from the original DataFrame
        df_from_to_keep = df.loc[indexes_to_keep]

        # Concatenate non-duplicate rows with identified rows to keep
        df_no_identical = pd.concat([df_no_identical, df_from_to_keep])

        # Reset indexes
        df_no_identical.reset_index(drop=True, inplace=True)
    else:
        # Columns to ignore when identifying duplicates
        columns_to_ignore = ['file', 'Message-ID', 'X-From', 'X-To', 'X-cc', 'X-bcc','X-Folder', 'X-Origin', 'X-FileName', 'user', 'content']

        # Remove duplicates based on a subset of columns
        df_subset = df.drop(columns=columns_to_ignore)
        df_subset_no_identical = df_subset.drop_duplicates()

        # Filter the original DataFrame to keep only non-duplicate rows
        df_no_identical = df[df.index.isin(df_subset_no_identical.index)]

        # Reset indexes
        df_no_identical.reset_index(drop=True, inplace=True)     

    # Display the size of the dataset without duplicates
    print(f"\nThe dataset's size without duplicates: {df_no_identical.shape}\n")

    # Save the cleaned DataFrame to a new CSV file
    df_no_identical.to_csv(paths.DATA_NO_DUPLICATE, index=False)
    print("\nCSV file created successfully!")

if __name__ == "__main__":
    remove_duplicates_and_merge()
