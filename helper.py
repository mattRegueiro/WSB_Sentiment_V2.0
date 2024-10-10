"""
----------------
helper.py
----------------
Contains functions used accomplish general tasks by the program.

"""

import globals
from imports import *

def get_all_stock_tickers():
    if not os.path.exists("Stock_Tickers"):                                 # If Stock_Tickers directory is not found, return "None" value
        logging.error(">>> ../Stock_Tickers directory not found!. . .")
        return None
    
    ticker_df = pd.DataFrame()                                              # Else directory is found, create empty dataframe
    for filename in os.listdir("Stock_Tickers"):                            # Iterate through all csv files in directory
        try:
            df = pd.read_csv(f"Stock_Tickers/{filename}")                   # Read csv file and append to dataframe
            ticker_df = ticker_df.append(df)
        
        except IOError:                                                     # If the csv file could not be read
            logging.warning(f"*** IOError: Could not read csv file {filename}. . .")

        except Exception:                                                   # If an Unknown Exception occured
            logging.error(f"*** Unexpected Exception Occured! ***", exc_info=True)
            return None

    ticker_df.drop_duplicates(inplace=True)                                 # Remove duplicate ticker entries, if any                                                   
    ticker_df.reset_index(drop=True, inplace=True)                          # Reset dataframe indexes      

    return ticker_df.to_dict()                                              # Return dictionary w/ list of stock tickers



def get_words_to_ignore():
    # In some cases, common words or acronyms are interpreted as stock tickers. To reduce the chance of seeing false tickers,
    # a text document is created (words_to_ignore.txt) that contains a list of words/phrases that will be ignored in find_mentioned_tickers()

    file = open('Data/words_to_ignore.txt', 'r')                                    # Open text file containing list of words to ignore
    words_to_ignore = list(map(lambda x:x.upper(), file.read().splitlines()))       # Read lines from text file and make uppercase
    file.close()                                                                    # Close the file

    words_to_ignore = list(dict.fromkeys(words_to_ignore))                          # Remove any duplicate words, if any
    
    return words_to_ignore                                                          # Return list of words to ignore



def get_market_holidays():
    us_holidays = UnitedStates(years=dt.datetime.now().date().year)                             # Get US Federal Holidays for the current year

    del us_holidays[dt.date(dt.datetime.now().date().year, 7, 4)]                               # Remove Independence Day (7/4)
    del us_holidays[dt.date(dt.datetime.now().date().year, 10, 14)]                             # Remove Columbus Day (10/11)
    del us_holidays[dt.date(dt.datetime.now().date().year, 11, 11)]                             # Remove Veteran's Day (11/11)
    del us_holidays[dt.date(dt.datetime.now().date().year, 12, 25)]                             # Remove Christmas Day (12/25)
    del us_holidays[dt.date(dt.datetime.now().date().year, 12, 31)]                             # Remove New Year's Eve (12/31)

    us_holidays[dt.date(dt.datetime.now().date().year, 4, 2)]   = "Good Friday"                 # Add Good Friday (4/2)
    us_holidays[dt.date(dt.datetime.now().date().year, 11, 26)] = "Day After Thanksgiving"      # Add Day after Thanksgiving (11/26)

    stock_market_holidays = dict()                                                              # Create empty dictionary for stock market holidays
    for key,value in us_holidays.items():                                                       # Iterate through all US holidays and add US stock market open and close times
        if key == dt.date(dt.datetime.now().date().year, 11, 26):                               # Early market close time for Day after Thanksgiving
            value_dict = {"Holiday Name" : value,
                          "Open Time"    : globals.MARKET_OPEN,
                          "Close Time"   : (dt.datetime.min + (dt.datetime.combine(dt.date.today(), globals.MARKET_CLOSE) -\
                                            dt.datetime.combine(dt.date.today(), dt.time(hour=3)))).time()}
    
        else:
            value_dict = {"Holiday Name" : value,                                               # No market open or close times for other US holidays
                          "Open Time"    : None,
                          "Close Time"   : None}
        
        stock_market_holidays[key] = value_dict                                                 # Add stock market holiday to dictionary

    return stock_market_holidays



