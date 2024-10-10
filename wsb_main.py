"""
    WSB_Sentiment v2.0:
        Uses website "https://stocks.comment.ai/" to gather sentiment data from WSB. Stores any ticker mentions
        in a pandas dataframe and includes number of mentions to determine if a stock should be bought or sold.

    v2.0 Update:
        We use a Thread to collect WSB sentiment data. This lets us collect sentiment data continuously so we can get
        accurate data in  real time.
"""
"""
    Momentum Trading off Sentiment from r/wallstreetbets
-----------------------------------------------------------
    Idea Referenced From: https://medium.com/@mjysong/momentum-trading-off-sentiment-from-r-wallstreetbets-149c19c7538d

    General Use:
        1.) During closed market hours, the script will collect comments from Reddit's WSB subreddit. All comments are 
            collected from "https://stocks.comment.ai/" which already categorizes each comment as "bullish" or "bearish".
        
        2.) When the market opens, the script will determine an overall sentiment score and collect the top 25 mentioned 
            tickers from the collected comments. The script will then collect an open price for each stock ticker.
        
        3.) The script will then determine a 10-day EMA via the overall sentiment score. If the current day's EMA is above
            the 10-day EMA sentiment score, we will signal a "BUY". If/When the current day's EMA is below the 10-day EMA
            sentiment score, we will signal a "SELL". Otherwise a "HOLD" signal will be given.
        
        4.) During weekends, the script will only collect WSB comments and any tickers that may be mentioned.
"""

import WSB_Sentiment as WSB
import Short_Squeeze as SHORT
import Email_SMS as SMS
import globals
from helper import *
from imports import *



if __name__ == '__main__':
    program_title()                         # Pretty title for program

    wsb = WSB.WSB_Sentiment(update_hour=1)  # Setup WSB sentiment analysis class
    short_squeeze = SHORT.Short_Squeeze()   # Setup short squeeze analysis class
    email_sms = SMS.Email_SMS(delete=True,  # Setup email_sms class for sending market updates via text
                              logger=False)
   
    # If no stock tickers were collected from the csv files, exit the program 
    # (We do this because we need stock tickers to compare against mentioned tickers from WSB comments)
    if globals.TICKER_DICT is None:
        print(">>> No stock tickers collected!. . . Cannot perform analysis without a list of NASDAQ, NYSE, or AMEX tickers. . .")
        print(">>> Exiting WSB Sentiment Program. . .")
        sys.exit(0)                                         # Exit WSB program

    wsb.run()                                               # Run WSB sentiment analysis on separate thread

    # Main loop forever. . .
    while True:
        try:
            # If Weekday (Mon-Fri) and not a Market Closure Holiday or Early Market Close time is provided
            if (is_weekday()[0] and not is_market_holiday()) or (globals.MARKET_CLOSE != dt.datetime.strptime('01:00PM', '%I:%M%p').time()):
                
                if globals.IS_WEEKEND:                                      # If recently changed to weekday
                    globals.IS_WEEKEND = False

                # (--- Stock Market is Closed ---)
                if dt.datetime.now().time() >= globals.MARKET_CLOSE or dt.datetime.now().time() < globals.MARKET_OPEN:      
                   
                    if globals.IS_MARKET_OPEN:                              # If the market just closed
                        with globals.WSB_SPINNER.hidden():
                            print(">>>")
                            print(">>> $$$ US Stock Market Closed $$$")
                            wsb.get_close_price_and_percent_chng()          # Get close price and calculate percent change from open price
                            wsb.determine_potential_profits()               # Determine potential end-of-day profits and losses
                            globals.IS_MARKET_OPEN = False                  # Set market open flag to false (market closed)

               # ( --- Stock Market is Open --- )
                else:
                    if not globals.IS_MARKET_OPEN:                          # If the market just opened
                        with globals.WSB_SPINNER.hidden():
                            print(">>>")
                            print(">>> $$$ US Stock Market Open $$$") 
                            wsb.get_top_tickers()                           # Determine top 25 bullish/bearish tickers and get their open prices

                            short_squeeze.analyze_tickers()                 # Determine if any of the top 25 bullish/bearish tickers have a short squeeze
                        
                            ema = wsb.calc_ema()                            # Calculate 10 day EMA for daily bull/bear ratio
                    
                            if wsb.get_overall_sentiment() > ema:           # Set 'BUY' signal if bull/bear ratio above its 10 day EMA
                                print(">>> BUY SIGNAL SET. . .")
                                                
                            elif wsb.get_overall_sentiment() < ema:         # Set 'SELL' signal if bull/bear ratio below its 10 day EMA
                                print(">>> SELL SIGNAL SET. . .")

                            else:                                           # Set 'HOLD' signal if bull/bear ratio equal to its 10 day EMA
                                print(">>> HOLD SIGNAL SET. . .")

                            # Send SMS message with top 10 WSB tickers
                            email_sms.sms_send_top_tickers(wsb.get_top_ticker_sentiment_df())

                            globals.IS_MARKET_OPEN = True                   # Set market open flag to true (market open)
                                                        
            # Else Weekend (Sat-Sun) or Market Holiday
            else:
                if not globals.IS_WEEKEND:
                    with globals.WSB_SPINNER.hidden():
                        print(">>> US Stock Market Closed for Weekend and/or Holiday. . .")
                        globals.IS_WEEKEND = True 

            # Check if WSB sentiment thread is still active
            if not wsb.get_wsb_thread().is_alive():
                logging.warning("*** WSB Sentiment Thread Shutdown. . . Exiting WSB Sentiment Program")
                sys.exit(0)     

        # /// Keyboard Shutdown Enabled
        except KeyboardInterrupt:
            with globals.WSB_SPINNER.hidden():
                logging.warning("*** KeyboardInterrupt: Exiting WSB Sentiment Program. . .")
                sys.exit(0)

        # /// Unknown Exception Handling
        except Exception:
            with globals.WSB_SPINNER.hidden():                                                           
                logging.error(f"*** Unexpected Exception Occured! (Main Loop)***", exc_info=True)
                sys.exit(0)                                               # If an Unknown Exception occured, Exit WSB program


    


  