import pandas as pd
import email
import time
import re
from datetime import datetime
import pytz
import paths


def get_text_from_email(msg):
    '''Extracts text content from email objects.
    
    Args:
    - msg: Email message object.
    
    Returns:
    - str: Concatenated text content extracted from the email message.
    '''
    parts = []
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            parts.append(part.get_payload())
    return ''.join(parts)


def clean_text(text):
    '''Cleans the text content for later processing, removing unnecessary characters and spaces.
    
    Args:
    - text (str): Text content to be cleaned.
    
    Returns:
    - str: Cleaned text content.
    '''
    # Remove the phrase "Please respond to" from each line
    text = re.sub(r'Please respond to', '', text, flags=re.IGNORECASE)
     
    # Remove lines similar to "- filename.extension"
    text = re.sub(r'- .*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf)', '', text, flags=re.IGNORECASE)
    
    # Remove document names enclosed within double angle brackets
    text = re.sub(r'<<.*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf)>>', '', text, flags=re.IGNORECASE)
    
    
    # Remove <Embedded StdOleLink>, <Embedded Picture (Metafile)>, and ">"
    text = re.sub(r'<Embedded StdOleLink>|<Embedded Picture \(Metafile\)>|<Embedded Microsoft Excel Worksheet>|>', '', text, flags=re.IGNORECASE)
    
    # Clean up other unnecessary characters and spaces
    text = re.sub(r'[\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    
    return text

# The first version of the cleaning content function
"""
def clean_text(text):
    '''Cleans the text content for later processing, removing unnecessary characters and spaces.
    
    Args:
    - text (str): Text content to be cleaned.
    
    Returns:
    - str: Cleaned text content.
    '''
    text = re.sub(r'[\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    return text
"""

def convert_date_to_timestamp(date_string):
    '''Converts date string to a Unix timestamp, considering the given timezone.
    
    Args:
    - date_string (str): Date string in the format 'Day, DD Mon YYYY HH:MM:SS ±zzzz' (e.g., 'Tue, 29 Mar 2022 10:15:00 -0700').
    
    Returns:
    - float: Unix timestamp corresponding to the given date string.
    '''
    pst_tz = pytz.timezone('America/Los_Angeles')
    date_format = '%a, %d %b %Y %H:%M:%S %z'
    date_string = date_string.replace(' (PDT)', '').replace(' (PST)', '')   
    parsed_date = datetime.strptime(date_string, date_format)    
    pst_date = parsed_date.astimezone(pst_tz)   
    timestamp = pst_date.timestamp()    
    return timestamp

def process_date_string(date_string):
    '''Process date string to convert it into a timestamp.
    
    Args:
    - date_string (str): Date string in the format 'Day, DD Mon YYYY HH:MM:SS ±zzzz' (e.g., 'Tue, 29 Mar 2022 10:15:00 -0700').
    
    Returns:
    - float: Unix timestamp corresponding to the given date string.
    '''
    timestamp = convert_date_to_timestamp(date_string)
    return timestamp


if __name__ == "__main__":
    # Read data from CSV file
    emails_df = pd.read_csv(paths.CSV_DATA)

    # Print basic information about the dataset
    print(f"The whole dataset's size: {emails_df.shape}\n")
    print(f"First few rows of the dataset:\n{emails_df.head()}")

    # Rename columns for better clarity
    new_column_names = {'File Path': 'file', 'File Text': 'message'}
    emails_df = emails_df.rename(columns=new_column_names)

    # Display an example message
    print(f"\nExample message:\n\n{emails_df.message[10]}\n")

    ######################################################################

    # Extract messages from strings
    start_time = time.time()
    messages = list(map(email.message_from_string, emails_df['message']))

    # Drop the original message column
    emails_df.drop('message', axis=1, inplace=True)

    # Get fields from parsed email objects
    keys = ['Message-ID', 'Date', 'From', 'To', 'Subject', 'Cc',
            'Mime-Version', 'Content-Type', 'Content-Transfer-Encoding',
            'Bcc', 'X-From', 'X-To', 'X-cc', 'X-bcc', 'X-Folder',
            'X-Origin', 'X-FileName']

    for key in keys:
        emails_df[key] = [doc[key] for doc in messages]

    # Convert date to timestamp
    emails_df['date-timestamp'] = emails_df['Date'].apply(convert_date_to_timestamp)

    # Parse content from emails
    emails_df['content'] = list(map(get_text_from_email, messages))
    emails_df['content-clean'] = emails_df['content'].apply(clean_text) 

    # Extract the root of 'file' as 'user''Date'
    emails_df['user'] = emails_df['file'].map(lambda x: x.split('/')[2])

    # Release memory by deleting the 'messages' list
    del messages

    print(f"\nFirst rows after parsing:\n{emails_df.head()}\n")
    print(f"The dataset's size after parsing: {emails_df.shape}\n")
    
    # Count the number of NaNs for each column
    nan_counts = emails_df.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")

    # Save the parsed DataFrame to a CSV file
    emails_df.to_csv(paths.PARSED_DATA, index=False)
    
    # Print time taken for parsing
    end_time = time.time()
    print("\nTime taken for parsing:", end_time - start_time, "seconds")

    
    







    

