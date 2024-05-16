import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import json
from collections import Counter
import paths

def modify_attachement(text):
    '''Replace the names of the attachement files.
    
    Args:
    - text (str): Text content to be modified.
    
    Returns:
    - str: Modified text content.
    '''

    # Remove lines similar to "- filename.extension"
    text = re.sub(r'- .*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif|dat)', 'Attachement file.', text, flags=re.IGNORECASE)  
    # Remove document names enclosed within double angle brackets
    text = re.sub(r'<<.*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif|dat)>>', 'Attachement file.', text, flags=re.IGNORECASE)   
    # Remove lines similar to "filename.extension"
    text = re.sub(r'.*?\.(doc|png|xlsx|jpeg|jpg|ppt|xls|wpd|pdf|vcf|tif|dat)', 'Attachement file.', text, flags=re.IGNORECASE)
    
    # Remove <Embedded StdOleLink>, <Embedded Picture (Metafile)>, ect.
    text = re.sub(r'<Embedded StdOleLink>', 'Attachement file.', text, flags=re.IGNORECASE)
    text = re.sub(r'\[IMAGE\]', 'Attachement file.', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Microsoft Excel Worksheet>', 'Attachement file.', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Device Independent Bitmap\)>', 'Attachement file.', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Metafile\)>', 'Attachement file.', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded >', 'Attachement file.', text, flags=re.IGNORECASE)
    text = re.sub(r'<Embedded Picture \(Device Independent Bitmap\)>', 'Attachement file.', text, flags=re.IGNORECASE)
    
    return text

def count_words(text):
    words = re.findall(r'\w+', text)
    return len(words)

def remove_from_pattern(message, pattern):
    match = re.search(pattern, message, flags=re.IGNORECASE)
    if match:
        message = message[:match.start()]
    return message

def extract_between_original_messages(text):
    # Define the marker
    marker = "Original Message"
    forwarded_phrase = "Forwarded by"
    
    # Find the positions of the first two "Original Message" instances
    first_pos = text.find(marker)
    second_pos = text.find(marker, first_pos + len(marker))
    # Check if there are at least two "Original Message" instances
    if (first_pos != -1) and (second_pos != -1) and not(forwarded_phrase in text):
        # Extract the text between the two "Original Message" instances
        start_index = first_pos + len(marker)
        end_index = second_pos
        extracted_text = text[start_index:end_index].strip()
    elif (first_pos != -1) and not(forwarded_phrase in text):
        start_index = first_pos + len(marker)
        extracted_text = text[start_index:].strip()
    else:
        return ""
    
    return extracted_text

def remove_forwarded_sections(text):
    # Define the markers
    forward_marker = "Forwarded by"
    subject_marker = "Subject:"
    
    first_pos = text.find(forward_marker)
    second_pos = text.find(subject_marker, first_pos + len(forward_marker))
    
    while (first_pos != -1) and (second_pos != -1):
        start_index = second_pos + len(subject_marker)
        text = text[start_index:]
        first_pos = text.find(forward_marker)
        if first_pos != -1:
            second_pos = text.find(subject_marker, first_pos + len(forward_marker))
            if first_pos > 35:
                end_index = first_pos
                text = text[:end_index]
                return text
    return text

def clean_email_body(body):
    orig_body = body[:]
    patterns = [
    r'Original Message',
    r'Forwarded by',
    r'Sent by:',
    ]

    for pattern in patterns:
        body = remove_from_pattern(body, pattern)

    if count_words(body) == 0:
        body = orig_body[:]
        body = extract_between_original_messages(body)
        
    if count_words(body) == 0:
        body = orig_body[:]
        body = remove_forwarded_sections(body)
        marker = "Original Message"
        pos = body.find(marker)
        if (pos != -1):
            body = body[:pos]

    return body.strip()


def when_to_insert_original_message(text):
    # Define the markers
    forward_marker = "Forwarded by"
    original_message_marker = "Original Message"
    to_marker = "To:"
    
    # Check if "Forwarded by" or "Original Message" exist in the text
    if forward_marker not in text and original_message_marker not in text:
        # Find the position to insert "Original Message" before the first "To:"
        to_pos = text.find(to_marker)
        if to_pos != -1:
            text = text[:to_pos] + original_message_marker + ' ' + text[to_pos:]
    return text
        
