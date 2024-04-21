import pandas as pd
import numpy as np
import re
import paths
        
def add_clean_text(text):
    '''Cleans the text content for later processing, removing unnecessary characters and spaces.
    
    Args:
    - text (str): Text content to be cleaned.
    
    Returns:
    - str: Cleaned text content.
    '''
    # Remove the symbols
    text = re.sub(r'=20', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=09', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=018', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=01', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'3D', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\?', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=\n', '', text, flags=re.IGNORECASE)
    
    # Emails
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  
    text = re.sub(email_pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(r'mailto:', '', text, flags=re.IGNORECASE)
    
    
    # Remove the phrase "Please respond to" from each line
    text = re.sub(r'Please respond to', '', text, flags=re.IGNORECASE)
    # URLs
    text = re.sub(r"(https?://[^<>|\s]+)", " ", text, flags = re.IGNORECASE)
    # Remove lines similar to "- filename.extension"
    text = re.sub(r'- .*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif)', '', text, flags=re.IGNORECASE)  
    # Remove document names enclosed within double angle brackets
    text = re.sub(r'<<.*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif)>>', '', text, flags=re.IGNORECASE)   
    # Remove lines similar to "filename.extension"
    text = re.sub(r'.*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif)', '', text, flags=re.IGNORECASE)
    
    # Remove <Embedded StdOleLink>, <Embedded Picture (Metafile)>, ect.
    text = re.sub(r'<Embedded StdOleLink>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[IMAGE\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Microsoft Excel Worksheet>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Device Independent Bitmap\)>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Metafile\)>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded >', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Device Independent Bitmap\)>', ' ', text, flags=re.IGNORECASE)
    
    # Remove the symbols
    text = re.sub(r'_!', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'!_', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'_', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'~', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'-', ' ', text, flags=re.IGNORECASE)

    text = re.sub(r'[\[\]]', '', text)
    text = re.sub(r'[\(\)]', '', text)
    text = re.sub(r'\'', ' ', text, flags=re.IGNORECASE)  
    text = re.sub(r',', '', text, flags=re.IGNORECASE)
    text = re.sub(r'>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\;', '', text, flags=re.IGNORECASE)   
    text = re.sub(r'\+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'"', '', text, flags=re.IGNORECASE)
    text = re.sub(r'&', '', text, flags=re.IGNORECASE)
    text = re.sub(r'=', '', text, flags=re.IGNORECASE)
    text = re.sub(r'=', '', text, flags=re.IGNORECASE)

    # Clean up other unnecessary characters and spaces
    text = re.sub(r'[\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    
    return text.lower()


df = pd.read_csv(paths.DATA_CLEAN_SUBJECT)
    
# Additional cleaning of the email body
df['content-extra-clean'] = df['content'].apply(add_clean_text)
    
# Save this more informative version of the dataframe
df.to_csv(paths.DATA_CLEAN_SUBJECT_INF, index=False)