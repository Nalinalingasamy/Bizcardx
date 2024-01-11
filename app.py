!pip install easyocr
!pip install streamlit
!pip install streamlit_option_menu

%%writefile app.py
# Importing libraries
import easyocr
import cv2
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import re
import pandas as pd
from io import BytesIO
from PIL import Image  # Import Image module from PIL

# Initialize OCR reader outside the function
reader = easyocr.Reader(['en'])

# extracting data from image
def get_details_from_image(uploaded_image_data):
    image = Image.open(BytesIO(uploaded_image_data))
    image_array = np.array(image)
    text_ = reader.readtext(image_array)
    text_datas = []
    text_datas.clear()
    for i in text_:
        text = i[1]
        text_datas.append(text)
    return text_datas


# Using regular expression to extract details
def get_text_df(text_datas, uploaded_file):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    website_pattern = r'[www|WWW|wwW|https?://|ftp://]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+'
    phone_pattern = r'(?:\+)?\d{3}-\d{3}-\d{4}'
    phone_pattern2 = r"(?:\+91[-\s])?(?:\d{4,5}[-\s])?\d{3}[-\s]?\d{4}"
    name_pattern = r'[A-Za-z]+(?:\s[A-Za-z]+)?\b'
    designation_pattern = r'\b[A-Za-z\s.-]+\b'
    pincode_pattern = r'\b\d{6}\b'
    address_pattern = r'\d+\s[A-Za-z\s,]+'
    company_index = len(text_datas) - 1

    final_data = {'Name': text_datas[0], 'Designation': text_datas[1], 'Company_name': text_datas[company_index],
                  'Contact_number': "NA", 'Mail_id': "NA", 'Website': "NA", 'Address': "NA", 'Pincode': "NA"}

    for details in text_datas:
        address = re.search(address_pattern, details)
        if address:
            final_data['Address'] = address.group()

        pincode = re.search(pincode_pattern, details)
        if pincode:
            final_data['Pincode'] = pincode.group()

        phone_number = re.search(phone_pattern + '|' + phone_pattern2, details)
        if phone_number:
            final_data['Contact_number'] = phone_number.group()

        Mail_id = re.search(email_pattern, details)
        if Mail_id:
            final_data['Mail_id'] = Mail_id.group()

        website = re.search(website_pattern, details)
        if website:
            final_data['Website'] = website.group()

    final_df = pd.DataFrame([final_data])
    # Extract filename or any other relevant identifier from the uploaded file
    file_identifier = uploaded_file.name if uploaded_file else "unknown"
    final_df['image'] = file_identifier
    return final_df, final_data

# Table creation (bizcard_data)
def table_creation_sql():
    con = sqlite3.connect("business_card.db", check_same_thread=False)
    table_create = '''CREATE TABLE IF NOT EXISTS bizcard_data (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT,
                        Designation TEXT,
                        Company_name TEXT,
                        Contact_number TEXT,
                        Mail_id TEXT,
                        Website TEXT,
                        Address TEXT,
                        Pincode TEXT,
                        Image BLOB
                    );'''
    con.execute(table_create)
    con.close()


# Inserting DF to SQLite
def insert_to_sql(final_df):
    con = sqlite3.connect("business_card.db", check_same_thread=False)
    final_df.to_sql('bizcard_data', con, if_exists='append', index=False)
    con.close()
    st.success("Details inserted successfully to database!!!")

# Getting id details
def get_id_details(con):
    details = []
    cur = con.cursor()
    cur.execute("SELECT ID FROM bizcard_data")
    for record in cur:
        details.append(record)
    ids_columns = pd.DataFrame(details, columns=['ID'])
    return ids_columns

# Display contents
def display_contents(final_data):
    st.text(f"Name: {final_data['Name']}")
    st.text(f"Designation: {final_data['Designation']}")
    st.text(f"Company_name: {final_data['Company_name']}")
    st.text(f"Contact_number: {final_data['Contact_number']}")
    st.text(f"Mail_id: {final_data['Mail_id']}")
    st.text(f"Website: {final_data['Website']}")
    st.text(f"Address: {final_data['Address']}")
    st.text(f"Pincode: {final_data['Pincode']}")

