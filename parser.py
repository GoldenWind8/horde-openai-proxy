from litellmParser import *
from transformers import AutoTokenizer

models = ["mistralai/Mistral-7B-Instruct-v0.1", "cognitivecomputations/dolphin-2.6-mistral-7b", "HuggingFaceH4/zephyr-7b-beta"]
# Path to the local configuration file
model = models[0]
# Load the tokenizer from the local configuration file
tokenizer = AutoTokenizer.from_pretrained(model)
#
# # Define the chat array
chat = [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing great. How can I help you today?"},
    {"role": "user", "content": "I'd like to show off how chat templating works!"},
]
#
# # Apply the chat template
# chat_template = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
#
# print(chat_template)
# print("===============")
#
# chat_t = hf_chat_template(model, chat)
# # Print the chat template
# print(chat_t)

def parse_messages(messages):
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return prompt


s= parse_messages(chat)
print(s)
