import pandas as pd
import re
import paths

def remove_prefixes(subject):
    """
    Remove common email subject prefixes (e.g., "Re:", "Fw:", "Fwd:") and square brackets from the subject.

    Args:
    - subject (str): The subject line of an email.

    Returns:
    - str: The cleaned subject line with prefixes and square brackets removed.
    """
    prefix_pattern = re.compile(r'(Re:|Fw:|Fwd:)', flags=re.IGNORECASE)
    subject = re.sub(prefix_pattern, '', subject)
    subject = re.sub(r'[\[\]]', '', subject)
    return subject

def remove_spaces(subject):
    """
    Remove leading, trailing, and extra spaces within the subject.

    Args:
    - subject (str): The subject line of an email.

    Returns:
    - str: The subject line with leading, trailing, and extra spaces removed.
    """
    subject = subject.strip()
    subject = ' '.join(subject.split())
    return subject

if __name__ == "__main__":
    # Read the DataFrame from the CSV file
    df = pd.read_csv(paths.DATA_NO_DUPLICATE)

    # Drop rows where 'To' field is unknown (NaN)
    df = df.dropna(subset=['To'])

    # Display the size of the dataset
    print(f"\nThe dataset's size: {df.shape}\n")

    # Count the number of NaNs for each column
    nan_counts = df.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")

    # Clean the subject lines by removing prefixes and spaces
    df['subject-clean'] = df['Subject'].fillna('')
    df['subject-clean'] = df['subject-clean'].apply(remove_prefixes).apply(remove_spaces)

    # Split the dataset into two based on whether subject lines are empty or not
    df_empty_subject = df[df['subject-clean'] == '']
    df_non_empty_subject = df[df['subject-clean'] != '']
    
    # Display the size of datasets with empty and non-empty subject lines
    print(f"\nThe dataset's size with empty subject: {df_empty_subject.shape}\n")
    print(f"\nThe dataset's size with subject: {df_non_empty_subject.shape}\n")

    # Save the cleaned datasets to CSV files
    df_empty_subject.to_csv(paths.DATA_CLEAN_EMPTY_SUBJECT, index=False)
    df_non_empty_subject.to_csv(paths.DATA_CLEAN_SUBJECT, index=False)
    
    print("\nCSV files are created!")
