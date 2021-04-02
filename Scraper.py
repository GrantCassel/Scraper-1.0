# Program Created By: GC
# Description: Scrapes the Newegg.com website and collects the relevant data and dumps it into a CSV
# Created Date: 3/31/2021
# Version: 1.0


from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import datetime
import re
import pandas as pd

myUrl = 'https://www.newegg.com/todays-deals?cm_sp=%20homepage_dailydeal-_-%20head_navigation-_-l'

# All the lists of data we are scraping
iName = []
iBrand = []
iURL = []
iPriceBefore = []
iPriceAfter = []
iPercentSaved = []
iShippingPrice = []
iTotalPrice = []
iPromoDiscount = []
iNumberOfReviews = []

uClient = uReq(myUrl)
page_html = uClient.read()
uClient.close()

pageSoup = soup(page_html, "html.parser")

# All Items That Are In The Deals Page
items = pageSoup.find("div", {"class":"item-cells-wrap tile-cells five-cells"})

# This function filters the NULLs and returns the total price
def GetTotalPrice(afterPrice, shippingPrice):
	# If Both Are Not Null
	if afterPrice != "NULL" and shippingPrice != "NULL":
		return str(float(afterPrice) + float(shippingPrice))

	# Shipping Price Is Null
	if afterPrice != "NULL" and shippingPrice == "NULL":
		return str(afterPrice)

	# After Price Is Null
	if afterPrice == "NULL" and shippingPrice != "NULL":
		return "NULL"

	# If Both Are Null
	if afterPrice == "NULL" and afterPrice == "NULL":
		return "NULL"

for item in items:
	# Variables gathered
	itemName = ""
	itemBrand = ""
	itemURL = ""

	itemPriceBefore = ""
	itemPriceAfter = ""
	percentSaved = ""
	shippingPrice = ""
	totalPrice = ""
	promoDiscount = ""
	numberOfReviews = ""

	# Try to get the variables
	# The Item's Name
	try:
		itemName = item.find(class_='item-img').img['title']
	except:
		itemName = "NULL"

	# Brand Name
	try:
		itemBrand = item.find(class_='item-branding').img['title']
	except:
		itemBrand = "NULL"

	# URL 
	try:
		itemURL = item.find(class_='item-img')['href']
	except:
		itemURL = "NULL"

	# Price Before
	try:
		# Remove $ and commas
		itemPriceBefore = item.find(class_='price-was-data').text
		itemPriceBefore = itemPriceBefore.replace("$", '')
		itemPriceBefore = itemPriceBefore.replace(',', '')
	except:
		itemPriceBefore = "NULL"

	# Price After
	try:
		# Chop off the last few digits of the string
		# Also remove % and commas
		itemPriceAfter = item.find(class_='price-current').text
		itemPriceAfter = itemPriceAfter.replace("$", '')
		itemPriceAfter = itemPriceAfter.replace(',', '')
		itemPriceAfter = itemPriceAfter[:len(itemPriceAfter) - 2]
	except:
		itemPriceAfter = "NULL"

	# Percent Saved
	try:
		# Chop off the percent sign
		saved = item.find(class_='price-save-percent').text
		percentSaved = saved[:len(saved) - 1]
	except:
		percentSaved = "NULL"

	# Shipping Price
	try:
		# TODO Check how it is formatted (All currently are free shipping)
		shippingPrice = item.find(class_='price-ship').text

		if shippingPrice == "Free Shipping":
			shippingPrice = 0
	except:
		shippingPrice = "NULL"

	# Total Price
	totalPrice = GetTotalPrice(itemPriceAfter, shippingPrice)

	# Promotion Discount
	try:
		# Grab the promo line and cut it from the & to the next space
		discount = item.find(class_='item-promo').text
		discount = re.findall('\$\d+(?:\.\d+)?', discount)

		# Return it back to a string from a list of strings
		promoDiscount = discount[0]

		# Remove the dollarsign
		promoDiscount = promoDiscount[1:]
	except:
		promoDiscount = "NULL"

	# Number of Reviews
	try:
		# Remove commas and the pair of ()
		numberOfReviews = item.find(class_="item-rating-num").text
		numberOfReviews = numberOfReviews.replace(',','')
		numberOfReviews = numberOfReviews.replace('(', '')
		numberOfReviews = numberOfReviews.replace(')', '')
	except:
		numberOfReviews = "NULL"

	# Append all the data to their respective lists
	iName.append(itemName)
	iBrand.append(itemBrand)
	iURL.append(itemURL)
	iPriceBefore.append(itemPriceBefore)
	iPriceAfter.append(itemPriceAfter)
	iPercentSaved.append(percentSaved)
	iShippingPrice.append(shippingPrice)
	iTotalPrice.append(totalPrice)
	iPromoDiscount.append(promoDiscount)
	iNumberOfReviews.append(numberOfReviews)

# Throw everything into a dataframe
scrapedData = pd.DataFrame(list(zip(iName, iBrand, iURL, iPriceBefore, iPriceAfter, iPercentSaved, iShippingPrice, iTotalPrice, iPromoDiscount, iNumberOfReviews)),
							columns = ["Name", "Brand", "URL", "Before Price", "After Price", "Percent Saved", "Shipping Price", "Total Price", "Promo Discount", "# of Reviews"])

# Timestamp every column
scrapedData['Date'] = str(datetime.datetime.now().strftime("%d %B %Y"))

# Export the dataframe into a CSV file
scrapedData.to_csv("Newegg Scrape " + str(datetime.datetime.now().strftime("%d %B %Y")) + ".csv")