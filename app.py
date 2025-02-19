import streamlit as st
import openai
import os
from dotenv import load_dotenv
from lxml import etree
import tempfile
import time

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_KEY"))

languages = [
    "Afrikaans", "Albanian", "Amharic", "Arabic", "Assamese", "Azerbaijani", 
    "Bangla", "Basque", "Bokmål", "Bosnian", "Bulgarian", "Catalan", "Chinese", 
    "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Farsi", "Filipino", 
    "Finnish", "French", "Gaelic", "Galician", "Georgian", "German", "Greek", "Gujarati", 
    "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Irish", "Italian", "Japanese", 
    "Kannada", "Kazakh", "Khmer", "Konkhani", "Korean", "Lao", "Latvian", "Lithuanian", 
    "Luxembourg", "Macedonian", "Malay", "Malayalam", "Maltese", "Maori", "Marathi", "Nepal", 
    "Nynorsk", "Oriya", "Polish", "Portuguese", "Punjabi", "Quechua", "Romanian", "Russian", 
    "Serbian", "Slovak", "Slovenian", "Spanish", "Swedish", "Tamil", "Telugu", "Thai", "Turkish", 
    "Turkmen", "Ukrainian", "Urdu", "Uyghur", "Vietnamese", "Welsh"
]

def translate_text(user_text, target_language):
    """Translate a given text to the target language using OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an expert English to {target_language} translator."},
                {"role": "user", "content": f"Translate: {user_text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def translate_xaml(xaml_content, target_language, progress_bar):
    """Translate XAML by extracting 'String' elements and updating their text."""
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.fromstring(xaml_content, parser)

    nsmap = {"system": tree.nsmap.get("system", "clr-namespace:System;assembly=mscorlib")}
    string_elements = tree.xpath("//system:String", namespaces=nsmap)

    total_elements = len(string_elements)
    if total_elements == 0:
        return None

    for idx, string_element in enumerate(string_elements):
        if string_element.text:
            string_element.text = translate_text(string_element.text, target_language)

        progress = int((idx + 1) / total_elements * 100)
        progress_bar.progress(progress)
        time.sleep(0.05)  

    progress_bar.progress(100)

    return etree.tostring(tree, encoding="utf-8", xml_declaration=False, pretty_print=True)

def main():
    st.title("English Text & XAML Translator")
    
    translation_mode = st.radio("Choose input type:", ["Text", "XAML File"])
    target_language = st.selectbox("Select the target language:", languages)

    if translation_mode == "Text":
        user_text = st.text_area("Enter the text in English that you want to translate:")
        
        if st.button("Translate"):
            if user_text:
                with st.spinner("Translating..."):
                    translated_text = translate_text(user_text, target_language)
                    st.success(f"Translated Text in {target_language}:\n\n{translated_text}")
            else:
                st.warning("Please enter some text to translate.")

    elif translation_mode == "XAML File":
        uploaded_file = st.file_uploader("Upload a XAML file", type=["xaml"])

        if uploaded_file:
            if st.button("Translate XAML"):
                progress_bar = st.progress(0)

                with st.spinner("Translating XAML..."):
                    xaml_content = uploaded_file.read()
                    translated_xaml = translate_xaml(xaml_content, target_language, progress_bar)

                    if translated_xaml:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".xaml") as temp_file:
                            temp_file.write(translated_xaml)
                            temp_file_path = temp_file.name

                        st.success("✅ XAML file translated successfully!")
                        st.download_button("📥 Download Translated XAML", translated_xaml, f"{target_language}_translated.xaml", "application/xml")
                    else:
                        st.error("No translatable content found in the XAML file.")

                progress_bar.empty()

if __name__ == "__main__":
    main()