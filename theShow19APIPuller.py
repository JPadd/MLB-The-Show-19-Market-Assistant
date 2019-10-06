import requests
import pandas as pd

#Set the type of cards you want to pull. You must select 1 and cannot select more than 1.
#Options: MLB_Card | Stadium | Equipment | Sponsorship | Unlockable
cardType = "MLB_Card"


#Required initializations
players=[]
pg=1
response = requests.get("https://mlb19.theshownation.com/apis/items?type={}&page={}".format(cardType, pg))

#Loop to pull every card of specified type from API
while response.json()["listings"] != []:
	for player in response.json()["listings"]:
		players.append(player)
	pg+=1
	response = requests.get("https://mlb19.theshownation.com/apis/items?type={}&page={}".format(cardType, pg))

#Write to csv of the name cardType.csv
#Writes to same directory as this file
playerDF = pd.DataFrame(players)
playerDF.to_csv("{}_list.csv".format(cardType), index=False)
