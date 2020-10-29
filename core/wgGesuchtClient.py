import requests
import json

class WgGesuchtClient:

    # Constants
    API_URL = 'https://www.wg-gesucht.de/api/{}'
    APP_VERSION = '1.28.0'
    APP_PACKAGE = 'com.wggesucht.android'
    CLIENT_ID = 'wg_mobile_app'
    USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Google Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36'

    # Constructor
    def __init__(self):
        self.userId, self.accessToken, self.refreshToken, self.phpSession, self.devRefNo = None, None, None, None, None

    # Performs a call to api
    def request(self, method: str, endpoint: str, params: object = None, payload: object = None, attempt: int = 0):

        # Build url
        url = self.API_URL.format(endpoint)

        # Build cookies
        cookies = [
            'PHPSESSID={}'.format(self.phpSession) if self.phpSession else None,
            'X-Client-Id={}'.format(self.CLIENT_ID),
            'X-Refresh-Token={}'.format(self.refreshToken) if self.refreshToken else None,
            'X-Access-Token={}'.format(self.accessToken) if self.accessToken else None,
            'X-Dev-Ref-No={}'.format(self.devRefNo) if self.devRefNo else None,
        ]
        cookieHeader = '; '.join(cookie for cookie in cookies if cookie)

        # Build headers
        headers = {
            'X-App-Version': self.APP_VERSION,
            'User-Agent': self.USER_AGENT,
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'application/json',
            'X-Client-Id': self.CLIENT_ID,
            'X-Authorization': 'Bearer {}'.format(self.accessToken) if self.accessToken else None,
            'X-User-Id': self.userId if self.userId else None,
            'X-Dev-Ref-No': self.devRefNo if self.devRefNo else None,
            'Cookie': cookieHeader,
            'X-Requested-With': self.APP_PACKAGE,
            'Origin': 'file://' if not self.accessToken else None
        }

        # Perform request
        r = requests.request(method=method, url=url, headers=headers, params=params, data=payload)

        # Check for response status code
        if r.status_code in range(200, 300):

            # Success, just return
            return r

        elif r.status_code == 401 and attempt < 1:

            # Responded code 401 and first attempt
            # Try to refresh token
            if self.refreshToken():

                # Success, retry request
                return self.request(method, endpoint, params, payload, attempt + 1)

            else:

                # The refresh token request failed, maybe invalid tokens?
                print('Refresh token request failed: {}'.format(r.text))
            
        else:
            
            # Request failed
            print('Request failed: {}'.format(r.text))
            return None

    # Import account data
    def importAccount(self, config: object):
        self.userId = config['userId']
        self.accessToken = config['accessToken']
        self.refreshToken = config['refreshToken']
        self.phpSession = config['phpSession']
        self.devRefNo = config['devRefNo']

    # Export account data
    def exportAccount(self):
        return {
            'userId': self.userId,
            'accessToken': self.accessToken,
            'refreshToken': self.refreshToken,
            'phpSession': self.phpSession,
            'devRefNo': self.devRefNo
        }

    # Login
    def login(self, username: str, password: str):
        
        # Build payload
        payload = {
            'login_email_username': username,
            'login_password': password,
            'client_id': self.CLIENT_ID,
            'display_language': 'de'
        }

        # Request api
        r = self.request('POST', 'sessions', None, json.dumps(payload))

        # Check for response success
        if r:

            # Success, set data
            jsonBody = r.json()
            self.accessToken = jsonBody['detail']['access_token']
            self.refreshToken = jsonBody['detail']['refresh_token']
            self.userId = jsonBody['detail']['user_id']
            self.devRefNo = jsonBody['detail']['dev_ref_no']
            self.phpSession = r.cookies['PHPSESSID']
            return True

        else:

            # Failture
            return False

    # Refresh login token
    def refreshToken(self):

        # Build payload
        payload = {
            'grant_type': 'refresh_token',
            'access_token': self.accessToken,
            'refresh_token': self.refreshToken,
            'client_id': self.CLIENT_ID,
            'dev_ref_no': self.devRefNo,
            'display_language': 'de'
        }

        # Build url
        url = 'sessions/users/{}'.format(self.userId)

        # Request api
        r = self.request('POST', url, None, json.dumps(payload))

        # Check for response success
        if r:

            # Success, set new data
            jsonBody = r.json()
            self.accessToken = jsonBody['detail']['access_token']
            self.refreshToken = jsonBody['detail']['refresh_token']
            self.devRefNo = jsonBody['detail']['dev_ref_no']
            return True

        else:

            # Failture
            return False

    # My Profile
    def myProfile(self):
        
        # Build url
        url = 'public/users/{}'.format(self.userId)

        # Request api
        r = self.request('GET', url)

        # Check for response success
        if r:

            # Success
            return r.json()

        else:

            # Failture
            return False

    # Search city by name
    def findCity(self, query: str):

        # Build url
        url = 'location/cities/names/{}'.format(query)

        # Request api
        r = self.request('GET', url)

        # Check for response success
        if r:

            # Success, just return city array
            return r.json()['_embedded']['cities']
        else:

            # Failture
            return False

    # Offers list
    def offers(self, cityId: str, categories: str, maxRent: str, minSize: str):
        
        # Build url
        url = 'asset/offers/'.format(self.userId)

        # Build params
        params = {
            'ad_type': '0',
            'categories': categories, # 0=WG-Zimmer, 1=1-Zimmer-Wohnung, 2=Wohnung, 3=Haus
            'city_id': cityId,
            'noDeact': '1',
            'img': '1',
            'limit': '20',
            'rMax': maxRent, # in €
            'sMin': minSize, # in m^2
            'rent_types': '0,1,2,3', # Same as categories?!?
            'page': '1'
        }

        # Request api
        r = self.request('GET', url, params)

        # Check for response success
        if r:

            # Success, just return offers array
            return r.json()['_embedded']['offers']

        else:

            # Failture
            return False

    # Offer detail
    def offerDetail(self, offerId: str):

        # Build url
        url = 'public/offers/{}'.format(offerId)

        # Request api
        r = self.request('GET', url)

        # Check for response success
        if r:

            # Success
            return r.json()

        else:

            # Failture
            return False

    # Contact offer
    def contactOffer(self, offerId: str, message: str):
        
        # Build payload
        payload = {
            'user_id': self.userId,
            'ad_type': 0,
            'ad_id': int(offerId),
            'messages':[
                {
                    'content': message,
                    'message_type': 'text'
                }
            ]
        }

        # Request api
        r = self.request('POST', 'conversations', None, json.dumps(payload))

        # Check for response success
        if r:

            # Success, return all conversation messanges
            return r.json()['messages']

        else:

            # Failture
            return False

    # Conversations list
    def conversations(self):

        # Build url
        url = 'conversations/user/{}'.format(self.userId)

        # Build params
        params = {
            'page': '1',
            'limit': '25',
            'language': 'de',
            'filter_type': '0'
        }

        # Request api
        r = self.request('GET', url, params)

        # Check for response success
        if r:

            # Success, just return conversation threads
            return r.json()['_embedded']['conversations']

        else:

            # Failture
            return False

    # Conversations detail
    def conversationDetail(self, conversationId):

        # Build url
        url = 'conversations/{}/user/{}'.format(conversationId, self.userId)

        # Build params
        params = {
            'language': 'de'
        }

        # Request api
        r = self.request('GET', url, params)

        # Check for response success
        if r:

            # Success
            return r.json()

        else:

            # Failture
            return False