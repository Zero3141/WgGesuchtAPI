import json
import sys
sys.path.append('.')
from core.wgGesuchtClient import WgGesuchtClient

# Init client
client = WgGesuchtClient()

# Load account object (e.g. Read from file)
with open('account.json', 'r') as file:
    jsonAccount = file.read()
    account = json.loads(jsonAccount)
    client.importAccount(account)

# City id can be found in findCity request
cityId = '23'

# Load offers
# Category settings seperated by ',' 
# 0=WG-Zimmer, 1=1-Zimmer-Wohnung, 2=Wohnung, 3=Haus
# maxRent in €, minSize in m^2
offers = client.offers(cityId, '0,1,2,3', '500', '20')

# Iterate through offers
for offer in offers:

    # Extract data
    print('Loading: ' + offer['offer_title'])
    offerId = offer['offer_id']

    # Load offer details
    offerDetail = client.offerDetail(offerId)
    print(offerDetail)

    # Do stuff with offer detail
