"""
Short_Squeeze.py
--------------------
Contains class functions for determining if any mentioned WSB tickers are
experiencing a "Short Squeeze".

"""

import globals
from imports import *
from helper import *


class Short_Squeeze():
    def __init__(self):
        self.short_squeeze_df = pd.DataFrame()      # This dataframe contains all data needed to determine if a stock is experiencing a short squeeze


    def analyze_tickers(self):
        dir_path = get_dir_path()
        try:
            # Get top 25 ticker sentiment data from excel sheet
            wsb_tickers_df = pd.read_excel(f'{dir_path}/ticker_sentiment_top25.xlsx', index_col=0, engine='openpyxl')

            print(f">>> Collecting Short Squeeze data for {len(wsb_tickers_df)} Stock Tickers. . .")

            # Create threadpool process for collecting stock data
            with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
                future_to_tickers = {executor.submit(self.get_ticker_data, ticker) : ticker for ticker in wsb_tickers_df.index \
                                                                                                if ticker in globals.TICKER_DICT['Symbol'].values()}

                # Create progress bar
                with alive_bar(len(wsb_tickers_df.index), spinner="classic", bar="smooth") as bar:

                    # Iterate through every completed threadpool process
                    for df_row in concurrent.futures.as_completed(future_to_tickers):

                        # Update progress bar text
                        bar.text(f">>> Processing {df_row.result()['Ticker']}. . .")

                        # If percent change is greater than 5% or positive percent change and upward trend, add to watchlist dataframe
                        if df_row.result()['Percent Change'] >= 5 or (df_row.result()['Percent Change'] > 0 and self.is_price_uptrend(df_row.result()['Ticker'])):
                            self.short_squeeze_df = self.short_squeeze_df.append(df_row.result(), ignore_index=True)

                        # Iterate progress bar
                        bar()   

            # If short squeeze dataframe is not empty, set dataframe index to be ticker symbols
            if not self.short_squeeze_df.empty:
                self.short_squeeze_df.set_index('Ticker', inplace=True)

                self.check_watchlist()              # Determine if any stocks in the watchlist are experiencing a short squeeze
                self.print_watchlist_report()       # Print short squeeze report
            
            # Else if short squeeze dataframe is empty, exit from function
            else:
                print(">>> No Short Squeeze Data Available!. . .")
            
            return

        
        except FileNotFoundError:       # If excel file w/ top 25 ticker sentiment data is not found, exit from function
            logging.warning(f"*** FileNotFoundError: Excel file '{dir_path}/ticker_sentiment_top25' not found. . .")
            return
        
        except Exception:               # If an Unknown Exception occured, exit from function
            logging.error("*** Unexpected Exception Occured! ***", exc_info=True)    
            return  



    def is_price_uptrend(self, ticker, numDays=4):
        past_week_df = yf.Ticker(ticker).history(period='5d')['Close']          # Get the close price of the stock from the last 5 days
        prev_close = 0                                                          # Initialize previous close

        for close_price in past_week_df[:numDays]:                              # Iterate through the close prices of the most recent 4 trading days

            if close_price < (prev_close * 1.025):                              # If close price is less than 25% of the previous close price, there is no price uptrend
                return False

            prev_close = close_price                                            # Update previous close price to be current close price 

        return True                                                             # Else there is a price uptrend



    def get_ticker_data(self, ticker):
        # Create dictionary for dataframe row entry
        df_row = dict()

        # Gether Yahoo finance data on ticker
        ticker_data = yf.Ticker(ticker)

        # Add ticker symbol to df row
        df_row['Ticker'] = ticker
        
        # Add current price (close price) for ticker to df row
        df_row['Current Price'] = ticker_data.history(period='1d').iloc[0]['Close']

        # Determine if current stock price is within 35% of its 52 week low
        df_row['Good Yearly Low'] = self.check_yearly_low(df_row['Current Price'], ticker_data)

        # Add previous close price for stock to df row
        df_row['Prev Close'] = ticker_data.info['previousClose']

        # Add avg volume of stock to df row
        df_row['Avg Volume'] = ticker_data.info['averageVolume']

        # Determine percent change between current price and prev close price and add to df row
        df_row['Percent Change'] = round((((df_row['Current Price']/df_row['Prev Close']) - 1) * 100), 3)

        return df_row



    def check_yearly_low(self, current_price, ticker_data):
        # Get 52 week low close price for stock
        fiftyTwoWeekLow = ticker_data.info['fiftyTwoWeekLow']

        # If current price of ticker is within 35% of 52 week low, add to short squeeze watchlist
        if current_price <= (fiftyTwoWeekLow * 1.35):
            return True
        
        return False



    def check_watchlist(self):
        for ticker in self.short_squeeze_df.index:                               # Iterate through all tickers within short squeeze dataframe
            self.check_volume_trend(ticker)                                      # Check stock volume trend
            self.check_price_trend(ticker)                                       # Check stock price trend
            self.check_shorts_beta(ticker)                                       # Check shorts beta on stock
            self.check_pain(ticker)                                              # Check max pain of stock



    def check_volume_trend(self, ticker, numDays=10):
        prev_volume, uptrend, downtrend, days_above_avg_vol = 0, 0, 0, 0        # Initialize previous volume, uptrend days, downtrend days, and days above average volume
        trend_list = list()                                                     # Create empty list to capture volume trends

        ticker_data = yf.Ticker(ticker)
        volume_list = ticker_data.history(period="1mo")['Volume']               # Get stock ticker volumes over the past 1 month of trading
        volume_list = volume_list[-numDays-1:-1]                                # Keep only last 10 trading days worth of volumes (Ignore current day volume)
        volume_list.reset_index(drop=True, inplace=True)                        # Reset volume index from dates to integers

        avg_volume = self.short_squeeze_df.loc[ticker, 'Avg Volume']            # Get average volume for stock ticker

        for i, volume in volume_list.iteritems():                               # Iterate through stock volumes over the past 10 trading days  

            if volume > (1.5 * avg_volume):                                     # If daily volume above 150% of average volume, increment days above average volume by one  
                days_above_avg_vol += 1

            if i < 6:                                                           # Only check most recent 6 trading days for vol uptrend (Still trying to determine why that is??)

                if prev_volume < volume:                                        # If previous volume is less than current volume, there is an uptrend in volume
                    uptrend += 1
                    downtrend = 0
                    trend_list.append(True)

                else:                                                           # Else there is a downtrend in volume
                    downtrend += 1
                    trend_list.append(False)

                
                if downtrend >= 2:                                              # If more than 2 trading days have a volume downtrend indicator, reset uptrend 
                    uptrend = 0                                                 # and set volume uptrend status to False
                    self.short_squeeze_df.loc[ticker, 'Volume Uptrend'] = False

                elif uptrend >= 3:                                              # Else if more than 3 trading days have a volume uptrend indicator, reset downtrend
                    downtrend = 0                                               # and set volume uptrend status to True
                    self.short_squeeze_df.loc[ticker, 'Volume Uptrend'] = True

            prev_volume = volume                                                # Update previous volume to be current volume
        
        if not self.short_squeeze_df.loc[ticker, 'Volume Uptrend']:             # If volume uptrend indicator for stock ticker is False
            
            for trend in trend_list[-4:]:                                       # Iterate through last 4 trading days of volume trends
                if not trend:                                                   # If not upward trend, exit function
                    return

            self.short_squeeze_df.loc[ticker, 'Volume Uptrend'] = True          # Else set flag for volume uptrend to True

        if days_above_avg_vol < 2:                                              # Remove ticker from watchlist if it has fewer than 2 days above 150% avg volume
            print(f">>> Volume Trend Check: Dropping {ticker} from watchlist. . .")
            self.short_squeeze_df.drop(ticker)

        return
           


    def check_price_trend(self, ticker, numDays=6):
        price_downtrend = 0                                                 # Initialize price downtrend
        self.short_squeeze_df.loc[ticker, 'Price Uptrend'] = True           # Initialize price uptrend for ticker

        ticker_data = yf.Ticker(ticker)                                    
        prev_close_list = ticker_data.history(period="1mo")['Close']        # Get stock ticker close price over the past 1 month of trading
        prev_close_list = prev_close_list[-numDays-2:-1]                    # Only collect the last 6 days of close prices (ignore current day close price)

        prev_close = prev_close_list[0]                                     # Set previous close price to be 7th past trading day

        for close_price in prev_close_list[1:]:                             # Iterate through most recent 6 trading days (Only 1 day can be negative, other days MUST have consistent 5% increases in close price)
                    
            if close_price < (prev_close * 1.05):                           # If observed close price is less than 5% of the previous close, there is a price downtrend
                price_downtrend += 1
            
            if price_downtrend > 1:                                         # If more than one day of price downtrend, set flag for price uptrend to False
                self.short_squeeze_df.loc[ticker, 'Price Uptrend'] = False

            prev_close = close_price                                        # Update previous close price to be current close price

        return



    def check_shorts_beta(self, ticker):
        self.short_squeeze_df.loc[ticker, 'High Shares Percent Change'] = False     # Initialize flag for High Shares % Change
        self.short_squeeze_df.loc[ticker, 'High Short Shares'] = False              # Initialize flag for High Short Shares
        self.short_squeeze_df.loc[ticker, 'High Beta'] = False                      # Initialize flag for High Beta

        ticker_data = yf.Ticker(ticker)
        short_percent_of_float = ticker_data.info['shortPercentOfFloat']            # Get the Short % of Float for stock
        self.short_squeeze_df.loc[ticker, 'Short Percent Float'] = short_percent_of_float

        if short_percent_of_float is not None:                                      # If there is a short % of float for stock ticker

            # If short % of float is >= 15% and stock ticker has had a close price percent change >= 10%, set flag for High Shares % Change to True
            if short_percent_of_float >= 15 and self.short_squeeze_df.loc[ticker, 'Percent Change'] >= 10:
                self.short_squeeze_df.loc[ticker, 'High Shares Percent Change'] = True
            
            # If short % of float is >= 5%, set flag for High Short Shares to True
            if short_percent_of_float >= 5:
                self.short_squeeze_df.loc[ticker, 'High Short Shares'] = True

        beta = ticker_data.info['beta']                                             # Get Beta for stock

        if beta is not None:                                                        # If there is a beta value for stock ticker
            if not (beta > -1 and beta < 1):                                        # If beta is not between -1 and 1, set flag for High Beta to True
                self.short_squeeze_df.loc[ticker, 'High Beta'] = True

        return



    def check_pain(self, ticker):
        # Calculate the Shorts Pain for the stock ticker
        self.short_squeeze_df.loc[ticker, 'Shorts Pain'] = round(self.short_squeeze_df.loc[ticker, 'Short Percent Float'] *\
                                                                 self.short_squeeze_df.loc[ticker, 'Percent Change'],3)

        return



    def print_watchlist_report(self):
        print(">>> Writing Short Squeeze Report. . .")

        # Create watchlist report file
        file = open(f'{get_dir_path()}/short_squeeze_report.txt', 'w')

        file.write("====================================================================\n")
        file.write("                       SHORT SQUEEZE REPORT                         \n")
        file.write("====================================================================\n")

        # Write stocks that have positive price and volume trends
        file.write('\n')
        file.write(">>> Stocks w/ Positive Price and Volume Trend\n")
        for ticker in self.short_squeeze_df[(self.short_squeeze_df['Volume Uptrend']==True) & (self.short_squeeze_df['Price Uptrend']==True)].index:
            file.write("Ticker: %-8s | %% Change: %-8.2f" % (ticker, self.short_squeeze_df.loc[ticker, 'Percent Change'])) 

        # Write stocks that have shorts >= 5%
        file.write('\n')
        file.write(">>> Stocks w/ Shorts >= 5%\n")
        for ticker in self.short_squeeze_df[self.short_squeeze_df['High Short Shares']==True].index:
            #if stock_watchlist.loc[ticker, 'Short Percent Float'] >= 15:
            file.write("Ticker: %-8s | Shorts %% Float: %-8.2f | %% Change: %-8.2f" % (ticker, self.short_squeeze_df.loc[ticker, 'Short Percent Float'],
                                                                                        self.short_squeeze_df.loc[ticker, 'Percent Change']))

        # Write stocks that have a price uptrend
        file.write('\n')
        file.write(">>> Stocks w/ Price Uptrend\n")
        for ticker in self.short_squeeze_df[self.short_squeeze_df['Price Uptrend']==True].index:
            file.write("Ticker: %-8s | %% Change: %-8.2f" % (ticker, self.short_squeeze_df.loc[ticker, 'Percent Change'])) 
            
        # Write stocks that have short pain and price uptrend
        file.write('\n')
        file.write(">>> Possible Great Stocks w/ Short Pain and 6-Day Price Uptrend\n")
        for ticker in self.short_squeeze_df[(self.short_squeeze_df['High Short Shares']==True) & (self.short_squeeze_df['Price Uptrend']==True)].index:
            file.write("Ticker: %-8s | Shorts Pain: %-8.2f | %% Change: %-8.2f" % (ticker, self.short_squeeze_df.loc[ticker, 'Shorts Pain'],
                                                                                    self.short_squeeze_df.loc[ticker, 'Percent Change']))        

        # Write stocks that have positive price and volume uptrend and a high short shares float value
        file.write('\n')
        file.write(">>> Perfect Stocks w/ Positive Price Trend, Volume Trend, and High Short Shares Float\n")
        for ticker in self.short_squeeze_df[(self.short_squeeze_df['High Short Shares']==True) & (self.short_squeeze_df['Price Uptrend']==True) & (self.short_squeeze_df['Volume Uptrend']==True)].index:
            file.write("Ticker: %-8s | %% Change: %-8.2f" % (ticker, self.short_squeeze_df.loc[ticker, 'Percent Change'])) 

        # Write stocks that are experiencing greatest pain
        file.write('\n')
        file.write(">>> Top 10 Stocks Experiencing Greatest Pain (Short Pain)\n")
        for ticker in self.short_squeeze_df.sort_values(by=['Shorts Pain'], ascending=False).index:
            file.write("Ticker: %-8s | Shorts Pain: %-8.2f | %% Change: %-8.2f\n" % (ticker, self.short_squeeze_df.loc[ticker, 'Shorts Pain'],
                                                                                        self.short_squeeze_df.loc[ticker, 'Percent Change']))  

        # Close the file after writing
        file.close()    



    def get_watchlist(self):
        return self.short_squeeze_df        # Return the short squeeze watchlist
