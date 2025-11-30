import json
import random
import os

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
INPUT_FILE = "data/raw_data.json"
TRAIN_FILE = "data/train.jsonl"
VALID_FILE = "data/valid.jsonl"
SPLIT_RATIO = 0.9  # 90% for training, 10% for validation

# def create_chat_message(typo, correct_name):
#     """
#     Creates the ChatML style message structure.
    
#     CHANGE: The assistant now outputs PLAIN TEXT (comma separated if multiple),
#     stripping away all JSON syntax.
#     """
#     return {
#         "messages": [
#             {
#                 "role": "user", 
#                 # explicit instruction helps the model converge faster
#                 "content": f"Fix the spelling of this search query. Output only the corrected words separated by commas: '{typo}'"
#             },
#             {
#                 "role": "assistant", 
#                 # The crucial part: This is just the raw string now.
#                 "content": correct_name
#             }
#         ]
#     }

def create_chat_message(typo, correct_name):
    # 1. Format the Correct Answer as JSON (matches your prompt instructions)
    # We use ensure_ascii=False to handle Indian language characters if needed
    target_json = json.dumps({"corrected": correct_name}, ensure_ascii=False)
    
    # 2. Hardcode the Gemma format. 
    # This ensures the <end_of_turn> is strictly part of the training data.
    # Note: We use the \n separator as Gemma expects.
    
    full_prompt_text = (
        f"<start_of_turn>user\n"
        f"You are a specialized Multilingual Query Corrector. "
        f"Map the query to the correct Standard Product Name in JSON format.\n\n"
        f"User Query: {typo}<end_of_turn>\n"
        f"<start_of_turn>model\n"
        f"{target_json}<end_of_turn>"
    )

    # Return "text" instead of "messages". 
    # MLX's lora.py prefers raw "text" when we want total format control.
    return {
        "text": full_prompt_text
    }

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please create it and paste your JSON data.")
        return

    print(f"Reading {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            return

    # Normalize data list
    data_batches = raw_data if isinstance(raw_data, list) else [raw_data]
    
    all_pairs = []

    for batch in data_batches:
        items = batch.get("items", [])
        for item in items:
            correct_name = item.get("original")
            variations = item.get("variations", [])
            
            for typo in variations:
                if typo and correct_name:
                    all_pairs.append(create_chat_message(typo, correct_name))

    print(f"Extracted {len(all_pairs)} query pairs.")

    # Shuffle and Split
    random.shuffle(all_pairs)
    split_index = int(len(all_pairs) * SPLIT_RATIO)
    train_data = all_pairs[:split_index]
    valid_data = all_pairs[split_index:]

    # Save to JSONL
    def save_jsonl(data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in data:
                f.write(json.dumps(entry) + '\n')
        print(f"Saved {len(data)} rows to {filename}")

    save_jsonl(train_data, TRAIN_FILE)
    save_jsonl(valid_data, VALID_FILE)

    # ---------------------------------------------------------
    # VERIFICATION PRINT
    # ---------------------------------------------------------
    print("\n--- Preview of Training Data (New Format) ---")
    print("User sends: " + train_data[0]['text'])
    print("Model replies: " + train_data[0]['text'])
    print("---------------------------------------------")

if __name__ == "__main__":
    main()