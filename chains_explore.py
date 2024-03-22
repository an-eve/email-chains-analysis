import json

file_path = 'data/chains.json'
with open(file_path, 'r') as file:
    chains = json.load(file)
    
    
def sort_dict_by_subject(test_dict):
    sorted_list = sorted(test_dict.items(), key=lambda x: x[0])
    return dict(sorted_list)
 
def sort_dict_by_value_lambda_reverse(test_dict):
    sorted_list = sorted(test_dict.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_list)

alphabetical_chains = sort_dict_by_subject(chains)

alphabetical_path = 'data/alphabetical-chains.json'
with open(alphabetical_path, 'w') as file:
    json.dump(alphabetical_chains, file)


# Chains longer than 1
filtered_chains = {key: value for key, value in alphabetical_chains.items() if value['length'] > 1}
print(f"Number of chains longer than 1: {len(filtered_chains)}")

chains2_path = 'data/chains-2.json'
with open(chains2_path, 'w') as file:
    json.dump(filtered_chains, file)
    
    
def print_text_from_files(dictionary, key, combined_path):
    if key in dictionary:
        ids = dictionary[key]['ids']
        with open(combined_path, 'w') as combined_file:
            for ind, file_path in enumerate(ids):
                with open(file_path, 'r') as file:
                    combined_file.write('#' * 60 + '\n')
                    combined_file.write('#' * 5 + ' ' * 20 + f'Message {ind+1}' + ' ' * 20 + '#' * 5 + '\n')
                    combined_file.write('#' * 60 + '\n'*4)
                    combined_file.write(file.read())
        print("Text from files combined and saved to 'combined_text.txt'")
    else:
        print("Key not found in the dictionary.")

path = 'data/combined_text_2.txt'


print_text_from_files(filtered_chains, '"Chinese Wall" Classroom Training | Participants: 51', path)

        
# Chains longer than 2
filtered_chains = {key: value for key, value in chains.items() if value['length'] > 2}
print(f"Number of chains longer than 2: {len(filtered_chains)}")

chains3_path = 'data/chains-3.json'
with open(chains3_path, 'w') as file:
    json.dump(filtered_chains, file)

# Longest chain
longest_chain = None
longest_chain_length = 0
longest_chain_title = None

for instance in filtered_chains:
    chain_length = filtered_chains[instance]['length']
    if chain_length > longest_chain_length:
        longest_chain_length = chain_length
        longest_chain_title = instance
        longest_chain = filtered_chains[instance]['ids']

# Print the instance with the longest chain
print("Title:", longest_chain_title)
print("Emails:", longest_chain)
print("Length of the Longest Chain:", longest_chain_length)
