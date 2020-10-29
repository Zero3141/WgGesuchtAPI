# WgGesuchtAPI
An inofficial API client for wg-gesucht.de. Not affiliated with SMP GmbH & Co. KG

### Installation
Copy `wgGesuchtClient.py` from `core` folder and import it to target file.

## Usage
### Login
Login with username/email and password:
```python
from wgGesuchtClient import WgGesuchtClient
client = WgGesuchtClient()
if client.login('username', 'password'):
  account = client.exportAccount()
```
The account object contains userId, accessToken, refreshToken, phpSession, devRefNo. Use this object for `importAccount` method to re-use session.

### Re-use session
Use previous account session. If the accessToken is expired we automatically try to refresh with the refreshToken.
```python
account = json.loads(jsonAccount)
client.importAccount(account)
```
The client is now ready to use

### API methods
Endpoints can only be used with valid session. As described in Re-use session, the accessToken is refreshed if required in every request.
|Method|Parameters|Response|
|------|----------|--------|
|myProfile|-|Profile json object|
|findCity|query: str| City array|
|offers|cityId: str, categories: str, maxRent: str, minSize: str, page: str = '1'| Offers array|
|offerDetail|offerId: str| Offer detail object|
|contactOffer|offerId: str, message: str| All conversation messanges in thread|
|conversations|page: str = '1'| Conversation threads array|
|conversationDetail|conversationId: str|Conversation object|

If a request failes, False is returned.

### Examples
Sample usages are located in examples folder:
  - Authentication in `authExample.py`
  - Offer in `offerExample.py`
