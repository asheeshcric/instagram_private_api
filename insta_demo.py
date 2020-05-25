import json
import pickle

from instagram_private_api import Client, ClientCompatPatch


def get_user_passwd():
    with open('credentials.json', 'r') as f:
        creds = json.load(f)

    return creds['username'], creds['password']


def save_settings(user_settings):
    with open('user_settings.pickle', 'wb') as f:
        pickle.dump(user_settings, f, protocol=pickle.HIGHEST_PROTOCOL)


def get_user_settings():
    try:
        with open('user_settings.pickle', 'rb') as f:
            user_settings = pickle.load(f)

        return user_settings
    except Exception as error:
        print(error)
        return False


def main():
    success = False
    username, password = get_user_passwd()
    user_settings = get_user_settings()
    while not success:
        # try:
            if user_settings is False:
                print('Logging user to create cookie...')
                api = Client(username, password)
                user_settings = api.settings
                save_settings(user_settings)
            else:
                print('Getting saved cookie...')
                cookie = user_settings['cookie']
                api = Client('', '', cookie=cookie)
            
            user_id = api.authenticated_user_id
            rank_token = api.generate_uuid()
            following = api.user_following(user_id=user_id, rank_token=rank_token)['users']
            followers = api.user_followers(user_id=user_id, rank_token=rank_token)
            with open('followers.json', 'w') as f:
                json.dump(followers, f)

            success = True

        # except Exception as error:
        #     print(error)
        #     success = True
        #     # Make it log in again to refresh the cookie
        #     user_settings = False


if __name__ == '__main__':
    main()
