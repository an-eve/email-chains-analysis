import json
import paths
from collections import Counter

def sort_dict_by_subject(test_dict):
    '''
    Sort the dictionary by subject line alphabetically.

    Args:
    - test_dict (dict): The input dictionary to be sorted.

    Returns:
    - dict: The sorted dictionary.
    '''
    sorted_list = sorted(test_dict.items(), key=lambda x: x[0])
    return dict(sorted_list)

def print_text_from_files(dictionary, key, combined_path):
    '''
    Print and save the combined text from files associated with a given subject line.

    Args:
    - dictionary (dict): The dictionary containing email groups indexed by subject line.
    - key (str): The subject line for which the files need to be combined and printed.
    - combined_path (str): The path to save the combined text file.
    '''
    if key in dictionary:
        ids = dictionary[key]['ids']
        with open(combined_path, 'w') as combined_file:
            for ind, file_path in enumerate(ids):
                with open('../' + file_path, 'r') as file:
                    combined_file.write('\n'*4 + '#' * 60 + '\n')
                    combined_file.write('#' * 5 + ' ' * 20 + f'Message {ind+1}' + ' ' * 20 + '#' * 5 + '\n')
                    combined_file.write('#' * 60 + '\n'*4)
                    combined_file.write(file.read())
        print("Text from files combined and saved to 'combined_text.txt'")
    else:
        print("Key not found in the dictionary.")

def process_subject_groups():
    # Load subject groups from file
    with open(paths.SUBJECT_GROUPS, 'r') as file:
        groups = json.load(file)

    # Sort groups by subject line alphabetically
    alphabetical_groups = sort_dict_by_subject(groups)

    # Save alphabetical groups to file
    with open(paths.ALPHABETICAL_SUBJECT_GROUPS, 'w') as file:
        json.dump(alphabetical_groups, file)

    # Get length values from alphabetical groups
    length_values = [entry['length'] for entry in alphabetical_groups.values()]

    # Count the occurrences of each length value
    length_counts = Counter(length_values)

    # Create a dictionary to hold the counts of lengths less than or equal to 20
    length_counts = sorted(length_counts.items())[:20]

    # Get count for lengths greater than 20
    greater_than_20_count = sum(1 for length in length_values if isinstance(length, int) and length > 20)

    # Total number
    print(f"\nTotal number of the subject groups: {len(groups)}\n\n")
    
    # Print the table
    print("Length    | Number of Instances")
    print("-----------------------------")
    for length, count in length_counts:
        print(f"{length:<9} | {count:<18}")
    
    # Print count for lengths greater than 20
    if greater_than_20_count > 0:
        print(">20" + " "*7 + f"| {greater_than_20_count:<18}")
        

    # Filter groups for further analysis
    filtered_groups = {key: value for key, value in alphabetical_groups.items() if value['length'] == 1}
    print(f"\nNumber of groups with the size 1: {len(filtered_groups)}")

    with open(paths.SUBJECT_GROUPS_1, 'w') as file:
        json.dump(filtered_groups, file)
     
    filtered_groups = {key: value for key, value in alphabetical_groups.items() if value['length'] > 1}
    print(f"Number of groups bigger than 1: {len(filtered_groups)}")

    with open(paths.SUBJECT_GROUPS_2_PLUS, 'w') as file:
        json.dump(filtered_groups, file)

    filtered_groups = {key: value for key, value in alphabetical_groups.items() if value['length'] == 2}
    print(f"Number of groups with the size 2: {len(filtered_groups)}")

    with open(paths.SUBJECT_GROUPS_2, 'w') as file:
        json.dump(filtered_groups, file)

    filtered_groups = {key: value for key, value in alphabetical_groups.items() if value['length'] == 3}
    print(f"Number of groups with the size 3: {len(filtered_groups)}")

    with open(paths.SUBJECT_GROUPS_3, 'w') as file:
        json.dump(filtered_groups, file)

    filtered_groups = {key: value for key, value in alphabetical_groups.items() if value['length'] == 6}
    print(f"Number of groups with the size 6: {len(filtered_groups)}")

    with open(paths.SUBJECT_GROUPS_6, 'w') as file:
        json.dump(filtered_groups, file)

    filtered_groups = {key: value for key, value in alphabetical_groups.items() if value['length'] > 2}
    print(f"Number of groups bigger than 2: {len(filtered_groups)}")

    with open(paths.SUBJECT_GROUPS_3_PLUS, 'w') as file:
        json.dump(filtered_groups, file)

    # Get the longest chain
    longest_chain = max(filtered_groups, key=lambda x: filtered_groups[x]['length'])
    longest_chain_length = filtered_groups[longest_chain]['length']

    # Print the instance of the Biggest Group
    print("\nTitle of the Biggest Group:", longest_chain)
    print("Length of the Biggest Group:", longest_chain_length)

if __name__ == "__main__":
    process_subject_groups()


"""
combined_path = '../' + 'data/check-groups/combined_text.txt'
print_text_from_files(groups, 'Alternate Decision on CPA Implementation (DWR rates and Direct Access)', combined_path)
"""



