# Bizcardx
# Extracting data from business card
## Introduction

BizCardX is a Streamlit application that effortlessly streamlines business card data extraction through advanced OCR technology. Users can easily upload card images to retrieve essential details, including company names, cardholder names, contact information, and more. With a strong focus on data security and user authentication, BizCardX ensures secure data storage and offers streamlined management via the user-friendly Streamlit UI. Experience an efficient, secure, and user-friendly solution for managing business card information effortlessly with BizCardX.

## What is EasyOCR?
EasyOCR, as the name suggests, is a Python package that allows computer vision developers to effortlessly perform Optical Character Recognition.It is a Python library for Optical Character Recognition (OCR) that allows you to easily extract text from images and scanned documents. In my project I am using easyOCR to extract text from business cards.

When it comes to OCR, EasyOCR is by far the most straightforward way to apply Optical Character Recognition:

* The EasyOCR package can be installed with a single pip command.

* The dependencies on the EasyOCR package are minimal, making it easy to configure your OCR development environment.

* Once EasyOCR is installed, only one import statement is required to import the package into your project.

* From there, all you need is two lines of code to perform OCR — one to initialize the Reader class and then another to OCR the image via the readtext function.

  
## Overview
  BizCardX aims to simplify the process of extracting and managing information from business cards. The tool offers the following features:

Extraction of key information from business cards: company name, cardholder name, designation, contact details, etc.

Storage of extracted data in a MySQL database for easy access and retrieval.

GUI built with Streamlit for a user-friendly interface.

User options to upload, extract, and modify business card data.

## E T L Process
a) Extract data

Extract relevant information from business cards by using the easyOCR library

b) Process and Transform the data

After the extraction process, process the extracted data based on Company name, Card Holder, Designation, Mobile Number, Email, Website, Area, City, State, and Pincode is converted into a data frame.

c) Load data

After the transformation process, the data is stored in the SQL database.

## Acknowledgements
* EasyOCR Documentation
* Python pandas documentation
* Python sql-connector documentation
* Streamlit Documentation

