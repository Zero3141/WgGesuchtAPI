import json
import sys
sys.path.append('.')
from core.wgGesuchtClient import WgGesuchtClient


# Init client
client = WgGesuchtClient()


# Option 1: Login & export account
# Try to login with credentials
if client.login('username', 'password'):
    
    # Logged in, export account
    account = client.exportAccount()

    # Save account object (e.g. Save as file)
    jsonAccount = json.dumps(account)
    with open('account.json', 'w') as file:
        file.write(jsonAccount)

    # Client is ready, do stuff

# Client is ready, do stuff


# Option 2: Load & import account
# Load account object (e.g. Read from file)
with open('account.json', 'r') as file:
    jsonAccount = file.read()
    account = json.loads(jsonAccount)
    client.importAccount(account)

# Client is ready, do stuff