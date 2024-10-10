import re
import os
import sys
import ssl
import time
import queue
import socket
import logging
import difflib
import imaplib
import smtplib
import getpass
import calendar  
import itertools
import html2text
import threading
import email.utils
import configparser
import pandas as pd
import datetime as dt
import yfinance as yf
import concurrent.futures

from queue import Queue
from selenium import webdriver
from yaspin import yaspin,Spinner            
from yaspin.spinners import Spinners            
from alive_progress import alive_bar
from email.mime.text import MIMEText
from email.mime.image import MIMEImage            
from holidays.countries import UnitedStates
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from selenium.common.exceptions import WebDriverException



##############################################################################################################################
#import io
#import requests
#from requests.exceptions import ConnectionError
#
# List of URLs for NASDAQ, AMEX, and NYSE tickers
#TICKER_LINKS            = ["https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download",
#                           "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download",
#                           "https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download"]
#TICKER_DICT             = download_stock_tickers()
##############################################################################################################################

#######################################################################################################################################################################
# def download_stock_tickers():
#     global TICKER_LINKS                                                                             # List of URLs for stock tickers
#     ticker_df = pd.DataFrame()                                                                      # Create dataframe to store all ticker symbols

#     # Loop over NASDAQ, AMEX, and NYSE ticker links
#     for link in TICKER_LINKS:
#         try:
#             req = requests.get(link, headers={"user-agent":"Mozilla"}).content.decode('utf-8')      # Download ticker symbol/data from link   
#             df = pd.read_csv(io.StringIO(req), error_bad_lines=False)                               # Store ticker symbol/data into dataframe
#             ticker_df = ticker_df.append(df)                                                        # Append to end of ticker dataframe

#         except ConnectionError:                                                                 
#             logging.warning(f"*** ConnectionError: Could not access {link}. . .")                   # Add "None" value to dataframe if website link is not accessable
#             ticker_df = ticker_df.append(None)

#         except Exception:
#             logging.error(f"*** Unexpected Exception Occured! ***", exc_info=True)                  # Return "None" value if unknown exception occured
#             return None
    
#     if(ticker_df.empty):                                                                            # Return "None" value if the dataframe is empty
#         logging.error(">>> Could Not Download NASDAQ, AMEX, and NYSE Ticker Data. . .")
#         return None

#     ticker_df.drop_duplicates(inplace=True)                                                         # Remove duplicate ticker entries, if any
#     ticker_df.reset_index(drop=True, inplace=True)                                                  # Reset dataframe indexes

#     # Remove unnecessary columns from ticker dataframe (Keep columns "Symbol", "Name", and "Sector")
#     ticker_df.drop(columns=['LastSale', 'MarketCap', 'IPOyear', 'industry', 'Summary Quote', 'Unnamed: 8'], inplace=True) 

#     return ticker_df.to_dict()                                                                      # Return dataframe as dictionary
#######################################################################################################################################################################

