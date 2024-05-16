import pandas as pd
import numpy as np
import json
import time
import re
import paths

def count_words(text):
    words = re.findall(r'\w+', text)
    return len(words)

if __name__ == "__main__":
    
    # Read the DataFrame from the CSV file
    df = pd.read_csv(paths.DATA_CLEAN_SUBJECT)
    print(f'Size with emty emails: {len(df)}')
    df['word_count'] = df['content'].apply(count_words)
    
    df = df[df['word_count'] != 0]
    df = df.drop(columns=['word_count'])
    print(f'Size without emty emails: {len(df)}')
    df.to_csv(paths.DATA_CLEAN_SUBJECT, index=False)
