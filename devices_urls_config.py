import requests
from config import HOST, USERS

# def get_token(username, password):
#     AUTH_URL = f'{HOST}/api/v1/oauth2/token'
#     responce = requests.post(AUTH_URL, 
#                                  params={
#         'grant_type': 'password',
#         'username': username,
#         'password': password,
#         'client_id': 'android-client'
#     },
#     auth=('android-client', 'password')
#                              )
#     responce.raise_for_status()
#     data = responce.json()

#     token = data['access_token']

#     return token


# def auth_users():
#     for user_key in USERS:
#         user = USERS[user_key]
#         token = get_token(user['username'], user['password'])
#         user['token'] = token
    

# def get_house_ids(user_data):

#     HEADERS = {
#      "Content-Type": "application/json",
#      "Authorization": f"Bearer {user_data['token']}"
#     }
#     GET_HOUSE_URL = f'{HOST}/api/v1/houses'
#     responce = requests.get(
#         GET_HOUSE_URL,
#         params={
#             'language' : 'ru'
#         },
#         headers=HEADERS
#     )

#     responce.raise_for_status()

#     data = responce.json()

#     house_ids = [house['id'] for house in data]

#     user_data['houses'] = house_ids


# def get_devices_urls(user_data):
#     for house in user_data['houses']:
#         GET_DEVICES_URL = f'{HOST}/api/v1/houses/{house}/devices'

#         HEADERS = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {user_data['token']}"
#         }

#         responce = requests.get(
#             GET_DEVICES_URL,
#             headers=HEADERS
#         )

#         responce.raise_for_status()

#         data = responce.json()

#         for device in data:
#             device_id = device['nodeId']
#             controller_id = device['controllerId']

#             device_url = f'{HOST}/api/v1/ctl/{controller_id}/devices/{device_id}'
#             print(f'DEVICE URLS: {device_url}')
#             user_data['devices'].append(device_url)




def user_devices_collect():
    auth_users()
    for user_key in USERS:
        get_house_ids(USERS[user_key])
        get_devices_urls(USERS[user_key])
    

if __name__ == "__main__":
    user_devices_collect()
