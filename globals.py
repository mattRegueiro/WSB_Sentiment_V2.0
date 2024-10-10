"""
----------------
globals.py
----------------
Contains all global variables used by the program.

"""

import helper
from imports import *

URL                     = "https://stocks.comment.ai/"                        # URL to WSB sentiment AI webpage
MARKET_OPEN             = dt.datetime.strptime('06:30AM', '%I:%M%p').time()   # 06:30 AM
MARKET_CLOSE            = dt.datetime.strptime('01:00PM', '%I:%M%p').time()   # 01:00 PM
HOLIDAY_DETERMINED      = False                                               # Determine if Market Holiday
IS_MARKET_OPEN          = False                                               # Initialize US stock market open flag to be false (market closed)
IS_WEEKEND              = False                                               # Initialize weekend determination flag to be false
MAX_RETRIES             = 12                                                  # Number of internet reconnectivity attempts
TICKER_DICT             = helper.get_all_stock_tickers()                      # Collects all available company stock tickers
WORDS_TO_IGNORE         = helper.get_words_to_ignore()                        # Read txt file containing words to ignore
HOLIDAYS                = helper.get_market_holidays()                        # Get US Stock Market Holidays

# Custom spinner design
MONEY_SPINNER           = Spinner(["( $    )",
                                   "(  $   )",
                                   "(   $  )",
                                   "(    $ )",
                                   "(     $)",
                                   "(    $ )",
                                   "(   $  )",
                                   "(  $   )",
                                   "( $    )",
                                   "($     )"], 100)
WSB_SPINNER             = yaspin(spinner=MONEY_SPINNER, color="white")

# List of top mentioned ETF's
ETFS_LIST               = ["EEM", "SPY", "GDX", "XLF", "XOP", "AMLP", "FXI", 
                           "QQQ", "EWZ", "EFA", "USO", "HYG", "IAU", "IWM", 
                           "XLE", "XLU", "IEMG", "GDXJ", "SLV", "VWO", "XLP",
                           "XLI", "OIH", "LQD", "XLK", "VEA", "TLT", "IEFA", 
                           "XLV", "EWJ", "GLD", "IYR", "BKLN", "EWH", "ASHR", 
                           "XLB", "RSX", "JNK", "KRE", "XBI", "AGG", "VNQ", 
                           "GOVT", "UNG", "IVV", "XLY", "EWT", "PFF", "XLRE", 
                           "MCHI", "INDA", "BND", "USMV", "EZU", "SMH", "XRT", 
                           "EWY", "IEF", "SPLV", "XLC", "IJR", "VIXY", "EWG", 
                           "EWW", "VTI", "VGK", "IBB", "PGX", "VOO", "EMB", 
                           "SCHF", "VEU", "SJNK", "EMLC", "XME", "DIA", "EWA", 
                           "VCSH", "JPST", "MLPA", "VCIT", "ITB", "ACWI", "KWEB", 
                           "EWC", "EWU", "BNDX", "SHY", "VT", "IWD", "VXUS", 
                           "MBB", "ACWX", "XHB", "BSV", "SHV", "FEZ", "IWF", 
                           "IGSB", "SPYV", "ITOT", "FPE", "FVD", "SHYG", "VYM", 
                           "BBJP", "DGRO", "KBE", "VTV", "SPAB", "SPIB", "IWR", 
                           "DBC", "BIL", "SPSB", "FLOT", "GLDM", "VIG", "XES", 
                           "SCHE", "TIP", "PDBC", "SPYG", "MINT", "SCZ", "SPDW", 
                           "PCY", "USHY", "IXUS", "NEAR", "EPI", "SPLG", "HYLB", 
                           "AAXJ", "SPEM", "VMBS", "BIV", "QUAL", "ILF", "EWP",
                           "TQQQ"]

# US/Canada cell carriers dictionary
CARRIERS = {
    # US Carriers
    "alltel"        : "@mms.alltelwireless.com",
    "att"           : "@mms.att.net",
    "boost"         : "@myboostmobile.com",
    "cricket"       : "@mms.cricketwireless.net",
    "p_fi"          : "msg.fi.google.com",
    "sprint"        : "@pm.sprint.com",
    "tmobile"       : "@tmomail.net",
    "us_cellular"   : "@mms.uscc.net",
    "verizon"       : "@vtext.com",
    "virgin"        : "@vmpix.com",

    # Canada Carriers
    "bell"          : "@txt.bell.ca",
    "chatr"         : "@fido.ca",
    "fido"          : "@fido.ca",
    "freedom"       : "@txt.freedommobile.ca",
    "koodo"         : "@msg.koodomobile.com",
    "public_mobile" : "@msg.telus.com",
    "telus"         : "@msg.telus.com",
    "rogers"        : "@pcs.rogers.com",
    "sasktel"       : "@sms.sasktel.com",
    "speakout"      : "@pcs.rogers.com",
    "virgin_ca"     : "@vmobile.ca"
}

# TEXT MESSAGE SEPARATOR
SEPARATOR = '-' * 60

# SUBJECT MESSAGES
STARTUP_MSG_SUBJECT     = "Email SMS Startup"
WSB_MSG_SUBJECT         = "WSB Tickers"
SHUTDOWN_MSG_SUBJECT    = "Email SMS Shutdown"
MSG_SUBJECT             = "Email SMS Message"
ERROR_MSG_SUBJECT       = "Email SMS Error"

# SMS MESSAGES
SMS_STARTUP             = "SMS is active! Waiting to send WSB Tickers!\n" + SEPARATOR 
SMS_WSB_TICKERS         = "Here are the top 10 mentioned WSB Tickers!\n" + SEPARATOR
SMS_CONFIRM             = "Command Received...Processing Request...\n" + SEPARATOR
SMS_SHUTDOWN            = "SMS shutting down...\n" + SEPARATOR

# ERROR MESSAGES
SMS_ERROR_INVALID_CMD   = "ERROR: Invalid command entered.\n" + SEPARATOR
SMS_ERROR_GENERAL       = "ERROR: An unknown error occured.\n" + SEPARATOR