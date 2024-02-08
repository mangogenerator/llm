# llm
Program that automatically queries English prompts to ChatGPT in Chinese, and translates back to English.

You need to have an API Key from OpenAI and Google Cloud to run this program.
# OpenAI API key
openai.api_key = open("openai-key.txt", "r").read().strip("\n")

# Google Cloud API key
api_key_path = "translate-key.json"
translate_client = Translate.Client.from_service_account_json(api_key_path)

The program takes input as "input.csv" and translates the text to Chinese via the Google Translate API. It can then make either a .json or .csv output file with the responses.
It does so using three Chinese variants: Chinese Traditional, Chinese Simplified, and Taiwanese Mandarin.

# Packages needed
openai,
translate_v2
