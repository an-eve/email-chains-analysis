import pandas as pd
import os, sys
import email
import time

def get_text_from_email(msg):
    '''To get the content from email objects'''
    parts = []
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            parts.append(part.get_payload())
    return ''.join(parts)


if __name__ == "__main__":
    
    # Uploading data
    file_path = 'data/mails-data.csv'
    emails_df = pd.read_csv(file_path)
    print(f"The whole dataset's size: {emails_df.shape}\n")
    print(f"First rows:\n{emails_df.head()}")

    new_column_names = {'File Path': 'file', 'File Text': 'message'}
    emails_df = emails_df.rename(columns=new_column_names)

    print(f"\nExample message:\n{emails_df.message[10]}\n")

    ######################################################################

    # Extract messages from strings
    start_time = time.time()
    messages = list(map(email.message_from_string, emails_df['message']))

    # Delete the string message (version before parsing)
    emails_df.drop('message', axis=1, inplace=True)

    # Get fields from parsed email objects
    keys = ['Message-ID', 'Date', 'From', 'To', 'Subject', 'Cc', 
            'Mime-Version', 'Content-Type', 'Content-Transfer-Encoding',
            'Bcc', 'X-From', 'X-To', 'X-cc', 'X-bcc', 'X-Folder',
            'X-Origin','X-FileName']
    
    for key in keys:
        emails_df[key] = [doc[key] for doc in messages]

    # Parse content from emails
    emails_df['content'] = list(map(get_text_from_email, messages))

    # Extract the root of 'file' as 'user''Date'
    emails_df['user'] = emails_df['file'].map(lambda x:x.split('/')[2])
    del messages

    print(f"\nFirst rows after parsing:\n{emails_df.head()}\n")

    # Save the DataFrame to a CSV file
    parsed_path = "data/parsed-mails-data.csv"
    emails_df.to_csv(parsed_path, index=False)
    
    end_time = time.time()
    print("Time taken for parsing:", end_time - start_time, "seconds")
    
