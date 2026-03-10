import os
import re
import json

def xor_transcode(data, key):
    return bytearray([b ^ key for b in data])

def process_file(file_path):
    with open(file_path, 'rb') as file:
        enc_data = file.read()

    transcoded_data = xor_transcode(enc_data, 0x55)
    transcoded_text = transcoded_data.decode('utf-8', errors='ignore')

    result = {}
    current_person = None
    reference = None

    lines = transcoded_text.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('/'):
            current_person = line[1:].strip()
            result[current_person] = {"reference": None, "quotes": []}
            reference = None
        elif line.startswith('"'):
            if current_person:
                if reference is None:
                    match = re.match(r'^"(\d{2})(.*)', line)
                    if match:
                        reference = match.group(1)
                        quote = match.group(2).strip().strip('"')
                    else:
                        quote = line.strip('"')  # Remove initial quote here
                else:
                    quote = line.strip('"')  # Remove initial quote here

                # Remove trailing commas and backslashes
                quote = quote.rstrip(',').rstrip('\\').strip()
                
                #Remove any remaining double quotes within the quote itself
                quote = quote.replace('"', '') # Clean up any internal quotes

                result[current_person]["quotes"].append(quote)
                if result[current_person]["reference"] is None:
                    result[current_person]["reference"] = reference
    return result

def parse_talking(original_gamedata, output_folder):
    os.makedirs("{}/text/".format(output_folder), exist_ok=True)
    directory_path = original_gamedata
    all_results = {}

    for file_name in os.listdir(directory_path):
        if file_name.startswith('FARE') and file_name.endswith('.ENC'):
            file_path = os.path.join(directory_path, file_name)
            print(f"Processing file: {file_path}")
            file_result = process_file(file_path)
            all_results[file_name] = file_result

    print(json.dumps(all_results, indent=4))
    
    # Write to a JSON file
    output_file_path = "{}/text/fare_data.json".format(output_folder)  # You can change the filename
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_results, json_file, indent=4, ensure_ascii=False)  # ensure_ascii=False for proper UTF-8 handling

    print(f"Data written to {output_file_path}")

if __name__ == "__main__":
    parse_talking()