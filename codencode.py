# codencode.py
import streamlit as st
from datetime import datetime
import requests
import io
import zipfile
import os
import base64
import shutil
from bs4 import BeautifulSoup
import json

# Set page configuration
st.set_page_config(page_title="Deen for Everyone", page_icon="🕌", layout="wide")

# Define the path for the Hadith books repository and datasets
HADITH_BOOKS_DIR = "E:/DFE/hadith_books"
HADITH_DATASETS_DIR = "E:/DFE/hadith_datasets"
if not os.path.exists(HADITH_BOOKS_DIR):
    os.makedirs(HADITH_BOOKS_DIR)
if not os.path.exists(HADITH_DATASETS_DIR):
    os.makedirs(HADITH_DATASETS_DIR)

# Sidebar navigation
st.sidebar.title("Navigation")
menu_options = ["Home", "Islamic Calendar", "Qibla Compass", "Digital Library", 
                "Quran Module", "Ahadith Collection", "Islamic Voice Assistant", 
                "Prayer Posture Tracking", "Namaz Timings"]
selected_page = st.sidebar.selectbox("Select a feature", menu_options)

# Main content based on selection
if selected_page == "Home":
    st.title("Welcome to Deen for Everyone 🕌")
    st.write("""
    **Deen for Everyone** is a comprehensive Islamic application designed to support your spiritual journey. 
    Explore features like prayer timings, Quran reading, a Qibla compass, and more—all in one place!
    """)
    st.image("E:/DFE/18118.jpg", caption="A journey to spiritual growth", use_column_width=True)

elif selected_page == "Islamic Calendar":
    st.header("Islamic Calendar 🗓️")

    # Get current date
    today = datetime.today()
    gregorian_date = today.strftime("%B %d, %Y")  # e.g., "March 21, 2025"

    # Fetch Hijri date from Aladhan API
    try:
        response = requests.get(f"http://api.aladhan.com/v1/gToH?date={today.day}-{today.month}-{today.year}")
        data = response.json()
        if data["code"] == 200:
            hijri_date = data["data"]["hijri"]
            hijri_formatted = f"{hijri_date['day']} {hijri_date['month']['en']} {hijri_date['year']} AH"
        else:
            hijri_formatted = "Error fetching Hijri date"
    except Exception as e:
        hijri_formatted = f"Error: {str(e)}"

    # Display current dates
    st.subheader("Today’s Date")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Gregorian (Solar):**")
        st.write(gregorian_date)
    with col2:
        st.write("**Hijri (Lunar):**")
        st.write(hijri_formatted)

    # Simple month selector for dynamic calendar
    st.subheader("View Monthly Calendar")
    current_year = today.year
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox("Select Month", months, index=today.month - 1)
    selected_year = st.number_input("Select Year", min_value=1900, max_value=2100, value=current_year)

    # Fetch Hijri month for selected Gregorian month (approximate)
    try:
        month_index = months.index(selected_month) + 1
        response = requests.get(f"http://api.aladhan.com/v1/gToH?date=1-{month_index}-{selected_year}")
        data = response.json()
        if data["code"] == 200:
            hijri_date = data["data"]["hijri"]
            hijri_month = f"{hijri_date['month']['en']} {hijri_date['year']} AH"
        else:
            hijri_month = "Error fetching Hijri month"
    except Exception as e:
        hijri_month = f"Error: {str(e)}"

    st.write(f"Corresponding Hijri Month (approx.): **{hijri_month}**")

    # Placeholder for a full calendar view
    st.write("Full calendar view with daily Hijri-Gregorian mapping coming soon!")

elif selected_page == "Qibla Compass":
    st.header("Qibla Compass")
    st.write("Find the direction of the Kaaba from your location. Coming soon!")

elif selected_page == "Digital Library":
    st.header("Digital Library")
    st.write("Access a collection of Islamic books. Coming soon!")

