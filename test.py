#!/usr/bin/env python3
import openai
import html
import json
import csv
import re
import time
from google.cloud import translate_v2 as Translate

# OpenAI API key
openai.api_key = open("openai-key.txt", "r").read().strip("\n")

# Google Cloud API key
api_key_path = "translate-key.json"
translate_client = Translate.Client.from_service_account_json(api_key_path)

# Translates text into the target language, must be valid ISO 639-1 language code
def translate(target: str, text: str) -> dict:
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    result = translate_client.translate(text, target_language=target)
    # Testing
    # print("Text: {}".format(result["input"]))
    # print("Translation: {}".format(result["translatedText"]))
    # print("Detected source language: {}".format(result["detectedSourceLanguage"]))
    return result["translatedText"]

# Using the three supported variants with Google Cloud Translate
def translate_to_chinese_variants(text):
    chinese_variants = {
        'zh': translate('zh', text),            #Chinese simplfied
        'zh-CN': translate('zh-CN', text),      #Chinese simplified, People's Republic of China
        'zh-TW': translate('zh-TW', text)       #Taiwanese Mandarin
    }
    return chinese_variants

def translate_responses_to_english(translations_with_responses):
    translated_responses = {}

    for english_prompt, response_variants in translations_with_responses.items():
        translated_variants = {}

        for variant, response in response_variants.items():
            # Decode HTML
            decoded_response = html.unescape(response)

            # Replace HTML entity &#39; with apostrophe '
            decoded_response = re.sub(r'&#39;', "'", decoded_response)
            translated_response = translate('en', decoded_response)
            translated_variants[f'{variant}_translated'] = translated_response

        translated_responses[english_prompt] = translated_variants

    return translated_responses

# def list_languages() -> dict:
#     """Lists all available languages."""
#     results = translate_client.get_languages()
#     for language in results:
#         print("{name} ({language})".format(**language))
#     return results
# list_languages()

def process_csv(input_file):
    translations_dict = {}

    with open(input_file, 'r', encoding='utf-8') as csv_input:
        reader = csv.DictReader(csv_input)

        for row in reader:
            # time.sleep(1)
            # csv column starts with 'text'
            english_prompt = row.get('text', '')

            if english_prompt:
                translations_dict[english_prompt] = translate_to_chinese_variants(english_prompt)

    return translations_dict

def make_chatgpt_call(translation: str):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{translation}"}]
    )
    return response.choices[0].message.content

def interact_with_chatgpt(translations: dict):
    responses_dict = {}

    for english_prompt, chinese_variants in translations.items():
        response_variants = {}

        for variant, translation in chinese_variants.items():
            print(f"Making ChatGPT call for {variant}:\t{translation}")
            # Call chatgpt
            completion = make_chatgpt_call(translation)
            response_variants[f'response_{variant}'] = completion

        responses_dict[english_prompt] = response_variants

    return responses_dict

def print_translations(translations: dict):
    print("\nTRANSLATIONS")
    for english_prompt, chinese_variants in translations.items():
        print(f"English: {english_prompt}")
        for variant, translation in chinese_variants.items():
            print(f"{variant}:\t{translation}")
        print("-" * 50)

def print_responses(translations_with_responses: dict):
    print("\nRESPONSES:")
    for english_prompt, response_variants in translations_with_responses.items():
        print(f"English: {english_prompt}")
        for variant, response in response_variants.items():
            print(f"{variant}: {response}\n")
        print("-" * 50)

def print_translated_responses(translated_responses: dict):
    print("\nTRANSLATED RESPONSES")
    for english_prompt, translated_variants in translated_responses.items():
        print(f"English: {english_prompt}")
        for variant, translation in translated_variants.items():
            # Convert to string
            translation_str = str(translation)
            # Replace HTML &#39; with apostrophe '
            decoded_translation = re.sub(r'&#39;', "'", translation_str)
            print(f"{variant}:\t{decoded_translation}\n")
        print("-" * 50)

# can use this if you want to make a csv instead of json
def write_csv(translated_responses: dict):
    with open('translated_responses.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Question in English', 'zh_response in English', 'zh_CN response in English', 'zh_TW response in English'])

        for english_prompt, translated_variants in translated_responses.items():
            row = [english_prompt]
            for variant, translation in translated_variants.items():
                row.append(translation)
            csv_writer.writerow(row)

def write_json(translated_responses: dict):
    with open('translated_responses.json', 'w', encoding='utf-8') as json_file:
        json.dump(translated_responses, json_file, ensure_ascii=False, indent=4)

def main():
    translations = process_csv('input.csv')
    print_translations(translations)

    translations_with_responses = interact_with_chatgpt(translations)
    print_responses(translations_with_responses)

    translated_responses = translate_responses_to_english(translations_with_responses)
    print_translated_responses(translated_responses)

    write_json(translated_responses)

    # write_csv(translated_responses)


if __name__ == "__main__":
    main()