def program_title():
    print("===========================================================================================")
    print("$ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $")
    print("===========================================================================================")
    print(                                                                                             )
    print(" /$$      /$$  /$$$$$$  /$$$$$$$                                                           ")
    print("| $$  /$ | $$ /$$__  $$| $$__  $$                                                          ")
    print("| $$ /$$$| $$| $$  \__/| $$  \ $$                                                          ")
    print("| $$/$$ $$ $$|  $$$$$$ | $$$$$$$                                                           ")
    print("| $$$$_  $$$$ \____  $$| $$__  $$                                                          ")
    print("| $$$/ \  $$$ /$$  \ $$| $$  \ $$                                                          ")
    print("| $$/   \  $$|  $$$$$$/| $$$$$$$/                                                          ")
    print("|__/     \__/ \______/ |_______/                                                           ")
    print("                                                                                           ")
    print("  /$$$$$$  /$$$$$$$$ /$$   /$$ /$$$$$$$$ /$$$$$$ /$$      /$$ /$$$$$$$$ /$$   /$$ /$$$$$$$$")
    print(" /$$__  $$| $$_____/| $$$ | $$|__  $$__/|_  $$_/| $$$    /$$$| $$_____/| $$$ | $$|__  $$__/")
    print("| $$  \__/| $$      | $$$$| $$   | $$     | $$  | $$$$  /$$$$| $$      | $$$$| $$   | $$   ")
    print("|  $$$$$$ | $$$$$   | $$ $$ $$   | $$     | $$  | $$ $$/$$ $$| $$$$$   | $$ $$ $$   | $$   ")
    print(" \____  $$| $$__/   | $$  $$$$   | $$     | $$  | $$  $$$| $$| $$__/   | $$  $$$$   | $$   ")
    print(" /$$  \ $$| $$      | $$\  $$$   | $$     | $$  | $$\  $ | $$| $$      | $$\  $$$   | $$   ")
    print("|  $$$$$$/| $$$$$$$$| $$ \  $$   | $$    /$$$$$$| $$ \/  | $$| $$$$$$$$| $$ \  $$   | $$   ")
    print(" \______/ |________/|__/  \__/   |__/   |______/|__/     |__/|________/|__/  \__/   |__/   ")
    print(                                                                                             )
    print("===========================================================================================")
    print("$ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $ $")
    print("===========================================================================================")



def is_market_holiday():
    if dt.date.today() in globals.HOLIDAYS.keys():  # Determine if today's date is a US stock market holiday
        if globals.HOLIDAY_DETERMINED:              # Quick return after determining if today's date is a US stock market holiday
            return globals.HOLIDAY_DETERMINED

        if not globals.HOLIDAY_DETERMINED:
            # If holiday is a market closure holiday
            if globals.HOLIDAYS[dt.date.today()]['Open Time'] is None and globals.HOLIDAYS[dt.date.today()]['Close Time'] is None:
                print(f">>> Market Closed today because of {globals.HOLIDAYS[dt.date.today()]['Holiday Name']}. . .")

            # Else if holiday is a early market closure holiday
            elif globals.HOLIDAYS[dt.date.today()]['Close Time'] != dt.datetime.strptime('01:00PM', '%I:%M%p').time():
                print(f">>> Market Closing Early today because of {globals.HOLIDAYS[dt.date.today()]['Holiday Name']}. . .")
                globals.MARKET_CLOSE = globals.HOLIDAYS[dt.date.today()]['Close Time']

            globals.HOLIDAY_DETERMINED = True

    else:                                           # Else today's date is not a US stock market holiday
        if not globals.HOLIDAY_DETERMINED:          # Quick return after determining if today's date is not a US stock market holiday
            return globals.HOLIDAY_DETERMINED

        # If market close time is not 1:00 PM, set it back to 1:00 PM
        if globals.MARKET_CLOSE != dt.datetime.strptime('01:00PM', '%I:%M%p').time():
            globals.MARKET_CLOSE = dt.datetime.strptime('01:00PM', '%I:%M%p').time()

        globals.HOLIDAY_DETERMINED = False
    
    return globals.HOLIDAY_DETERMINED                                               