elif selected_page == "Quran Module":
    st.header("Quran Module 📖")

    # Fetch available Urdu translations
    st.write("Loading Urdu translations...")
    try:
        response = requests.get("http://api.alquran.cloud/v1/edition?language=ur")
        editions_data = response.json()
        if editions_data["code"] == 200:
            urdu_editions = editions_data["data"]
            urdu_translation_options = {edition["name"]: edition["identifier"] for edition in urdu_editions}
        else:
            urdu_translation_options = {"Jalandhry": "ur.jalandhry"}  # Fallback to default
            st.error("Error fetching Urdu translations. Using default (Jalandhry).")
    except Exception as e:
        urdu_translation_options = {"Jalandhry": "ur.jalandhry"}  # Fallback to default
        st.error(f"Error: {str(e)}. Using default Urdu translation (Jalandhry).")

    # Dropdown for selecting Urdu translation
    selected_urdu_translation = st.selectbox("Select Urdu Translation", list(urdu_translation_options.keys()), index=0)
    selected_urdu_identifier = urdu_translation_options[selected_urdu_translation]

    # Fetch the list of Surahs from the Al-Quran API
    st.write("Loading Surahs...")
    try:
        response = requests.get("http://api.alquran.cloud/v1/surah")
        surah_data = response.json()
        if surah_data["code"] == 200:
            surahs = surah_data["data"]
        else:
            surahs = []
            st.error("Error fetching Surah list.")
    except Exception as e:
        surahs = []
        st.error(f"Error: {str(e)}")

    if surahs:
        # Create a list of Surah names for the dropdown
        surah_names = [f"{surah['number']}. {surah['englishName']} ({surah['name']})" for surah in surahs]
        selected_surah = st.selectbox("Select a Surah", surah_names)
        selected_surah_number = int(selected_surah.split(".")[0])

        # Fetch the selected Surah's text (Arabic, English, and Urdu translations)
        st.write(f"### Reading Surah {selected_surah}")
        try:
            # Fetch Arabic text
            arabic_response = requests.get(f"http://api.alquran.cloud/v1/surah/{selected_surah_number}/ar")
            arabic_data = arabic_response.json()
            if arabic_data["code"] != 200:
                st.error("Error fetching Arabic text.")
                arabic_verses = []
            else:
                arabic_verses = arabic_data["data"]["ayahs"]

            # Fetch English translation (Saheeh International)
            english_response = requests.get(f"http://api.alquran.cloud/v1/surah/{selected_surah_number}/en.sahih")
            english_data = english_response.json()
            if english_data["code"] != 200:
                st.error("Error fetching English translation.")
                english_verses = []
            else:
                english_verses = english_data["data"]["ayahs"]

            # Fetch Urdu translation (based on user selection)
            urdu_response = requests.get(f"http://api.alquran.cloud/v1/surah/{selected_surah_number}/{selected_urdu_identifier}")
            urdu_data = urdu_response.json()
            if urdu_data["code"] != 200:
                st.error("Error fetching Urdu translation.")
                urdu_verses = []
            else:
                urdu_verses = urdu_data["data"]["ayahs"]

            # Display the verses
            if arabic_verses and english_verses and urdu_verses:
                for i, (arabic_verse, english_verse, urdu_verse) in enumerate(zip(arabic_verses, english_verses, urdu_verses), 1):
                    st.write(f"**Verse {i}:**")
                    st.write(f"**Arabic:** {arabic_verse['text']}")
                    st.write(f"**English:** {english_verse['text']}")
                    st.write(f"**Urdu ({selected_urdu_translation}):** {urdu_verse['text']}")
                    st.write("---")
        except Exception as e:
            st.error(f"Error fetching Surah text: {str(e)}")

        # Download options
        st.subheader("Download Options")
        
        # Download the selected Surah
        if st.button(f"Download Surah {selected_surah} (Text)"):
            surah_text = f"Surah {selected_surah}\n\n"
            for i, (arabic_verse, english_verse, urdu_verse) in enumerate(zip(arabic_verses, english_verses, urdu_verses), 1):
                surah_text += f"Verse {i}:\n"
                surah_text += f"Arabic: {arabic_verse['text']}\n"
                surah_text += f"English: {english_verse['text']}\n"
                surah_text += f"Urdu ({selected_urdu_translation}): {urdu_verse['text']}\n\n"
            
            st.download_button(
                label=f"Download Surah {selected_surah}.txt",
                data=surah_text,
                file_name=f"Surah_{selected_surah_number}_{surahs[selected_surah_number-1]['englishName']}.txt",
                mime="text/plain"
            )

        # Download the entire Quran
        if st.button("Download Entire Quran (Text)"):
            st.write("Fetching the entire Quran... This may take a moment.")
            full_quran_text = "The Holy Quran\n\n"
            try:
                for surah_number in range(1, 115):  # Surahs 1 to 114
                    arabic_response = requests.get(f"http://api.alquran.cloud/v1/surah/{surah_number}/ar")
                    english_response = requests.get(f"http://api.alquran.cloud/v1/surah/{surah_number}/en.sahih")
                    urdu_response = requests.get(f"http://api.alquran.cloud/v1/surah/{surah_number}/{selected_urdu_identifier}")
                    arabic_data = arabic_response.json()
                    english_data = english_response.json()
                    urdu_data = urdu_response.json()
                    
                    if arabic_data["code"] == 200 and english_data["code"] == 200 and urdu_data["code"] == 200:
                        surah_name = arabic_data["data"]["englishName"]
                        full_quran_text += f"Surah {surah_number}: {surah_name}\n\n"
                        arabic_verses = arabic_data["data"]["ayahs"]
                        english_verses = english_data["data"]["ayahs"]
                        urdu_verses = urdu_data["data"]["ayahs"]
                        for i, (arabic_verse, english_verse, urdu_verse) in enumerate(zip(arabic_verses, english_verses, urdu_verses), 1):
                            full_quran_text += f"Verse {i}:\n"
                            full_quran_text += f"Arabic: {arabic_verse['text']}\n"
                            full_quran_text += f"English: {english_verse['text']}\n"
                            full_quran_text += f"Urdu ({selected_urdu_translation}): {urdu_verse['text']}\n\n"
                        full_quran_text += "===\n\n"
                    else:
                        st.warning(f"Could not fetch Surah {surah_number}.")
                
                # Provide the download button for the entire Quran
                st.download_button(
                    label="Download Full Quran.txt",
                    data=full_quran_text,
                    file_name="Full_Quran.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Error fetching the entire Quran: {str(e)}")

