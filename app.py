#importing lib
import easyocr
import cv2
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import re
import pandas as pd
from PIL import Image,ImageOps
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

def get_connections():#for usage connection functions is created separately
        connection1 = sqlite3.connect("bizcardx.db")
        curs1 = connection1.cursor()
        engine = create_engine('sqlite:///bizcardx.db',echo=True)
        return connection1,curs1,engine
    
def get_details_from_image(image):#extracting data from image
        #extracting data from image
        image_ = cv2.imread("image")
        reader = easyocr.Reader(['en'])
        #text_ = reader.readtext(image)
        #text_
        image_array = np.array(image_)  # Convert to NumPy array
        text_ = reader.readtext(image_array)
        text_datas=[]
        text_datas.clear()
        for i in text_:
          text = i[1]
          text_datas.append(text)
        return text_datas
    
def get_text_df(text_datas,uploaded_file):
        #using regular expression extract details
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        website_pattern = r'[www|WWW|wwW|https?://|ftp://]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+'
        phone_pattern = r'(?:\+)?\d{3}-\d{3}-\d{4}'
        phone_pattern2 = r"(?:\+91[-\s])?(?:\d{4,5}[-\s])?\d{3}[-\s]?\d{4}"
        name_pattern =  r'[A-Za-z]+(?:\s[A-Za-z]+)?\b'
        designation_pattern = r'\b[A-Za-z\s.-]+\b'
        pincode_pattern = r'\b\d{6}\b'
        #address_pattern = r'(?:No.\s\d+|\d+\s|\d+|[A-Za-z\s,]+)+'
        address_pattern = r'\d+\s[A-Za-z\s,]+'
        company_index = len(text_datas)-1
        #company_name = r'[A-Za-z]+(?:\s[A-Za-z]+)?\b'

        final_data = {'Name': text_datas[0], 'Designation': text_datas[1], 'Company_name': text_datas[company_index],
                      'Contact_number': "NA",'Mail_id': "NA", 'Website': "NA", 'Address': "NA", 'Pincode': "NA"}
        
        for details in text_datas:
            address= re.search(address_pattern, details)
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

        final_df= pd.DataFrame([final_data])
        final_df['image']=uploaded_file
        return final_df,final_data
    
def table_creation_sql():
        table_create = '''create table if not exists bizcardx (ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                          Name TEXT,Designation TEXT,Company_name TEXT,Contact_number TEXT,Mail_id TEXT,
                          Website TEXT,Address TEXT,Pincode TEXT,Image BLOB);'''
        connection1,curs1,engine = get_connections()
        curs1.execute(table_create)
        
def insert_to_sql(final_df):
        connection1,curs1,engine = get_connections()
        final_df.to_sql('bizcardx', engine, if_exists='append', index=False)
        st.success("Details inserted successfully!")
        
