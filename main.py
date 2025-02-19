from lxml import etree
import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_KEY"))

def translate_text(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a translator that accurately translates text from English to Arabic."},
                {"role": "user", "content": f"Translate this to Arabic: {text}"}
            ]
        )
        translated_text = response.choices[0].message.content.strip()
        return translated_text if translated_text else text
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return text

def translate_xaml(input_file, output_file):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_file, parser)
    root = tree.getroot()

    # Print root namespaces for debugging
    print("Namespaces found:", root.nsmap)

    # Extract system namespace dynamically
    system_ns = root.nsmap.get("system", "clr-namespace:System;assembly=mscorlib")
    nsmap = {"system": system_ns}

    # Print all child elements to verify structure
    print("\nRoot child elements:")
    for elem in root:
        print(f"Tag: {elem.tag}, Text: {elem.text}")

    cnt = 1

    # Use the correct namespace prefix
    for string_element in root.xpath("//system:String", namespaces=nsmap):
        print(f"{cnt}. Found element: {string_element.tag} - {string_element.text}")
        cnt += 1
        if string_element.text:
            translated_text = translate_text(string_element.text)
            print(f"Translating: {string_element.text} -> {translated_text}")
            string_element.text = translated_text

    with open(output_file, "wb") as f:
        f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))

    print("Translation completed successfully!")

translate_xaml("/Users/satviksrivastava/Documents/Projects/translate/en-US.xaml", "translated.xaml")