elif selected_page == "Ahadith Collection":
    st.header("Ahadith Collection 📜")

    # Admin Section for Uploading Hadith Books
    st.subheader("Admin: Upload Hadith Books")
    admin_password = "admin123"  # Simple password for admin access (replace with a more secure method in production)
    password_input = st.text_input("Enter Admin Password", type="password")
    
    if password_input == admin_password:
        st.write("Admin access granted!")
        uploaded_file = st.file_uploader("Upload a Hadith Book (PDF or Text)", type=["pdf", "txt"])
        if uploaded_file is not None:
            # Save the uploaded file to the hadith_books directory
            file_path = os.path.join(HADITH_BOOKS_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Hadith book '{uploaded_file.name}' uploaded successfully!")
    else:
        if password_input:  # Show error only if the user has entered a password
            st.error("Incorrect password. Please try again.")

    # User Section for Viewing/Downloading Uploaded Hadith Books
    st.subheader("Uploaded Hadith Books")
    hadith_books = [f for f in os.listdir(HADITH_BOOKS_DIR) if f.endswith((".pdf", ".txt"))]
    
    if not hadith_books:
        st.write("No Hadith books available yet.")
    else:
        selected_book = st.selectbox("Select a Hadith Book to View or Download", hadith_books)
        
        if selected_book:
            book_path = os.path.join(HADITH_BOOKS_DIR, selected_book)
            
            # Display the book
            st.write(f"### Viewing: {selected_book}")
            if selected_book.endswith(".pdf"):
                with open(book_path, "rb") as file:
                    pdf_data = file.read()
                    base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
            else:  # Text file
                with open(book_path, "r", encoding="utf-8") as file:
                    text_content = file.read()
                    st.text_area("Hadith Text", text_content, height=300)

            # Option to download the book
            with open(book_path, "rb") as file:
                st.download_button(
                    label=f"Download {selected_book}",
                    data=file,
                    file_name=selected_book,
                    mime="application/pdf" if selected_book.endswith(".pdf") else "text/plain"
                )

    # Load Hadith Datasets
    st.subheader("Browse Hadith Datasets")
    scholars = ["abudawud", "bukhari", "ibnmajah", "muslim", "tirmidhi"]
    scholar_files = {scholar: f"{scholar}.js" for scholar in scholars}
    selected_scholar = st.selectbox("Select Scholar (Dataset)", scholars)

    # Load the selected scholar's dataset
    hadith_data = []
    try:
        file_path = os.path.join(HADITH_DATASETS_DIR, scholar_files[selected_scholar])
        with open(file_path, "r", encoding="utf-8") as file:
            # Read the file content
            content = file.read()
            # If the file contains JavaScript syntax like "var data = {...};", strip it
            if content.startswith("var "):
                content = content.split("=", 1)[1].strip()
                if content.endswith(";"):
                    content = content[:-1]
            # Parse the JSON content
            data = json.loads(content)
            hadith_data = data.get("hadith", [])
    except FileNotFoundError:
        st.error(f"Dataset file for {selected_scholar} not found. Please ensure {scholar_files[selected_scholar]} exists in {HADITH_DATASETS_DIR}.")
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON for {selected_scholar}: {str(e)}")
    except Exception as e:
        st.error(f"Error loading dataset for {selected_scholar}: {str(e)}")

    if hadith_data:
        # Option 1: Select Hadith by ID
        st.write("### Select Hadith by ID")
        hadith_ids = [str(hadith["id"]) for hadith in hadith_data]
        selected_hadith_id = st.selectbox("Select Hadith ID", hadith_ids)
        
        selected_hadith = next((hadith for hadith in hadith_data if str(hadith["id"]) == selected_hadith_id), None)
        if selected_hadith:
            st.write("#### Hadith Details")
            st.write(f"**ID:** {selected_hadith['id']}")
            st.write(f"**Header:** {selected_hadith['header']}")
            st.write(f"**Hadith (English):** {selected_hadith['hadith_english']}")
            st.write(f"**Book:** {selected_hadith['book']}")
            st.write(f"**Reference Number:** {selected_hadith['refno']}")
            st.write(f"**Book Name:** {selected_hadith['bookName'].strip()}")
            st.write(f"**Chapter Name:** {selected_hadith['chapterName']}")

        # Option 2: Browse Hadith with Pagination
        st.write("### Browse Hadith Collection")
        items_per_page = 5
        total_items = len(hadith_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        page_number = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page_number - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        for hadith in hadith_data[start_idx:end_idx]:
            st.write("---")
            st.write(f"**ID:** {hadith['id']}")
            st.write(f"**Header:** {hadith['header']}")
            st.write(f"**Hadith (English):** {hadith['hadith_english']}")
            st.write(f"**Book:** {hadith['book']}")
            st.write(f"**Reference Number:** {hadith['refno']}")
            st.write(f"**Book Name:** {hadith['bookName'].strip()}")
            st.write(f"**Chapter Name:** {hadith['chapterName']}")

    # Fetch Specific Hadith from Sunnah.com (Previous Functionality)
    st.subheader("Fetch Specific Hadith from Sunnah.com")
    scholars = ["abudawud", "bukhari", "ibnmajah", "muslim", "tirmidhi"]
    selected_scholar = st.selectbox("Select Scholar (Sunnah.com)", scholars)
    hadith_number = st.text_input("Enter Hadith Number (e.g., 1, 2, 3)", value="1")

    if st.button("Fetch Hadith from Sunnah.com"):
        st.write(f"Fetching Hadith {hadith_number} from {selected_scholar.capitalize()}...")
        try:
            # Fetch the Hadith page
            url = f"https://sunnah.com/{selected_scholar}:{hadith_number}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            soup = BeautifulSoup(response.text, "lxml")
            hadiths = soup.find_all("div", class_="mainContainer")

            if hadiths:
                for hadith in hadiths:
                    book_name = hadith.find("div", class_="book_page_english_name").text.strip() if hadith.find("div", class_="book_page_english_name") else "Unknown"
                    chapter_name = hadith.find("div", class_="englishchapter").text.strip() if hadith.find("div", class_="englishchapter") else "Unknown"
                    narrator = hadith.find("div", class_="hadith_narrated").text.strip() if hadith.find("div", class_="hadith_narrated") else "Unknown"
                    hadith_text = hadith.find("div", class_="text_details").text.strip() if hadith.find("div", class_="text_details") else "No text available"
                    reference = hadith.find("div", class_="hadith_reference_sticky").text.strip() if hadith.find("div", class_="hadith_reference_sticky") else "No reference"

                    hadith_details = {
                        "Book Name": book_name,
                        "Chapter Name": chapter_name,
                        "Narrated By": narrator,
                        "Hadith": hadith_text,
                        "Reference": reference
                    }

                    # Display the Hadith details
                    st.write("### Hadith Details (Sunnah.com)")
                    for key, value in hadith_details.items():
                        st.write(f"**{key}:** {value}")
                    break  # Only display the first matching Hadith
            else:
                st.error("No Hadith found for the given scholar and number.")
        except Exception as e:
            st.error(f"Error fetching Hadith: {str(e)}")

elif selected_page == "Islamic Voice Assistant":
    st.header("Islamic Voice Assistant")
    st.write("Ask and get Islamic content. Coming soon!")

elif selected_page == "Prayer Posture Tracking":
    st.header("Prayer Posture Tracking")
    st.write("Learn correct Salah postures with AI. Coming soon!")

elif selected_page == "Namaz Timings":
    st.header("Namaz Timings")
    st.write("Get accurate prayer times and Adhan notifications. Coming soon!")

# Footer
st.sidebar.write("---")
st.sidebar.write("Developed by M.Hashir and Junaid | Powered by AI")