def is_weekday():
    day_of_week = calendar.day_name[dt.date.today().weekday()]      # Return the day of week

    if (day_of_week == 'Saturday') or (day_of_week == 'Sunday'):    # Weekend
        return (False, day_of_week)
    else:                                                           # Weekday
        return (True, day_of_week)



def is_network_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))       # Attempt to create socket connection
        return True                                     # Return True if successful connection attempt

    except OSError:
        return False                                    # Return False if unsuccessful connection attempt

    except Exception:                                   # Return False if unknown exception occured
        logging.error(f"*** Unexpected Exception Occured! ***", exc_info=True)
        return False 



def write_df_to_excel(df, file_name):
    dir_path = get_dir_path()

    # Create sentiment dir if it doesnt exists (Don't create dir for EMA excel file)
    if not os.path.exists(dir_path) and ("ema" not in file_name):
        print(f">>> Creating wsb_sentiment directory. . .")
        os.makedirs(dir_path)

    # If previous wsb_comments already exist in sentiment dir and new wsb_comments are being written to excel file
    elif os.path.exists(f'{dir_path}/{file_name}.xlsx') and ("comments" in file_name):
        # Read old wsb_comments excel file
        comments_df = pd.read_excel(f'{dir_path}/{file_name}.xlsx', index_col=0, engine='openpyxl')
        
        # Append new comments df to old comments df
        comments_df = comments_df.append(df, ignore_index=True)
        
        # Set new df to write to excel file
        df = comments_df

    print(f'>>> Writing excel file {file_name}. . . ')
    if "ema" not in file_name:                      # Write sentiment comments and individual ticker sentiment to excel sheet
        df.to_excel(f'{dir_path}/{file_name}.xlsx')
    else:                                           # Write sentiment EMA data to excel sheet
        df.to_excel(f'Data/{file_name}.xlsx')

    return df



