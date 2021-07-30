import requests
import requests.auth
import websocket
import json
from time import gmtime, strftime
import time

ws = 'wss://www.gasnow.org/ws'
endpoint =  "https://oauth.reddit.com/api/editusertext"

# reddit auth2 app
app_id = ''
app_secret = ''

#reddit usarname and password
username = ''
password = ''

#post that will be edited
post_id = 'oumiy3'

def addRedditToken(headers):
    client_auth = requests.auth.HTTPBasicAuth(app_id, app_secret)
    post_data = {"grant_type": "password", "username": username, "password":password}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    if response.status_code == 401:
        print('status code 401, Authorization error')
    headers.update({"Authorization":"bearer " + response.json()["access_token"]})
    return headers


def update_post(content):
    print('updating post: ', flush=True)
    body = {
        'api_type': 'json',
        'thing_id': 't3_' + post_id,
        'text':content
    }
    print('---------------', flush=True)
    post_response = requests.post(endpoint, headers=headers,data=body)
    if post_response.status_code != 200:
        wsapp.close()
    print(post_response.status_code)
    print('x-ratelimit-remaining: {}'.format(post_response.headers['x-ratelimit-remaining']), flush=True)
    print('x-ratelimit-used: {}'.format(post_response.headers['x-ratelimit-used']), flush=True)
    print('x-ratelimit-reset: {}'.format(post_response.headers['x-ratelimit-reset']), flush=True)
    print('---------------\n', flush=True)

def on_message(wsapp, message):
    date_time =time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
    message_data = json.loads(message)
    gas_prices = message_data['data']['gasPrices']
    text = 'Rapid: **{:3.1f}** | Fast: **{:3.1f}** | Standard: **{:3.1f}** | Slow: **{:3.1f}** \n\n ^({})'.format(
        #Gas Fee Now (Gwei):\n
        gas_prices['rapid']/1000000000,
        gas_prices['fast']/1000000000,
        gas_prices['standard']/1000000000,
        gas_prices['slow']/1000000000,
        date_time
    )
    print('================', flush=True)
    print(text, flush=True)
    print('================', flush=True)
    update_post(text)

while True:
    headers = addRedditToken(
        headers={"User-Agent": "liveEthGasFeePost/0.1 by mpcabete"})

    wsapp = websocket.WebSocketApp(ws, on_message=on_message)
    wsapp.run_forever()
    print('connection ended!', flush=True)
    time.sleep(10)
