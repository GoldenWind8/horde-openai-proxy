from transformers import AutoTokenizer

# Path to the local configuration file
config_file = "c.json"

# Load the tokenizer from the local configuration file
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

# Define the chat array
chat = [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing great. How can I help you today?"},
    {"role": "user", "content": "I'd like to show off how chat templating works!"},
]

# Apply the chat template
chat_template = tokenizer.apply_chat_template(chat, tokenize=False)

# Print the chat template
print(chat_template)