def get_updates(final_df):
    name = st.text_input("Name:", f"{final_df['Name']}")
    designation = st.text_input("Designation:", f"{final_df['Designation']}")
    company_name = st.text_input("Company_name:", f"{final_df['Company_name']}")
    contact_number = st.text_input("Contact_number:", f"{final_df['Contact_number']}")
    mail_id = st.text_input("Mail_id:", f"{final_df['Mail_id']}")
    website = st.text_input("Website:", f"{final_df['Website']}")
    address = st.text_input("Address:", f"{final_df['Address']}")
    pincode = st.text_input("Pincode:", f"{final_df['Pincode']}")

    updated_data = [name, designation, company_name, contact_number, mail_id, website, address, pincode]
    return updated_data

def display_card_details(image_data, details_data):
    st.subheader("Business Card Details")
    st.image(image_data, caption='Uploaded Card', use_column_width=True)
    # Display details as data fields
    st.text(f"Name: {details_data['Name']}")
    st.text(f"Designation: {details_data['Designation']}")
    st.text(f"Company_name: {details_data['Company_name']}")
    st.text(f"Contact_number: {details_data['Contact_number']}")
    st.text(f"Mail_id: {details_data['Mail_id']}")
    st.text(f"Website: {details_data['Website']}")
    st.text(f"Address: {details_data['Address']}")
    st.text(f"Pincode: {details_data['Pincode']}")

def get_details(ID):
    ids_query = f"SELECT * FROM bizcard_data WHERE ID={ID};"
    details = []
    cur.execute(ids_query)
    for record in cur:
        details.append(record)
    columns_fields = ['ID', 'Name', 'Designation', 'Company_name', 'Contact_number', 'Mail_id', 'Website', 'Address',
                       'Pincode', 'Image']
    df = pd.DataFrame(details, columns=columns_fields)
    return df

def update_sql(updated_data, selected_id):
    update_query = f'''UPDATE bizcard_data SET Name=?, Designation=?, Company_name=?, Contact_number=?,
                        Mail_id=?, Website=?, Address=?, Pincode=?
                        WHERE ID={selected_id}'''
    values = [updated_data[0], updated_data[1], updated_data[2], updated_data[3],
              updated_data[4], updated_data[5], updated_data[6], updated_data[7]]
    cur.execute(update_query, values)
    st.success("Records updated successfully!")

def delete_sql_record(selected_id):
    delete_query = f"DELETE FROM bizcard_data WHERE ID={int(selected_id)}"
    cur.execute(delete_query)
    con.commit()
    st.success(f"Record with ID {selected_id} deleted successfully!")

def truncate_sql_record():
    cur.execute("DELETE FROM bizcard_data")
    con.commit()
    cur.execute("VACUUM")
    con.commit()
    st.success("All Records deleted successfully!")