def get_dir_path(prev_day=False):
    day_of_week = is_weekday()[1]                           # Determine day of week

    if day_of_week == 'Monday':
        if prev_day:                                        # If data from previous market day is requested, return directory for (Thursday)_(Friday) of previous week
            return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=4)).strftime("%Y-%m-%d")}_{(dt.date.today()-dt.timedelta(days=3)).strftime("%Y-%m-%d")}'
        
        else:
            if dt.datetime.now().time() >= globals.MARKET_CLOSE and not globals.IS_MARKET_OPEN:    # If stock market is closed for the day, return directory for (Monday)_(Tuesday) of current week
                return f'Data/wsb_sentiment_{dt.date.today().strftime("%Y-%m-%d")}_{(dt.date.today()+dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

            else:                                           # If stock market is closed (pre-market) or market is open, return directory for (Friday)_(Monday) of current week
                return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=3)).strftime("%Y-%m-%d")}_{dt.date.today().strftime("%Y-%m-%d")}'


    elif day_of_week == 'Tuesday':
        if prev_day:                                        # If data from previous market day is requested, return directory for (Friday)_(Monday) of current week
            return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=4)).strftime("%Y-%m-%d")}_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

        else:
            if dt.datetime.now().time() >= globals.MARKET_CLOSE and not globals.IS_MARKET_OPEN:    # If stock market is closed for the day, return directory for (Tuesday)_(Wednesday) of current week
                return f'Data/wsb_sentiment_{dt.date.today().strftime("%Y-%m-%d")}_{(dt.date.today()+dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

            else:                                           # If stock market is closed (pre-market) or market is open, return directory for (Monday)_(Tuesday) of current week
                return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}_{dt.date.today().strftime("%Y-%m-%d")}'


    elif day_of_week == 'Wednesday':
        if prev_day:                                        # If data from previous market day is requested, return directory for (Monday)_(Tuesday) of current week
            return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=2)).strftime("%Y-%m-%d")}_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

        else:
            if dt.datetime.now().time() >= globals.MARKET_CLOSE and not globals.IS_MARKET_OPEN:    # If stock market is closed for the day, return directory for (Wednesday)_(Thursday) of current week
                return f'Data/wsb_sentiment_{dt.date.today().strftime("%Y-%m-%d")}_{(dt.date.today()+dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

            else:                                           # If stock market is closed (pre-market) or market is open, return directory for (Tuesday)_(Wednesday) of current week
                return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}_{dt.date.today().strftime("%Y-%m-%d")}'


    elif day_of_week == 'Thursday':
        if prev_day:                                        # If data from previous market day is requested, return directory for (Tuesday)_(Wednesday) of current week
            return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=2)).strftime("%Y-%m-%d")}_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

        else:
            if dt.datetime.now().time() >= globals.MARKET_CLOSE and not globals.IS_MARKET_OPEN:    # If stock market is closed for the day, return directory for (Thursday)_(Friday) of current week
                return f'Data/wsb_sentiment_{dt.date.today().strftime("%Y-%m-%d")}_{(dt.date.today()+dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

            else:                                           # If stock market is closed (pre-market) or market is open, return directory for (Wednesday)_(Thursday) of current week
                return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}_{dt.date.today().strftime("%Y-%m-%d")}'


    elif day_of_week == 'Friday':                           
        if prev_day:                                        # If data from previous market day is requested, return directory for (Wednesday)_(Thursday) of current week
            return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=2)).strftime("%Y-%m-%d")}_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}'

        else:
            if dt.datetime.now().time() >= globals.MARKET_CLOSE and not globals.IS_MARKET_OPEN:    # If stock market is closed for the day, return directory for (Friday)_(Monday) of next week
                return f'Data/wsb_sentiment_{dt.date.today().strftime("%Y-%m-%d")}_{(dt.date.today()+dt.timedelta(days=3)).strftime("%Y-%m-%d")}'

            else:                                           # If stock market is closed (pre-market) or market is open, return directory for (Thursday)_(Friday) of current week
                return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}_{dt.date.today().strftime("%Y-%m-%d")}'


    elif day_of_week == 'Saturday':                         # If Weekend (Saturday), return directory for (Friday)_(Monday) of next week
        return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=1)).strftime("%Y-%m-%d")}_{(dt.date.today()+dt.timedelta(days=2)).strftime("%Y-%m-%d")}'


    elif day_of_week == 'Sunday':                           # If Weekend (Sunday), return directory for (Friday)_(Monday) of next week
        return f'Data/wsb_sentiment_{(dt.date.today()-dt.timedelta(days=2)).strftime("%Y-%m-%d")}_{(dt.date.today()+dt.timedelta(days=1)).strftime("%Y-%m-%d")}'


    else:                                                   # If some error occured, return "NA_NA_NA" directory value
        print("*** get_dir_path() ERROR: Unknown error occured!. . .")
        return "NA_NA_NA"


# Create program logger for errors and exceptions
logging.basicConfig(filename=f'Error_Logs/WSB_Sentiment_Run_Log_{dt.datetime.today().date()}.log',     # Log file name
                    filemode='w',                                                                      # Write to log file
                    format="\n%(asctime)s | %(levelname)s | %(funcName)s() | %(message)s")             # Log file output format
logging.getLogger('').addHandler(logging.StreamHandler(sys.stdout))                                    # Show log output in console window