def clean_text_initial(text):
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
    
    #text = re.sub(r'\?', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'=\n', '', text, flags=re.IGNORECASE)
    '''
    # Emails
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  
    text = re.sub(email_pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(r'mailto:', '', text, flags=re.IGNORECASE)
    '''
    
    # Remove the phrase "Please respond to" from each line
    #text = re.sub(r'Please respond to', '', text, flags=re.IGNORECASE)
    # URLs
    #text = re.sub(r"(https?://[^<>|\s]+)", " ", text, flags = re.IGNORECASE)
    
    # Remove the symbols
    text = re.sub(r'_!', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'!_', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'_', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'~', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'--', ' ', text, flags=re.IGNORECASE)

    text = re.sub(r'[\[\]]', '', text)
    #text = re.sub(r'[\(\)]', '', text)
    #text = re.sub(r'\'', ' ', text, flags=re.IGNORECASE)  
    text = re.sub(r'>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<', '', text, flags=re.IGNORECASE)
    #text = re.sub(r'\;', '', text, flags=re.IGNORECASE)   
    text = re.sub(r'\+', '', text, flags=re.IGNORECASE)
    #text = re.sub(r'"', '', text, flags=re.IGNORECASE)
    text = re.sub(r'&', '', text, flags=re.IGNORECASE)
    #text = re.sub(r'=', '', text, flags=re.IGNORECASE)

    # Clean up other unnecessary characters and spaces
    text = re.sub(r'[\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    text = when_to_insert_original_message(text)
    pattern = r"\b\w+\s\w+(?:@\w+)? \d{2}/\d{2}/\d{4} \d{2}:\d{2} [ap]m\b"
    text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    text = text.strip()
    
    return text

def clean_text_further(text):
    '''Cleans the text content for later processing, removing unnecessary characters and spaces.
    
    Args:
    - text (str): Text content to be cleaned.
    
    Returns:
    - str: Cleaned text content.
    '''

    # Pattern to match
    pattern = r"\b\w+\s\w+(?:@\w+)? \d{2}/\d{2}/\d{4} \d{2}:\d{2} [ap]m\b"

    # Remove the pattern
    text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    if (len(text) > 0) and (text[0] == "-"):
        text = text[1:]
    if (len(text) > 0) and (text[-1] == "-"):
        text = text[:-1]
        
    text = text.strip()

    return text

def add_subject_to_content(row, name_col_content):
    return f"Subject: {row['subject-clean']}. {row[name_col_content]}"

def extract_heading_name(heading):
    # Define a regular expression pattern to match the heading structure
    pattern = re.compile(r'\[\d+\]\s*(.*)')

    # Use the pattern to search for matches in the heading
    match = pattern.match(heading)

    # If there is a match, return the extracted heading name
    if match:
        return match.group(1).strip()
    else:
        # If no match is found, return None or raise an error, depending on your preference
        return None
    
def print_chains(dictionary, df, key, combined_path):
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
                    combined_file.write('\n'*3 + '#' * 10 + ' ' * 15 + f'Cleaned {ind+1}' + ' ' * 16 + '#' * 10 + '\n'*3)
                    combined_file.write(df.loc[file_path, "content-new-2"])
        print(f"Text from files combined and saved to {combined_path}")
    else:
        print("Key not found in the dictionary.")


if __name__ == "__main__":

    all_chains = []
    all_chains_names = []

    # Iterate over the paths and load data from each file
    for path_key in paths.__dict__:
        if path_key.startswith('CHAINS_'):
            with open('../' + getattr(paths, path_key), 'r') as file:
                length_data = json.load(file)
                length_names = length_data.keys()
                all_chains.append(length_data)
                all_chains_names.extend(length_names)
    
    all_chains_names = list(map(extract_heading_name, all_chains_names))
    names_counts = Counter(all_chains_names)
    names_counts = dict(sorted(names_counts.items(), key=lambda item: item[1], reverse=True))
    
 
    df = pd.read_csv('../'+paths.DATA_CLEAN_SUBJECT)
    # File path is the index
    df.set_index('file', inplace=True)
    
    # Count the number of NaNs for each column
    nan_counts = df.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")

    nested_lists_of_files = [list(length_data.values()) for length_data in all_chains]
    indexes = []
    for sublist1 in nested_lists_of_files:
        for sublist2 in sublist1:
            indexes.extend(sublist2)

    df_chains = df.loc[indexes].copy()
    # Count the number of NaNs for each column
    nan_counts = df_chains.isna().sum()
    print(f"Number of NaNs for every column:\n{nan_counts}")

    
    df_chains['content-attachement'] = df_chains['content'].apply(modify_attachement)
    df_chains['content-new'] = df_chains['content-attachement'].apply(clean_text_initial)
    df_chains['content-new-1'] = df_chains['content-new'].apply(clean_email_body)
    df_chains['content-new-2'] = df_chains['content-new-1'].apply(clean_text_further)
    df_chains['content-new-2'] = df_chains.apply(add_subject_to_content, args=('content-new-2',), axis=1)
    
    import random
    chains = all_chains[0]
    checks = random.sample(list(chains.keys()), 50)
    # Write chains and groups in a file
    for i, key in enumerate(checks):
        print_chains(chains,df_chains, key, '../' + paths.CHECK_CHAINS + f'checking-chain-body-{i+1}.txt')
 


    empty_body = df_chains.loc[df_chains['content-clean'] == "", 'content-attachement']
    for i in range(len(empty_body)):
        print(i, ': ', empty_body.iloc[i])
    

    df_chains['word_count'] = df_chains['content'].apply(count_words)
    df_chains['word_count'] = df_chains['content-new-2'].apply(count_words)
    df_chains['word_count'].max()
    
    df_chains.loc[df_chains['word_count']<50]['word_count'].plot(kind='hist', bins=100, edgecolor='black')

    # Add labels and title
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Distribution of Values')

    # Show plot
    plt.show()
    
    len(df_chains.loc[df_chains['word_count']==0])
    
    with open('../'+paths.CHECK_CHAINS + f'null-body.txt', 'w') as combined_file:
        for i in df_chains.loc[df_chains['word_count']==0, 'content'].items():
            combined_file.write('\n'*3 + '#' * 10 + ' ' * 15 + 'Message' + ' ' * 16 + '#' * 10 + '\n'*3)
            combined_file.write(i[1])

        
    df_to_emb = df_chains.copy()
    df_to_emb.reset_index(inplace=True)
    columns_to_drop = ['Message-ID', 'Date', 'From', 'To', 'Subject', 'Cc', 'Mime-Version',
       'Content-Type', 'Content-Transfer-Encoding', 'Bcc', 'X-From', 'X-To', 'X-cc', 'X-bcc', 
       'X-Folder', 'X-Origin', 'X-FileName', 'content-clean', 'content',
       'content-attachement', 'content-new', 'content-new-1', 'word_count']
    df_to_emb.drop(columns=columns_to_drop, inplace=True)
    df_to_emb.to_csv('../data/mails-to_emb.csv', index=False)
    




                
    
    

# Example usage
email_text = """-----Original Message-----
From: Herod, Brenda F. 
Sent: Sunday, July 22, 2001 4:29 PM
To: Ha, Kenny; Stokley, Chris
Cc: Hart, Vivian; Thompson, Patti
Subject: FW: Metered Usage
 
As part of Project Ranger, it is my goal to have a single repository to house all actual data, allowing users to access data through an ad hoc reporting tool.  Additionally, as areas identify needs, I would hope that we can develop feeds rather than just ad hoc reporting.
 
We are setting up a meeting with CSC for this Wednesday to discuss the needs and start defining Iteration 2 of the project.  Vivian forwarded me this meeting that you have already set-up.  My question:  Without knowing the full scope of your efforts, I'd like to propose a single initiative to obtain actuals.  Additionally, we wanted to set-up this meeting for Wednesday when the CSC business analyst is in town.  Do you think it would be advantageous to combine the meetings, and schedule it for Wednesday?  
 
We will move forward with our efforts and will schedule a meeting for Wednesday.  If you all want to combine efforts, please let me know and we will include you on the meeting.
 
Chris - I had already included both you and Murray on the invitation listing.  Will you forward this E-mail to him?  I'm having problems trying to call up his E-mail address.
 
Please let me know.  
-----Original Message----- 
From: Hart, Vivian 
Sent: Fri 7/20/2001 5:12 PM 
To: Herod, Brenda F. 
Cc: 
Subject: Metered Usage
Kenny Ha who works for Anthony is already setting a meeting with the Portland guys on this.
Should you just attend this meeting or do you still want to have a separate meeting.  Kevin
Crippen is not going to be in until Wednesday though.
---------------------- Forwarded by Vivian Hart/HOU/EES on 07/20/2001 04:59 PM ---------------------------
Alarm enabled: an alarm will occur 10 minutes before the start time of this entry.
        Calendar Entry 
 
Brief description:
Date:
Time:
EB1114 / CSC Metering Data
07/24/2001
10:00 AM - 11:00 AM
 
Detailed description:
Kenny Ha, Todd Taylor, John Rutledge, Maurice Winter, Vivian Hart, Chris Stokley, Murray O'Neil
Invitations have been sent to:  Todd Taylor/HOU/EES, John Rutledge/HOU/EES, Maurice Winter/HOU/EES, Vivian Hart/HOU/EES, Chris Stokley/HOU/ECT, Murray P O'Neil/HOU/ECT
_________________________________________________________________________
Chairperson:    Kenny Ha/HOU/EES
Sent by:        Melinda Winkler/HOU/EES
This meeting repeats   starting on    (if the date occurs on a weekend the meeting ).
"""


email_text = clean_text_initial(email_text)
clean_email_body(email_text)




    
    
    df = pd.read_csv(paths.DATA_CLEAN_SUBJECT)
    
# Additional cleaning of the email body
df['content-extra-clean'] = df['content'].apply(add_clean_text)
    
# Save this more informative version of the dataframe
df.to_csv(paths.DATA_CLEAN_SUBJECT_INF, index=False)

 -----Original Message-----
 
 **********************************************************************
This e-mail is the property

Sent by: (+ 1 line before it)

To: (+ 3 line before it)

----- Forwarded by Sara Shackleton/HOU/ECT on 05/15/2001 06:50 PM -----

----- Forwarded by Tana Jones/HOU/ECT on 05/16/2001 03:22 PM -----

	Julia Murray@ENRON
	Sent by: Carolyn George@ENRON
	05/15/2001 03:59 PM
		 
		 To: Alan Aronowitz/HOU/ECT@ECT, Sandi M Braband/HOU/ECT@ECT, Teresa G 
Bushman/HOU/ECT@ECT, Michelle Cash/HOU/ECT@ECT, Barton Clark/HOU/ECT@ECT, 
Harry M Collins/HOU/ECT@ECT, Peter del Vecchio/HOU/ECT@ECT, Stacy E 
Dickson/HOU/ECT@ECT, Shawna Flynn/HOU/ECT@ECT, Barbara N Gray/HOU/ECT@ECT, 
Wayne Gresham/HOU/ECT@ECT, Mark E Haedicke/HOU/ECT@ECT, Leslie 
Hansen/HOU/ECT@ECT, Jeffrey T Hodge/HOU/ECT@ECT, Dan J Hyvl/HOU/ECT@ECT, Anne 
C Koehler/HOU/ECT@ECT, Dan Lyons/HOU/ECT@ECT, Kay Mann/Corp/Enron@Enron, 
Travis McCullough/HOU/ECT@ECT, Lisa Mellencamp/HOU/ECT@ECT, Janet H 
Moore/HOU/ECT@ECT, Julia Murray/HOU/ECT@ECT, Gerald Nemec/HOU/ECT@ECT, David 
Portz/HOU/ECT@ECT, Michael A Robison/HOU/ECT@ECT, Elizabeth 
Sager/HOU/ECT@ECT, Richard B Sanders/HOU/ECT@ECT, Lance 
Schuler-Legal/HOU/ECT@ECT, Sara Shackleton/HOU/ECT@ECT, Carol St 
Clair/HOU/ECT@ECT, Lou Stoler/HOU/ECT@ECT, Mark Taylor/HOU/ECT@ECT, Sheila 
Tweed/HOU/ECT@ECT, Steve Van Hooser/HOU/ECT@ECT, John 
Viverito/Corp/Enron@Enron, Ann Elizabeth White/HOU/ECT@ECT, Donna 
Lowry/Enron@EnronXGate, Susan Bailey/HOU/ECT@ECT, Kimberlee A 
Bennick/HOU/ECT@ECT, Genia FitzGerald/HOU/ECT@ECT, Nony Flores/HOU/ECT@ECT, 
Linda R Guinn/HOU/ECT@ECT, Ed B Hearn III/HOU/ECT@ECT, Mary J 
Heinitz/HOU/ECT@ECT, Tana Jones/HOU/ECT@ECT, Deb Korkmas/HOU/ECT@ECT, Laurie 
Mayer/HOU/ECT@ECT, Matt Maxwell/Corp/Enron@ENRON, Mary Ogden/HOU/ECT@ECT, 
Debra Perlingiere/HOU/ECT@ECT, Robert Walker/HOU/ECT@ECT, Kay 
Young/HOU/ECT@ECT, Merrill W Haas/HOU/ECT@ECT, Mark Greenberg/NA/Enron@ENRON, 
Robert Bruce/NA/Enron@Enron, Samantha Boyd/NA/Enron@Enron, Mary 
Cook/HOU/ECT@ECT, Angela Davis/NA/Enron@Enron, Stephanie 
Panus/NA/Enron@Enron, Marcus Nettelton/NA/Enron@ENRON, Brent 
Hendry/NA/Enron@Enron, Michelle Blaine/ENRON@enronXgate, Gail 
Brownfeld/ENRON@enronXgate, Dominic Carolan/Enron@EnronXGate, Eddy 
Daniels/NA/Enron@Enron, Andrew Edison/NA/Enron@Enron, Roseann 
Engeldorf/Enron@EnronXGate, Robert H George/NA/Enron@Enron, Cheryl 
Nelson/NA/Enron@Enron, Cheryl Lindeman/ENRON@enronXgate, Carlos 
Sole/NA/Enron@Enron, Randy Young/NA/Enron@Enron, Kathleen 
Carnahan/NA/Enron@Enron, Diane Goode/NA/Enron@Enron, Nancy 
Corbet/ENRON_DEVELOPMENT@ENRON_DEVELOPMENt, Ned E 
Crady/ENRON_DEVELOPMENT@ENRON_DEVELOPMENT, Francisco Pinto 
Leite/ENRON_DEVELOPMENT@ENRON_DEVELOPMENT, Coralina 
Rivera/ENRON_DEVELOPMENT@ENRON_DEVELOPMENT, Daniel R 
Rogers/ENRON_DEVELOPMENT@ENRON_DEVELOPMENT, Frank 
Sayre/ENRON_DEVELOPMENT@ENRON_DEVELOPMENT, Martha 
Braddy/ENRON_DEVELOPMENT@ENRON_DEVELOPMENt, Sarah 
Bruck/ENRON_DEVELOPMENT@ENRON_DEVELOPMENt, William S 
Bradford/Enron@EnronXGate, Debbie R Brackett/Enron@EnronXGate, Tom 
Moran/Enron@EnronXGate, Wendi LeBrocq/Enron@EnronXGate, Nidia 
Mendoza/ENRON@enronXgate, Veronica Espinoza/Enron@EnronXGate, Ken 
Curry/Enron@EnronXGate, Carol North/Enron@EnronXGate, Aparna 
Rajaram/Enron@EnronXGate
		 cc: 
		 Subject: Letter of Credit Seminar - May 23, 2001