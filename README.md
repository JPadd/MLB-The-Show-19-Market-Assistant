# MLB-The-Show-19-Market-Assistant
This project leverages the official MLB the Show 19 API to generate a summary of profit margins and item activity. It can also be used to pull a spreadsheet with card ratings. 

## Required Python Libraries
- requests
- pandas
- datetime

## Code Files Included
- theShow19APIPuller.py
  - Run this file to get a spreadsheet of all cards of a specific type and all their attributes.
  - MUST RUN for "MLB_Card" to run the next py file.

- ultimate_flip_helper.py
  - Run this file to generate a spreadsheet for market listings.
  - Output spreadsheet includes net profit, profit margins, buy orders posted, buy orders fulfilled, sell orders posted, sell orders fulfilled, total activities, times flipped, and total profits.
    - Buy orders posted: tallies when the best buy price goes up 
    - Buy orders fulfilled: tallies when the best buy price goes down
    - Sell orders posted: tallies when the best sell price goes down
    - Sell orders fulfilled: tallies when the best sell price goes up
    - Total actvities: sum of buy/sell orders fulfilled and posted
    - Times flipped: Minimum of buy order fulfilled and sell orders fulfilled
    - Total Profit: .5 * (buy orders fulfilled + sell orders fulfilled) * net profit.
