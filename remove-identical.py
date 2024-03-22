import pandas as pd

# Uploading data
file_path = 'data/parsed-mails-data.csv'
df = pd.read_csv(file_path)

print(f"\nThe dataset's size with identical: {df.shape}\n")

# List of columns to ignore while checking for duplicates
columns_to_ignore = ['file', 'Message-ID', 'X-Folder', 'X-Origin', 'X-FileName', 'user']

# Create a new dataframe excluding the columns to ignore
df_subset = df.drop(columns=columns_to_ignore)

# Drop duplicate rows from the subset dataframe and the dataframe itself
df_subset_no_identical = df_subset.drop_duplicates()
df_no_identical = df[df.index.isin(df_subset_no_identical.index)]

# Reset indexes
df_no_identical.reset_index(drop=True, inplace=True)

print(f"\nThe dataset's size without identical: {df_no_identical.shape}\n")

output_path = 'data/no-identical-mails-data.csv'
df_no_identical.to_csv(output_path, index=False)
print("\nCSV file created successfully!")