"""
WSB_Sentiment.py
-----------------
Contains class functions for processing WSB comment sentiment and analysis.

"""

import urllib3
import globals
from imports import *
from helper import *



class WSB_Sentiment():
    def __init__(self, **kwargs):
        self.wsb_thread = None                                                                  # Initialize WSB Sentiment thread       
        self.driver = None                                                                      # Initialize chrome webdriver to None
        self.wsb_sentiment_df = pd.DataFrame(columns=['Time', 'Sentiment', 'Ticker', 'Text'])   # This dataframe contains all sentiment comments from WSB
        self.wsb_status_update_df = pd.DataFrame()                                              # This dataframe contains stock tickers for the WSB status report
        self.ticker_sentiment_df = pd.DataFrame()                                               # This dataframe contains all stock ticker sentiment
        self.top_ticker_sentiment_df = pd.DataFrame()                                           # This dataframe contains top stock ticker sentiment
        self.ema_df = pd.DataFrame()                                                            # Exponential Moving Average dataframe
        self.overall_sentiment = 1.0                                                            # Initialize bull/bear ratio (overall market sentiment)
        self.update_hour = kwargs.get('update_hour')                                            # Initialize WSB sentiment update hour
        if self.update_hour is None:
            self.update_hour = 1                                                                # Default setiment update hour to 1 if not set from kwargs



    def run(self):
        self.wsb_thread = threading.Thread(name="WSBSentimentThread",                           # Create WSB thread to collect sentiment comments
                                      target=self.get_wsb_comments)
        self.wsb_thread.setDaemon(True)                                                         # Set WSB thread to be background task
        self.wsb_thread.start()                                                                 # Start WSB thread (Begin collecting sentiment comments in the background)



    def setup_driver(self):

        print(">>> Setting Up Chrome Webdriver. . .")

        # Create Chrome webdriver options
        options = webdriver.ChromeOptions()                                                     # Create webdriver instance
        options.add_argument('--headless')                                                      # Make windowless browser
        options.headless = True                                                                 # Prevents chrome window from opening
        options.add_experimental_option("excludeSwitches", ["enable-logging"])                  # Prevents chrome webdriver logging
        options.binary_location="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"   # Specify chrome webdriver executable location (Dont know if we need this)

        # Create Chrome webdriver using webdriver options
        try:
            self.driver = webdriver.Chrome(executable_path="C:\Program Files (x86)\Google\chromedriver_win32\chromedriver.exe", options=options)
            self.driver.delete_all_cookies()             # Delete all cookies (Dont know if we really need to do this)
            self.driver.get(globals.URL)                 # Open the WSB AI using the site URL
            return
        
        # If driver cannot connect to URL, return "None" value
        except WebDriverException:
            logging.error(f"*** WebDriverException: Could not reach URL {globals.URL}. . .")
            self.driver = None
            return

        # If unknown exception occured, return "None" value
        except Exception:
            logging.error(f"*** Unexpected Exception Occured! ***", exc_info=True)
            self.driver = None
            return



    def shutdown_driver(self):
        if self.driver is not None:                             # If driver is still active, shutdown driver
            print('>>> Shutting Down Chrome Webdriver . . .')
            self.driver.quit()                                  # Shut down chrome webdriver
            self.driver = None                                  # Set driver to "None" value

        return



    def get_wsb_comments(self):

        self.setup_driver()                                                     # Setup Chrome Webdriver

        retry_count = 0                                                         # Initialize reconnection attempts counter if webdriver or socket interrupts occur
        previous_time = dt.datetime.now()                                       # Initialize current time for WSB sentiment status updates
        prev_comments = self.driver.find_element_by_id("comment-area").text     # Initialize current comments collected from WSB

        print(">>> Collecting WSB Sentiment Comments. . .")

        with globals.WSB_SPINNER as spinner:                                                # Create progress spinner for sentiment loop
            while True:                                                                     # Loop forever on daemon thread. . .
                try:
                    # /// Network connection handling
                    if retry_count > 0 and is_network_connected():                          # If network connection is re-established after being disconnected
                        with spinner.hidden():
                            print(">>> Network Connection Established. . .")
                            retry_count = 0                                                 # Reset the reconnection attempts counter

                            if self.driver is None:                                         # Setup webdriver if driver was not established
                                self.setup_driver()                                                   

                    elif not is_network_connected():                                        # If network connection is disconnected after being established
                        with spinner.hidden():
                            print(">>> Network Disconnected. . .")
                            self.shutdown_driver()                                          # Shutdown the webdriver

                    # /// Sentiment message processing
                    recent_comments = self.driver.find_element_by_id("comment-area").text   # Get new WSB comments from "comment-area" section of webpage

                    old_comments = prev_comments.splitlines()                               # Split text from old comments
                    new_comments = recent_comments.splitlines()                             # Split text from new comments

                    # Get new "Bullish", "Bearish", and "None" sentiment type comments, if any
                    updated_comments = [comment for comment in new_comments if comment not in set(old_comments)]
                    
                    if not updated_comments:                                                # If no new comments have been collected, 
                        continue                                                            # return to the beginning of while loop

                    prev_comments = recent_comments                                         # Update previous comments collected with most recent comments collected

                    # Find all indexes of "bullish", "bearish", and "none" comments
                    idx_list = [idx for idx, comment in enumerate(updated_comments) if ("bullish" in comment) or ("bearish" in comment) or ("none" in comment)]

                    # Merge comments initially separated by "\n" into one comment and ignore all "none" sentiment type comments
                    updated_comments = [" ".join(updated_comments[idx_list[i]:idx_list[i+1]]) if (i < len(idx_list)-1) and (idx_list[i+1]-idx_list[i] > 1) \
                                        else updated_comments[idx_list[i]] for i in range(len(idx_list)) if not("none" in updated_comments[idx_list[i]])]

                    if not updated_comments:                                                # If no new "bullish" or "bearish" comments have been collected (only "none" comments)
                        continue                                                            # have been collected), return to the beginning of while loop  
                        
                    for comment in updated_comments:                                        # Iterate through all new comments collected
                        strn = comment.split(' ', 3)
                        
                        if len(strn) < 4:                                                   # Skip new comment if not in the correct format 
                            continue                                                        # (sentiment / time / author / text)

                        sentiment, time_stamp, author, text = strn[0], strn[1], strn[2], strn[3]    # Get sentiment / time stamp / author / comment text
                        mentioned_tickers = self.find_mentioned_tickers(text)                       # Find any tickers mentioned in comment text        
                            
                        # If no tickers are mentioned in WSB comment, set "Ticker" to "None" value and append row to Sentiment Dataframe
                        if not mentioned_tickers:
                            df_row = {  'Time'        : time_stamp[1:-1],
                                        'Sentiment'   : sentiment,
                                        'Ticker'      : None,
                                        'Text'        : text}
                            
                            self.wsb_sentiment_df = self.wsb_sentiment_df.append(df_row, ignore_index=True)
                        
                        # Else if there are tickers mentioned in WSB comment
                        else:
                            # Iterate through each mentioned ticker and append row to Sentiment Dataframe
                            for ticker in mentioned_tickers:
                                df_row = {  'Time'        : time_stamp[1:-1],
                                            'Sentiment'   : sentiment,
                                            'Ticker'      : ticker,
                                            'Text'        : text}
                            
                                self.wsb_sentiment_df = self.wsb_sentiment_df.append(df_row, ignore_index=True)

                        spinner.text = f"Mentioned Tickers: {mentioned_tickers}"                    # Show mentioned tickers in spinner text for visual confirmation
                    
                    # Provide sentiment update every (n) hour increments [(# of hours to wait) * (# of sec in an hour)]
                    if (dt.datetime.now() - previous_time).total_seconds() >= (self.update_hour * 3600):    
                        self.sentiment_analysis()                                                           
                        previous_time = dt.datetime.now()                                           # Update current time for WSB sentiment status updates


                # /// WiFi Connection Issues
                except AttributeError:
                    with spinner.hidden():                                                      
                        logging.warning("*** AttributeError: Could Not Access Sentiment Data. . .")
                        retry_count += 1                                                            # If AttributeError raised (internet connection issue), increment retry count
                        
                        # If connection retry counter < max number of connection retries allowed
                        if retry_count <= globals.MAX_RETRIES:                                      
                            print(f">>> Connection retry attempt {retry_count}/{globals.MAX_RETRIES}. . . ")
                            time.sleep(5.0)                                                         # Wait 5 seconds before trying again
                            continue                                                                # Return to beginning of While Loop

                        # WiFi re-connectivity failed
                        else:                                                                   
                            print('>>> Max connection retry attempts reached. . . Exiting WSB Sentiment Program')
                            break

                # /// Keyboard Shutdown Enabled
                except (urllib3.exceptions.ProtocolError, urllib3.exceptions.NewConnectionError, KeyboardInterrupt):
                    with spinner.hidden():
                        logging.warning("*** ProtocolError/NewConnectionError/KeyboardInterrupt: Exiting WSB Sentiment loop. . .")

                        # Write any collected WSB sentiment comments to excel file before exiting
                        if not self.wsb_sentiment_df.empty:
                            write_df_to_excel(self.wsb_sentiment_df, "wsb_comments")

                        break

                # /// Unknown Exception Handling
                except Exception:   
                    with spinner.hidden():                                                      
                        logging.error(f"*** Unexpected Exception Occured! (WSB Loop)***", exc_info=True)
                        break

            # If still active, shutdown driver
            with spinner.hidden():
                self.shutdown_driver()

        return



    def find_mentioned_tickers(self, text):
        # Determine if any tickers are mentioned in the comment text by finding any words that are uppercase
        # (Although not always the case, stock ticker symbols are usually written in uppercase)
        potential_ticker_list = [list(word) for upper, word in itertools.groupby(text.split(), key=str.isupper) if upper]   # Returns a list of lists w/ potential ticker mentions
        potential_ticker_list = [item for sublist in potential_ticker_list for item in sublist]                             # Converts list of lists to single list of potential tickers

        # Remove all special characters and punctuations that may be attached to potential tickers (Only keep letters and numbers)
        potential_ticker_list = [re.sub('[^a-zA-Z0-9]+','', ticker) for ticker in potential_ticker_list]

        # Check if potential tickers are valid tickers
        mentioned_tickers = [ticker for ticker in potential_ticker_list if ((ticker in globals.TICKER_DICT['Symbol'].values()) or \
                                                                            (ticker in globals.ETFS_LIST)) and (ticker not in globals.WORDS_TO_IGNORE)]

        # Remove duplicates of same ticker (ex. [TSLA, TSLA, TSLA, AAPL] --> [TSLA, AAPL])
        mentioned_tickers = list(dict.fromkeys(mentioned_tickers))

        return mentioned_tickers



    def sentiment_analysis(self):
        try:
            if self.wsb_sentiment_df.empty:     # If WSB sentiment dataframe is empty (no WSB comments were collected)
                print(">>> No WSB sentiment comments found!. . . No analysis to be done. . .")
                return                          # Exit function

            # Only keep bullish/bearish and possible bullish/bearish comments ((bullish)/(bearish)) (Remove potential garbage from dataframe)
            self.wsb_sentiment_df = self.wsb_sentiment_df[self.wsb_sentiment_df['Sentiment'].isin(['bullish', '(bullish)', 'bearish', '(bearish)'])].reset_index(drop=True)

            self.wsb_sentiment_df = write_df_to_excel(self.wsb_sentiment_df, "wsb_comments")          # Write WSB sentiment comments to excel file

            print(">>>")
            print(">>> ===========================================================")
            print(">>> $ $ $    W S B    S E N T I M E N T    S T A T U S    $ $ $")
            print(">>> ===========================================================")
            print(">>>")

            print(f">>> DATE / TIME OF REPORT: {dt.date.today().strftime('%Y-%m-%d')} \t {dt.datetime.now().time()}")

            # Count all occurrences of bullish / possible bullish sentiment and bearish / possible bearish sentiment
            value_counts = self.wsb_sentiment_df['Sentiment'].value_counts()

            # Get bullish and potential bullish sentiment count
            if ('bullish' in value_counts) or ('(bullish)' in value_counts):
                if 'bullish' not in value_counts:
                    bull_count = value_counts['(bullish)']
                elif '(bullish)' not in value_counts:
                    bull_count = value_counts['bullish']
                else:
                    bull_count = value_counts['bullish'] + value_counts['(bullish)']
            else:
                bull_count = 0
            
            # Get bearish and potential bearish sentiment count
            if ('bearish' in value_counts) or ('(bearish)' in value_counts):
                if 'bearish' not in value_counts:
                    bear_count = value_counts['(bearish)']
                elif '(bearish)' not in value_counts:
                    bear_count = value_counts['bearish']
                else:
                    bear_count = value_counts['bearish'] + value_counts['(bearish)']
            else:
                bear_count = 0

            if bear_count == 0:                                                                     # This ensures no divide by zero error when calculating 
                bear_count = 1                                                                      # bull/bear ratio

            self.overall_sentiment = bull_count/bear_count

            print(f">>> OVERALL WSB SENTIMENT SCORE (BULL / BEAR RATIO): {self.overall_sentiment}") 
            print(">>>")

            mentioned_tickers = self.wsb_sentiment_df['Ticker'].unique().tolist()                   # Collect all tickers mentioned in WSB dataframe
            mentioned_tickers = list(filter(None, mentioned_tickers))                               # Remove any "None" type values from list

            ticker_sentiment_rows_list = list()                                                     # Create list to hold dataframe rows that will obtain ticker sentiment data
            for ticker in mentioned_tickers:                                                        # Iterate through all mentioned tickers
                ticker_df = self.wsb_sentiment_df[self.wsb_sentiment_df['Ticker'].isin([ticker])]   # Create separate dataframe for specific ticker

                # Count all occurrences of bullish / possible bullish sentiment and bearish / possible bearish sentiment for ticker
                ticker_value_counts = ticker_df['Sentiment'].value_counts()
                
                # Get bullish and potential bullish sentiment count
                if ('bullish' in ticker_value_counts) or ('(bullish)' in ticker_value_counts):
                    if 'bullish' not in ticker_value_counts:
                        ticker_bull_count = ticker_value_counts['(bullish)']
                    elif '(bullish)' not in ticker_value_counts:
                        ticker_bull_count = ticker_value_counts['bullish']
                    else:
                        ticker_bull_count = ticker_value_counts['bullish'] + ticker_value_counts['(bullish)']
                else:
                    ticker_bull_count = 0
                
                # Get bearish and potential bearish sentiment count
                if ('bearish' in ticker_value_counts) or ('(bearish)' in ticker_value_counts):
                    if 'bearish' not in ticker_value_counts:
                        ticker_bear_count = ticker_value_counts['(bearish)']
                    elif '(bearish)' not in ticker_value_counts:
                        ticker_bear_count = ticker_value_counts['bearish']
                    else:
                        ticker_bear_count = ticker_value_counts['bearish'] + ticker_value_counts['(bearish)']
                else:
                    ticker_bear_count = 0

                if ticker_bear_count == 0:                                                          # This ensures no divide by zero error when calculating 
                    ticker_bear_count = 1                                                           # bull/bear ratio

                # Create dataframe row w/ specific ticker data
                ticker_sentiment_row = {'Ticker'            : ticker, 
                                        'Bullish Count'     : ticker_bull_count, 
                                        'Bearish Count'     : ticker_bear_count, 
                                        'Bull/Bear Ratio'   : ticker_bull_count/ticker_bear_count}

                ticker_sentiment_rows_list.append(ticker_sentiment_row)                                  # Append list containing sentiment data for specific ticker
                
            # Append rows to ticker sentiment dataframe
            self.ticker_sentiment_df = self.ticker_sentiment_df.append(ticker_sentiment_rows_list, ignore_index=True)

            # Sort ticker sentiment dataframe from largest to smallest Bullish and Bearish count
            self.ticker_sentiment_df.sort_values(by=['Bullish Count', 'Bearish Count'], ascending=False, inplace=True)  
            self.ticker_sentiment_df.set_index('Ticker', inplace=True)                              # Set dataframe indexes to be stock ticker symbols
                      
            write_df_to_excel(self.ticker_sentiment_df, "ticker_sentiment_all")                     # Write all ticker sentiment dataframe to excel file

            ticker_report_df = self.ticker_sentiment_df[:10]                                        # Only show top 10 Bullish/Bearish tickers for WSB status update

            bull_bear_ratio_percent_change = "N/A"                                                  # Initialize bull/bear ratio percent change to N/A
            for ticker in ticker_report_df.index:                                                   # Iterate through each top 10 Bullish/Bearish tickers

                # If the WSB status update dataframe is not empty (contains ticker data) and the current ticker is found in the dataframe and the Bull/Bear Ratio of the ticker
                # in the WSB status update dataframe is not zero (prevent divide by zero error), calculate a percent change between the ticker's current and previous 
                # bull/bear ratio values
                if (not self.wsb_status_update_df.empty) and (ticker in self.wsb_status_update_df.index) and (self.wsb_status_update_df.loc[ticker, "Bull/Bear Ratio"] != 0):
                    bull_bear_ratio_percent_change = str(round(((ticker_report_df.loc[ticker, "Bull/Bear Ratio"] - self.wsb_status_update_df.loc[ticker, "Bull/Bear Ratio"])\
                                                        / self.wsb_status_update_df.loc[ticker, "Bull/Bear Ratio"]) * 100, 2))

                # Print information for each ticker
                print(">>> TICKER: %-8s BULL COUNT: %-8d BEAR COUNT: %-8d BULL/BEAR RATIO: %-8.2f RATIO %% CHANGE: %-8s" % (ticker,
                                                                                                                            ticker_report_df.loc[ticker, "Bullish Count"],
                                                                                                                            ticker_report_df.loc[ticker, "Bearish Count"],
                                                                                                                            ticker_report_df.loc[ticker, "Bull/Bear Ratio"],
                                                                                                                            bull_bear_ratio_percent_change))

            print(">>>")
            self.wsb_status_update_df = ticker_report_df                                        # Update WSB status update dataframe
            return 

        except KeyError:
            logging.warning("*** KeyError: DataFrame Key Not Found. . .", exc_info=True)        # If dataframe Key Error Exception occured,
            print(">>> Unable to provide WSB sentiment analysis!. . . ")
            self.overall_sentiment = 1.0
            return                                                                             

        except Exception:
            logging.error(f"*** Unexpected Exception Occured! ***", exc_info=True)              # If an Unknown Exception occured,
            print(">>> Unable to provide WSB sentiment analysis!. . . ")
            self.overall_sentiment = 1.0
            return                                                                                     



    def get_top_tickers(self):
        print(">>> Collecting top tickers. . .")
        try:
            # Get all ticker sentiment data from excel file
            self.top_ticker_sentiment_df = pd.read_excel(f'{get_dir_path()}/ticker_sentiment_all.xlsx', index_col=0, engine='openpyxl')

            # If overall sentiment is bullish, get all bullish tickers
            if self.overall_sentiment > 1.0:
                # Find tickers with a bull/bear ratio > 1.0
                self.top_ticker_sentiment_df = self.top_ticker_sentiment_df[self.top_ticker_sentiment_df['Bull/Bear Ratio'] > 1.0]  # Overwrite ticker dataframe with only bullish tickers
                                                                                                                                    # (Bull/Bear Ratio already sorted from sentiment_analysis() function)
            
            # If overall sentiment is bearish, get all bearish tickers
            elif self.overall_sentiment < 1.0:
                self.top_ticker_sentiment_df = self.top_ticker_sentiment_df[self.top_ticker_sentiment_df['Bull/Bear Ratio'] < 1.0]  # Overwrite ticker dataframe with only bearish tickers
                self.top_ticker_sentiment_df.sort_values(by=['Bull/Bear Ratio'], ascending=True, inplace=True)                      # Sort Bull/Bear Ratio from smallest to largest
                
            self.top_ticker_sentiment_df = self.top_ticker_sentiment_df[:25]    # Collect only the top 25 bullish/bearish tickers

            self.get_previous_sentiment_percent_chng()                          # Calculate previous day's sentiment percent change for top
                                                                                # 25 bullish/bearish tickers

            # Get open price for top 25 bullish/bearish tickers
            with globals.WSB_SPINNER as spinner:                   # Create progress spinner for sentiment loop
                open_price_list = list()                                                    # Initialize list for Open price of stock tickers
                for ticker in self.top_ticker_sentiment_df.index:                           # Iterate through all tickers
                    try:
                        spinner.text = f'Collecting Open Price for. . . {ticker}'
                        open_price_list.append(yf.Ticker(ticker).info['open'])
                    
                    except IndexError:                                                      # If unable to obtain open price via first method, try second method
                        with spinner.hidden():
                            print(f">>> Unable to collect open price for {ticker}. . . Trying alternative method. . .")
                            try:
                                open_price_list.append(yf.Ticker(ticker).history(period="1d").iloc[0]['Open'])

                            except Exception:                                                  # If unable to obtain open price via second method, insert "None" value
                                logging.error(f">>> Failed to collect open price for {ticker}. . .", exc_info=True)
                                open_price_list.append(None)

            
            self.top_ticker_sentiment_df['Open'] = open_price_list                          # Add stock ticker's Open price to top tickers dataframe

            write_df_to_excel(self.top_ticker_sentiment_df, 'ticker_sentiment_top25')

            return 

        except FileNotFoundError:       # If excel file w/ individual ticker sentiment is not found, exit from function
            logging.warning(f"*** FileNotFoundError: Excel file '{get_dir_path()}/ticker_sentiment_all' not found. . .")
            return
        
        except Exception:               # If an Unknown Exception occured, exit from function
            logging.error("*** Unexpected Exception Occured! ***", exc_info=True)    
            return  



    def get_previous_sentiment_percent_chng(self):
        print(">>> Collecting percent change of previous day sentiment. . .")
        dir_path = get_dir_path(prev_day=True)          # Get directory path for previous market day data

        try:
            yesterdays_ticker_sentiment_df = pd.read_excel(f'{dir_path}/ticker_sentiment_top25.xlsx', index_col=0, engine='openpyxl')

            # Iterate through all tickers from today's top 25 ticker sentiment
            for ticker in self.top_ticker_sentiment_df.index:
                # If ticker found in yesterday's top 25 ticker sentiment, calculate sentiment percent change for ticker
                if ticker in yesterdays_ticker_sentiment_df.index:
                    self.top_ticker_sentiment_df.loc[ticker, 'Sentiment Percent Change'] = ((self.top_ticker_sentiment_df.loc[ticker, 'Bull/Bear Ratio'] - yesterdays_ticker_sentiment_df.loc[ticker, 'Bull/Bear Ratio'])\
                                                                                            / yesterdays_ticker_sentiment_df.loc[ticker, 'Bull/Bear Ratio']) * 100

            return
        
        except FileNotFoundError:       # If excel file w/ top 25 individual ticker sentiment data is not found, exit from function
            logging.warning(f"*** FileNotFoundError: Excel file '{dir_path}/ticker_sentiment_top25' not found. . .")
            return

        except Exception:               # If an Unknown Exception occured, exit from function
            logging.error("*** Unexpected Exception Occured! ***", exc_info=True)    
            return   



    def calc_ema(self, period=10):
        # If previous EMA data exists, read EMA excel file
        if os.path.exists(f'Data/{period}_day_ema".xlsx'):
            self.ema_df = pd.read_excel(f'Data/{period}_day_ema".xlsx', index_col=0, engine='openpyxl')
        
            # If 10-day EMA for today's date already exists in dataframe, return 10-day EMA value
            if dt.date.today().strftime("%Y_%m_%d") in self.ema_df['Date']:
                return self.ema_df["10-day EMA"][self.ema_df['Date'] == dt.date.today().strftime("%Y_%m_%d")].values

        # Add today's date and bull/bear ratio to dataframe
        self.ema_df = self.ema_df.append({"Date": dt.date.today().strftime("%Y_%m_%d"), "Bull/Bear Ratio": self.overall_sentiment}, ignore_index=True)

        # Calculate 10 day EMA for all bull/bear ratio entries in dataframe
        self.ema_df['10-day EMA'] = self.ema_df['Bull/Bear Ratio'].ewm(span=period, adjust=False).mean()

        # Write EMA data to excel file
        write_df_to_excel(self.ema_df, f"{period}_day_ema")

        # Return 10-day EMA for today's date
        return self.ema_df["10-day EMA"][self.ema_df['Date'] == dt.date.today().strftime("%Y_%m_%d")].values



    def get_close_price_and_percent_chng(self):
        print(">>> Collecting Close Price. . .")
        try:
            # Write close price for top 10 bullish/bearish tickers to dataframe
            #self.top_ticker_sentiment_df['Close'] = [yf.Ticker(ticker).history(period="1d").iloc[0]['Close'] for ticker in self.top_ticker_sentiment_df.index\
            #                                                                                                    if self.top_ticker_sentiment_df.loc[ticker, "Open"] is not None]

            # Write percent change between open and close prices for top 25 bullish/bearish tickers to dataframe
            for ticker in self.top_ticker_sentiment_df.index:
                if self.top_ticker_sentiment_df.loc[ticker, 'Open'] is not None:
                    self.top_ticker_sentiment_df.loc[ticker, 'Close'] = yf.Ticker(ticker).history(period="1d").iloc[0]['Close'] 
                    self.top_ticker_sentiment_df.loc[ticker, "Price Percent Change"] = ((self.top_ticker_sentiment_df.loc[ticker, 'Close'] - self.top_ticker_sentiment_df.loc[ticker, 'Open'])\
                                                                                        / self.top_ticker_sentiment_df.loc[ticker, 'Open']) * 100
                else:
                    self.top_ticker_sentiment_df.loc[ticker, "Close"] = None
                    self.top_ticker_sentiment_df.loc[ticker, "Price Percent Change"] = None

            # self.top_ticker_sentiment_df['Price Percent Change'] = ((self.top_ticker_sentiment_df['Close'] - self.top_ticker_sentiment_df['Open'])\
            #                                                         / self.top_ticker_sentiment_df['Open']) * 100

            # Write ticker sentiment dataframe to excel file (this should overwrite previous ticker_sentiment excel sheet)
            write_df_to_excel(self.top_ticker_sentiment_df, "ticker_sentiment_top25")

            return

        except TypeError:       
            logging.warning("*** TypeError: Empty DataFrame. . .")                      # If top 25 ticker sentiment dataframe is empty, exit function
            return

        except Exception:       
            logging.error(f"*** Unexpected Exception Occured! ***", exc_info=True)      # If Unknown Exception occured, return exit function
            return  



    def determine_potential_profits(self):
        print(">>> Writing Potential Profit/Loss Report. . .")

        # Create watchlist report file
        file = open(f'{get_dir_path()}/potential_profit_loss_report.txt', 'w')

        file.write("====================================================================\n")
        file.write("                       PROFIT / LOSS REPORT                         \n")
        file.write("====================================================================\n")

        # Write total cost to own 100 shares of each stock at Market Open price
        file.write('\n')
        file.write(">>> Cost for 100 shares at Market Open\n")
        total_cost = 0
        for ticker in self.top_ticker_sentiment_df.index:
            file.write("Ticker: %-8s | Open Price Cost (USD): $%-8.2f" % (ticker, self.top_ticker_sentiment_df.loc[ticker, "Open"] * 100))
            total_cost += round(self.top_ticker_sentiment_df.loc[ticker, "Open"] * 100, 2)
        file.write(f"Total Cost (USD): ${total_cost}")
        
        # Write total value/worth of 100 shares of each stock at Market Close price
        file.write('\n')
        file.write(">>> Value of 100 shares at Market Close\n")
        total_value = 0
        for ticker in self.top_ticker_sentiment_df.index:
            file.write("Ticker: %-8s | Close Price Value (USD): $%-8.2f" % (ticker, self.top_ticker_sentiment_df.loc[ticker, "Close"] * 100))
            total_value += round(self.top_ticker_sentiment_df.loc[ticker, "Close"] * 100, 2)
        file.write(f"Total Value (USD): ${total_value}")

        # Write daily profit/loss made from each stock
        file.write('\n')
        file.write(">>> Daily Profit/Loss from each stock ticker\n")
        for ticker in self.top_ticker_sentiment_df.index:
            file.write("Ticker: %-8s | Profit/Loss (USD): $%-8.2f" % (ticker, ((self.top_ticker_sentiment_df.loc[ticker, "Close"] * 100) - \
                                                                                (self.top_ticker_sentiment_df.loc[ticker, "Open"] * 100))))

        # Write total daily profit/loss
        file.write('\n')
        file.write(f">>> Total Daily Profit/Loss (USD): ${total_value - total_cost}\n")        

        # Close the file after writing
        file.close()    
        
        return



    def get_wsb_thread(self):
        return self.wsb_thread                  # Return WSB sentiment daemon thread



    def get_wsb_sentiment_df(self):
        return self.wsb_sentiment_df            # Return dataframe containing all WSB sentiment comments



    def get_all_ticker_sentiment_df(self):
        return self.ticker_sentiment_df         # Return dataframe containing the sentiment of all collected tickers from WSB comments



    def get_top_ticker_sentiment_df(self):
        return self.top_ticker_sentiment_df     # Return dataframe containing the sentiment of the 25 top mentioned tickers from WSB comments



    def get_ema_df(self):
        return self.ema_df                      # Return dataframe containing EMA data



    def get_overall_sentiment(self):
        return self.overall_sentiment           # Return overall bull/bear ratio sentiment score


    