if __name__ == "__main__":
    # Creating the 'bizcard_data' table
    table_creation_sql()

    # Setting up page configuration
    st.title(":green[BizCardX: Extracting Business Card Data with OCR]")

    # Creating sidebar for option menu
    with st.sidebar:
        st.header(":green[**WELCOME TO DASHBOARD**]")
        st.write("The User-Friendly Tool created by Nalina Lingasamy for the capstone project in Data Science course")
        st.image("/content/Data extraction-rafiki.png")
        selected = option_menu("Menu", ["Home", "Fetch Details", "Retrieve Details"],
                               icons=["house", "cloud-upload", "pencil-square"],
                               menu_icon="menu-button-wide",
                               default_index=0,
                               styles={"nav-link": {"font-size": "15px", "text-align": "left", "margin": "-2px",
                                                   "--hover-color": "#7db086"},
                                       "nav-link-selected": {"background-color": "#0b7d20"}})


    if selected == "Home":
        st.header(":black[Project Overview]")
        st.write(" ")
        st.subheader(":green[Skills used:]")
        st.write(" ")
        st.write("**# Python**")
        st.write("**# Sqlite3**")
        st.write("**# EasyOCR**")  
        st.write("**# Streamlit**")
        st.write(" ")
        st.subheader(":green[Overview:]")
        st.write(" ")
        st.write("BizCardX is a Streamlit application that effortlessly do business card data extraction through "
                "advanced OCR technology.")
        st.write("After extracting data from business card, the datas are uploaded to Sqlite3 database.")
        st.write("Once data is loaded into database,it can be retrieved to do changes in datas through streamlit app ")
        column1,column2 = st.columns(2)
        with column1:
           st.image("/content/Data extraction-bro.png")
        with column2:
           st.image("/content/Data extraction-amico.png")
    # Initialize session_state
    if 'uploaded_image_data' not in st.session_state:
        st.session_state.uploaded_image_data = None

    if 'details_fetched' not in st.session_state:
        st.session_state.details_fetched = False


    if selected == "Fetch Details":
        uploaded_file = st.file_uploader("Upload a business_card", type=["jpg", "png", "jpeg"])
        
        if uploaded_file is not None:
            if st.button('Fetch Details'):
                with st.spinner('Please Wait, the data is being extracted!!!'):
                    st.session_state.uploaded_image_data = uploaded_file.read()
                    image = Image.open(BytesIO(st.session_state.uploaded_image_data))
                    image_array = np.array(image)
                    result = get_details_from_image(st.session_state.uploaded_image_data)
                    
                    # Check if details are fetched successfully
                    if result:
                        final_df, final_data = get_text_df(result, uploaded_file)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Uploaded Image")
                            st.image(image, caption='Uploaded Card')
                        with col2:
                            st.subheader("Extracted Business Card Data")
                            display_contents(final_data)
                            st.session_state.details_fetched = True  # Set details_fetched to True
                    else:
                        st.warning("No details found. Please upload a valid image.")

        # Check if details are fetched before enabling the button
        if st.button('Save Details to Database', disabled=not st.session_state.details_fetched):
            if st.session_state.uploaded_image_data is not None and st.session_state.details_fetched:
                with st.spinner('Please Wait, transferring data!!!'):
                    result = get_details_from_image(st.session_state.uploaded_image_data)
                    final_df, final_data = get_text_df(result, uploaded_file)
                    insert_to_sql(final_df)
            else:
                st.warning("Please fetch details before saving to the database.")

    # Initialize session_state
    if 'uploaded_image_data' not in st.session_state:
        st.session_state.uploaded_image_data = None

    if 'details_fetched' not in st.session_state:
        st.session_state.details_fetched = False

    # Page for retrieving details from the database
    if selected == "Retrieve Details":

        # Establish SQLite connection
        con = sqlite3.connect("business_card.db", check_same_thread=False)
        cur = con.cursor()

        id_value = get_id_details(con)  # pass con to the function

        if id_value is not None:
            ids = id_value['ID'].unique()
            selected_id = st.selectbox('Select the id to display details', ids)

            if selected_id:
                detail_df = get_details(selected_id)  # calling function
                record_dict = detail_df.to_dict(orient='records')[0]
                image_data = record_dict['Image']

                # Display image and details in two columns
                col1, col2= st.columns(2)
                with col1:
                    display_card_details(image_data, record_dict)

                with col2:
                    st.subheader("Actions")
                    # Update button
                    updated_data = get_updates(record_dict)  # calling function
                    update_condition = st.button('Update')
                    if update_condition:
                        if len(updated_data) == 8:
                            update_sql(updated_data, selected_id)  # calling function

                     # Delete button
                    delete_condition = st.button('Delete')
                    if delete_condition:
                        delete_sql_record(selected_id)  # calling function

                    # Truncate button
                    truncate_condition = st.button('Truncate')
                    if truncate_condition:
                        truncate_sql_record()  # calling function

        # Close the SQLite connection
        con.close()
