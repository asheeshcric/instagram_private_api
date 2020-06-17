import json
import os
import pickle
import datetime

from instagram_private_api import Client, ClientCompatPatch


def get_user_passwd():
    global project_path
    creds_path = os.path.join(project_path, 'credentials.json')
    with open(creds_path, 'r') as f:
        creds = json.load(f)

    return creds['username'], creds['password']


def save_settings(user_settings):
    global project_path
    settings_path = os.path.join(project_path, 'user_settings.pickle')
    with open(settings_path, 'wb') as f:
        pickle.dump(user_settings, f, protocol=pickle.HIGHEST_PROTOCOL)


def get_user_settings():
    global project_path
    settings_path = os.path.join(project_path, 'user_settings.pickle')
    try:
        with open(settings_path, 'rb') as f:
            user_settings = pickle.load(f)

        return user_settings
    except Exception as error:
        print(error)
        return False


def get_followers(api, user_id, rank_token):
    max_id = ''
    followers = []
    while True:
        followers_resp = api.user_followers(
            user_id=user_id, rank_token=rank_token, max_id=max_id)
        followers += followers_resp['users']
        max_id = followers_resp['next_max_id']
        if not max_id:
            print(f'Total followers: {len(followers)}')
            return followers


def get_following(api, user_id, rank_token):
    max_id = ''
    following = []
    while True:
        following_resp = api.user_following(
            user_id=user_id, rank_token=rank_token, max_id=max_id)
        following += following_resp['users']
        max_id = following_resp['next_max_id']
        if not max_id:
            print(f'Total following: {len(following)}')
            return following


def unfriend_people(api, followers, following):
    follower_ids = [f['pk'] for f in followers]
    following_ids = [f['pk'] for f in following]
    people_to_unfollow = list(set(following_ids).difference(follower_ids))
    for user_id in people_to_unfollow:
        api.friendships_destroy(user_id=user_id)

    return people_to_unfollow


def main():
    global project_path
    success = False
    username, password = get_user_passwd()
    user_settings = get_user_settings()
    while not success:
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

        # Save all followers to a file
        followers_path = os.path.join(project_path, 'followers.json')
        with open(followers_path, 'w') as f:
            followers = get_followers(api, user_id, rank_token)
            json.dump(followers, f)

        # Save all following to a file
        following_path = os.path.join(project_path, 'followers.json')
        with open(following_path, 'w') as f:
            following = get_following(api, user_id, rank_token)
            json.dump(following, f)

        # Unfriend people that don't follow back
        print('Unfriending people that don\'t follow back')
        people_unfollowed = unfriend_people(api, followers, following)
        if len(people_unfollowed) == 0:
            print('No one eligible to unfollow')
        else:
            print('People unfollowed:')
            for user_id in people_unfollowed:
                for people in following:
                    if people['pk'] == user_id:
                        print(
                            f"User ID: {people['pk']} | {people['username']}: {people['full_name']}")
                        break

        success = True


if __name__ == '__main__':
    project_path = '/home/pi/Documents/Github/instagram_private_api/'
    now = datetime.datetime.now()
    print('-----------------------------------------------------------------------')
    print('-----------------------------------------------------------------------')
    print(f'Datetime: {now.strftime("%d/%m/%Y %H:%M:%S")}')
    try:
        main()
    except Exception as error:
        # if the cookie expires or cannot login somehow, relogin the user
        print(error)
        settings_path = os.path.join(project_path, 'user_settings.pickle')
        os.remove(settings_path)
        main()