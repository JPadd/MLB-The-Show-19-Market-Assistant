import requests
import pandas as pd
from datetime import datetime, timedelta

#Function to get listings on the market and calculate the profit margin and percent return for each one.
#	returns dataframe including item name, buy/sell prices, net profit, and percent return.
def get_pct_return(thingType="MLB_Card", pgStart=1, pgMax=1000):
	
	# thingType: Type of Cards you want to run the function on. One of MLB_Card | Stadium | Equipment | Sponsorship | Unlockable
	# pgStart: Page to start on. If you don't want to run over the entire set of cards, you can start with a certain page.
	# pgMax: page to end on. If you don't want to run over the entire set of cards, you can cap it on a certain page.
	
	things=[]
	fill_in = "type="+thingType+"&"
	pg=pgStart
	response = requests.get("https://mlb19.theshownation.com/apis/listings.json?{}page={}".format(fill_in, pg))
	while response.json()["listings"] != [] and pg <= (pgStart+pgMax):
		for thing in response.json()["listings"]:
			things.append(thing)
		pg+=1
		response = requests.get("https://mlb19.theshownation.com/apis/listings.json?{}page={}".format(fill_in, pg))
	things = pd.DataFrame(things)
	things['profit'] = .9 * (things['best_sell_price'] - 1) - (things['best_buy_price'] + 1)
	things["percent_return"] = (things['profit'])/things["best_buy_price"]
	return things	

#Handles cases where a listing has no buy orders, so we have to determine the sell now price of the card by finding the card's tier from the list of cards.
#	returns dataframe of listings where buy price is set to appropriate quick sell price and recalculated profit and profit margin.
def adjust_listings(listings, players):
	
	#listings: dataframe of listings on the market (output of get_pct_return function)
	#players: dataframe of players, used to match overalls of players to market listings (read CSV output from theShowAPIPuller.py)

	listings_adjusted=listings.copy()
	for index, row in listings.iterrows():
	    if row["best_buy_price"] == 0:
       		listings_adjusted.at[index, "best_buy_price"] = set_minimum_buy(row, players, listings)
	listings_adjusted['profit'] = .9 * (listings_adjusted['best_sell_price'] - 1) - (listings_adjusted['best_buy_price'] + 1)
	listings_adjusted["percent_return"] = listings_adjusted["profit"]/listings_adjusted["best_buy_price"]
	return listings_adjusted

# Gets the minimum buy price of a passed in card. Used in adjust_listings() function
#	returns quick sell price + 1 of card
def set_minimum_buy(row, players, listings):
	
	#row: row from market listings dataframe with missing buy price.
	#players: dataframe of players (read CSV output from theShowAPIPuller.py)
	#listings: dataframe of listings (ouptut from get_pct_return() function)

	minimum_sell = {"common":5, "bronze":25, "silver":100, "gold":1000, "diamond":5000}
	players_filtered = players.loc[players["name"]==row['name']]
	if len(players_filtered)==1:
		tier = players_filtered["rarity"].values[0]
	else:
		player_listings = listings.loc[listings["name"]==row["name"]]
		player_listings = player_listings.sort_values("best_sell_price")
		players_filtered = players_filtered.sort_values("ovr")
		if len(player_listings)==len(players_filtered):
			player_listings = player_listings.reset_index()
			players_filtered = players_filtered.reset_index()
			for index, list_row in player_listings.iterrows():
				if list_row["best_buy_price"]==row["best_buy_price"]:
					tier = players_filtered.loc[index]["rarity"]
		else:
			players_filtered = players_filtered.reset_index()
			tier = players_filtered.loc[0]["rarity"]
	return(minimum_sell[tier])

#Uses other functions to get dataframe of listings with profit and profit margins. 
def get_pct_return_all(playerListFile = "MLB_Card_list.csv"):
	
	#playerList: filename where list of all players is stored

	get_pct_return().to_csv("percent_return.csv")
	listings = pd.read_csv("percent_return.csv", index_col="Unnamed: 0")
	players = pd.read_csv(playerListFile)
	return adjust_listings(listings, players)