def get_id_details():#getting id details
        connection1,curs1,engine = get_connections()
        details=[]
        curs1.execute("SELECT ID FROM bizcardx")
        for record in curs1:
            details.append(record)
        ids_columns=pd.DataFrame(details,columns=['ID']
        return ids_column
                                 
def display_contents(final_data):#display contents
        st.text(f"Name: {final_data['Name']}")
        st.text(f"Designation: {final_data['Designation']}")
        st.text(f"Company_name: {final_data['Company_name']}")
        st.text(f"Contact_number: {final_data['Contact_number']}")
        st.text(f"Mail_id: {final_data['Mail_id']}")
        st.text(f"Website: {final_data['Website']}")
        st.text(f"Address: {final_data['Address']}")
        st.text(f"Pincode: {final_data['Pincode']}")
                                 
def get_updates(detail_df):
        name=st.text_input("Name:",f"{detail_df['Name']}")
        designation=st.text_input("Designation:",f"{detail_df['Designation']}")
        company_name=st.text_input("Company_name:",f"{detail_df['Company_name']}")
        contact_number=st.text_input("Contact_number:",f"{detail_df['Contact_number']}")
        mail_id=st.text_input("Mail_id:",f"{detail_df['Mail_id']}")
        website=st.text_input("Website:",f"{detail_df['Website']}")
        address=st.text_input("Address:",f"{detail_df['Address']}")
        pincode=st.text_input("Pincode:",f"{detail_df['Pincode']}")
       
        updated_data =[name,designation,company_name,contact_number,mail_id,website,address,pincode]
        return updated_data
                                 
def get_details(ID):
        ids_query=f"SELECT * FROM bizcardx Where ID={ID};"
        connection1,curs1,engine = get_connections()
        details=[]
        curs1.execute(ids_query)
        for record in curs1:
            details.append(record)
        columns_fields = ['ID', 'Name', 'Designation', 'Company_name', 'Contact_number', 'Mail_id', 'Website', 'Address', 'Pincode', 'Image']
        df = pd.DataFrame(details, columns=columns_fields)
        return df
                                 
def update_sql(updated_data,selected_id):
        update_query=f'''UPDATE bizcardx SET Name=?, Designation=?, Company_name=?, Contact_number=?, Mail_id=?, Website=?, Address=?, Pincode=? 
                            WHERE ID={selected_id}'''
        values=[updated_data[0], updated_data[1], updated_data[2], updated_data[3],
                        updated_data[4], updated_data[5], updated_data[6], updated_data[7]]
        connection1,curs1,engine = get_connections()
        curs1.execute(update_query,updated_data)
        connection1.commit()
        st.success("Record updated successfully!")
                                 
def delete_sql_record(selected_id):
        delete_query=f"DELETE FROM bizcardx WHERE ID={int(selected_id)}"
        connection1,curs1,engine = get_connections()
        curs1.execute(delete_query)
        connection1.commit()
        st.success(f"Record with ID {selected_id} deleted successfully!")

def truncate_sql_record():
    try:
        connection1,curs1,engine = get_connections()
        curs1.execute("DELETE FROM bizcardx")
        connection1.commit()
        curs1.execute("VACUUM")
        connection1.commit()
        st.success(f"All Records deleted successfully!")
                                 
# Setting up page configuration

st.title(":yellow[BizCardX: Extracting Business Card Data with OCR]")
st.markdown(f""" <style>.stApp {{
                        background:url("https://C:/Users/NANDHU/Desktop/wooden-background-1jmd98j7kzv4h8bf (1).jpg");
                        background-size: cover}}
                     </style>""", unsafe_allow_html=True)


#creating sidebar for option menu
with st.sidebar:
           img = Image.open(r"C:\\Users\\NANDHU\\Desktop\\data-extraction.jpg)
           st.image(img)
           st.header(":blue[**WELCOME TO DASHBOARD**]")
           st.write("The User-Friendly Tool created by Nalina Lingasamy for capstone project in Data Science course")          
           selected = option_menu("Menu", ["Home","Fetch Details","Retrive Details"], 
                icons=["house","cloud-upload","pencil-square"],
                menu_icon= "menu-button-wide",
                default_index=0,
                styles={"nav-link": {"font-size": "15px", "text-align": "left", "margin": "-2px", "--hover-color": "#8F9CAE"},
                        "nav-link-selected": {"background-color": "#6F36AD"}})
         

if selected == "Home":

    st.write("BizCardX is a Streamlit application that effortlessly streamlines business card data extraction through advanced OCR technology.")
    st.write(" ")
    image1 = Image.open(r"C:\\Users\\NANDHU\\Desktop\\1_R5ycr8667WiiMfXSlN6RCQ.png")
    st.image(image1,width= 305)
    
if selected == "Fetch Details": #page for text extraction and save into sql
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        file_name = uploaded_file.name
        st.write("filename:", file_name)
                            
        if st.button('Fetch Details'):
          with st.spinner('Please Wait,fetching data!!!'):
            #for reading the file
            uploaded_image_data = uploaded_file.read()
            image = Image.open(BytesIO(uploaded_image_data))
            image_array = np.array(image)
            image_bytes = image_array.tobytes()
            result=get_details_from_image(image) #calling function
            final_df,final_data=get_text_df(result,uploaded_image_data) #calling function
            col1, col2 = st.columns(2)
            with col1:
              st.subheader("Uploaded Image")
              st.image(image, caption='Uploaded Card')
            with col2:
              st.subheader("Extracted Business Card Data")
              st.subheader("Data Fields")
              display_contents(final_data)
                            
         if st.button('Save Details to Database'):
          with st.spinner('Please Wait,transferring data!!!'):
            table_creation_sql() #calling function
            insert_to_sql(final_df) #calling function
            
if selected == "Retrive Details":
      st.subheader("Retrieve Data from Database")
      id_value=get_id_details() #calling function

      if id_value is not None:
        ids=id_value['ids'].unique()
        selected_id=st.selectbox('Select the id to display details',ids)

        if selected_id:
          detail_df=get_details(selected_id) #calling function
          st.markdown("""<style>.custom-column {width: 33.33% !important; /* Set equal width for all columns */
            height: 400px !important; /* Set equal height for all columns */display: inline-block;
            margin: 10px; /* Add margin between columns if needed */}</style>""",unsafe_allow_html=True)
          #inorder to use values here series dataframe is converted to dict
          record_dict = detail_df.to_dict(orient='records')[0]
          image_data=record_dict['image']
          col1, col2 ,col3= st.columns(3)
          with col1:
            st.markdown("### Business Card")
            st.image(image_data)
            truncate_condition=st.button('Clear all Records (Truncate)')
            if truncate_condition:
              truncate_sql_record() #calling function

          with col2:
            st.markdown("### Details")
            display_contents(record_dict) #calling function
            delete_condition=st.button('Delete the Record')
            if delete_condition:
              delete_sql_record(selected_id)  #calling function

          with col3:
            st.markdown("### Update Details")
            updated_data=get_updates(record_dict) #calling function
            update_condition=st.button('Update the Record')
            if update_condition:
              if len(updated_data) == 8:
                update_sql(updated_data,selected_id)  #calling function
