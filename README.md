# WSB_Sentiment_V2.0

WSB_Sentiment_V2.0 is a Python-based program designed to fetch Bullish and Bearish sentiment from Reddit's WallStreetBets subreddit. It aims to predict which stocks are likely to go up or down in price by analyzing subreddit comments, extracting stock tickers, and assessing their sentiment ratings.

## Features

- **Subreddit Sentiment Extraction**: The program fetches comments from the WallStreetBets subreddit using Selenium WebDriver and parses stock tickers mentioned in the comments.
- **Sentiment Rating**: Each comment's sentiment is classified as bullish or bearish. Sentiment data is collected from [stocks.comment.ai](https://stocks.comment.ai/).
- **Bullish-to-Bearish Ratio**: For each stock ticker mentioned, a bullish-to-bearish sentiment ratio is calculated based on the comments extracted.
- **Daily Stock Predictions**: Before the stock market opens the next day, the program generates a list of stock tickers with the highest and lowest bullish-to-bearish ratio.
- **Automated Email Alerts**: Using SMTP services, the program sends a daily email report highlighting the stock tickers with the most extreme bullish and bearish sentiment.

## Usage

1. **Install Dependencies**: Install the necessary Python packages, including Selenium and any email-related libraries (e.g., `smtplib`).

2. **Configure SMTP**: Set up SMTP services to allow the program to send email alerts. You will need to provide your SMTP server details and credentials.

3. **Run the Program**: Execute the Python script to start extracting comments, calculating sentiment, and sending alerts before the market opens.

## Requirements

- Python 3.x
- Selenium WebDriver
- SMTP server credentials
- Internet connection for accessing Reddit and sentiment data from [stocks.comment.ai](https://stocks.comment.ai/)

## How it Works

1. **Subreddit Comments**: The program navigates to WallStreetBets using Selenium and retrieves the latest comments.
2. **Sentiment Analysis**: For each comment containing stock tickers, the sentiment is fetched from [stocks.comment.ai](https://stocks.comment.ai/) (Bullish or Bearish).
3. **Stock Sentiment Report**: A bullish-to-bearish ratio is calculated for each stock ticker mentioned in the comments.
4. **Email Alert**: The program sends an email summarizing the stocks with the most extreme sentiment before the next trading day begins.

## License

This project is open-source and available under the [MIT License](LICENSE).