#Iterates pulling market listings and generalizes how often cards are bought and sold. Determined by changes in price.
#Returns dataframe with number of buy/sell orders posted and buy/sell order fulfilled for each listing.
def get_item_activity(thingType="MLB_Card", timeLimit=40, pgStart=1, pgMax=1000):
	
	# thingType: Type of Cards you want to run the function on. One of MLB_Card | Stadium | Equipment | Sponsorship | Unlockable
	# timeLimit: Length of time you want to iterate through for. Pulling listings takes ~20 seconds each time, so make timeLimit at least 40 seconds.
	# pgStart: Page to start on. If you don't want to run over the entire set of cards, you can start with a certain page.
	# pgMax: page to end on. If you don't want to run over the entire set of cards, you can cap it on a certain page.

	fill_in = "type="+thingType+"&"
	end_time = datetime.now() + timedelta(seconds=timeLimit)
	iteration = 1
	pg=pgStart
	while datetime.now() <= end_time:
		things=[]
		response = requests.get("https://mlb19.theshownation.com/apis/listings.json?{}page={}".format(fill_in, pg))
		while response.json()["listings"] != [] and pg <= (pgStart+pgMax):
			for thing in response.json()["listings"]:
					thing["iteration"]=iteration
					things.append(thing)
			pg+=1
			response = requests.get("https://mlb19.theshownation.com/apis/listings.json?{}page={}".format(fill_in, pg))
		things = pd.DataFrame(things)
		if iteration == 1:
			buy_prices = things[["best_buy_price", "name"]].copy()
			buy_prices.columns=[1, "name"]
			buy_prices = buy_prices[["name",1]]
			sell_prices = things[["best_sell_price", "name"]].copy()
			sell_prices.columns=[1, "name"]	
			sell_prices = sell_prices[["name", 1]]	
		else:
			buy_prices[iteration]=things["best_buy_price"]
			sell_prices[iteration]=things["best_sell_price"]
		iteration += 1
		pg = pgStart

	activity = buy_prices[["name",1]].copy()
	activity["buy_orders_posted"]=0
	activity["buy_orders_fulfilled"]=0
	activity["sell_orders_posted"]=0
	activity["sell_orders_fulfilled"]=0
	activity = activity.drop([1],axis=1)

	for index, row in buy_prices.iterrows():
		for col_index in range(1,iteration-1):
			if row[col_index+1]>row[col_index]:
				activity.at[index, "buy_orders_posted"] += 1
			elif row[col_index+1]<row[col_index]:
				activity.at[index, "buy_orders_fulfilled"] += 1

	for index, row in sell_prices.iterrows():
		for col_index in range(1,iteration-1):
			if row[col_index+1]<row[col_index]:
				activity.at[index, "sell_orders_posted"] += 1
			elif row[col_index+1]>row[col_index]:
				activity.at[index, "sell_orders_fulfilled"] += 1
	
	activity["total_activity"] = activity["sell_orders_posted"] + activity["sell_orders_fulfilled"] + activity["buy_orders_posted"] + activity["buy_orders_fulfilled"]
	return activity


#Merges item activity and pct return attributes determined for each listing.
activity = get_item_activity(timeLimit=(10*60))
activity.to_csv("item_activity.csv")
pct_return = get_pct_return_all()
pct_return.to_csv("percent_return_adjusted.csv")
combined = activity.merge(pct_return, how="outer", left_index=True, right_index=True)

combined["times_flipped"] = combined[["buy_orders_fulfilled", "sell_orders_fulfilled"]].min(axis=1)

combined["total_profits"] = .5*(combined["buy_orders_fulfilled"]+combined["sell_orders_fulfilled"])*combined["profit"]
combined = combined.sort_values("total_profits", ascending=False)

#Write output to a file. It sucks when you run this whole thing and then accidentally have it open. 
try:
	combined.to_csv("flip_assistant.csv")
except:
	combined.to_csv("flip_assitant1.csv")
