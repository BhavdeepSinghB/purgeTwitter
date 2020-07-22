import tweepy
import time
import threading
import webbrowser

class TwitterPurge:
    API_KEY = 'c7iPSOknHGPPOruXrYo8d1tKe'
    API_SECRET = '31uLPFRIPXXgmzWvUdlOCsxoGaRZ4EJxIrA0fDoaoQovvuUNVz'
    ACCESS = '755691023305740289-nybekgIus7QaKbNDXNKeUZw7Qg5k92M'
    ACCESS_SECRET = 'zmlFhEVzHDpdZEZk6m8dJqYiTGSTlRKfy1X3fNTrjcfB1'
    
    me = ''
    my_id = ''
    target_user = ''
    target_user_id = ''
    alt_names = []

    def authenticate(self):
        # API calls = 3
        auth = tweepy.OAuthHandler(self.API_KEY, self.API_SECRET)
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            print('Error! Failed to get request token')
        request_token = auth.request_token
        webbrowser.open_new_tab(redirect_url)
        # verifier = input('Verifier:')
        auth = tweepy.OAuthHandler(self.API_KEY, self.API_SECRET)
        token = request_token
        auth.request_token = token

        try:
            auth.get_access_token()
        except tweepy.TweepError:
            print('Error! Failed to get access token!')
        key = auth.access_token
        secret = auth.access_token_secret
        auth = tweepy.OAuthHandler(self.API_KEY, self.API_SECRET)
        auth.set_access_token(key, secret)
        #auth.set_access_token(self.ACCESS, self.ACCESS_SECRET)
        self.api = tweepy.API(auth)
        try:
            self.api.verify_credentials()
            print("Auth OK")
            return True
        except:
            print("Error during authentication")
            return False
        
    def print_me(self):
        print(self.api.me())
    
    def get_id_from_json(self, data):
        return data._json['id']

    def get_user_mentions_id(self, status):
        id_list = []
        user_mentions = status._json['entities']['user_mentions']
        for i in user_mentions:
            id_list.append(i['id'])
        return id_list
    
    def get_target_user(self):
        # First thing we want to do is find who we want to purge
        # API calls = 1
        target_user = input("Enter @ of person you wish to purge\n")
        self.target_user = self.api.get_user(target_user)
        self.target_user_id = self.get_id_from_json(self.target_user)
        
        csvstr = input("Enter any other screen names of theirs they may have interacted with as a comma separated list\n (eg: joey_2, monica1234, chandler) press enter if none or done\n")
        self.alt_names = csvstr.split(',')
        if len(self.alt_names) == 1 and self.alt_names[0] == '':
            self.alt_names = []

    def unfriend_mutuals(self):
        # Now we find any mutual followers between the two
        # API calls = unknown
        self.me = self.api.me()._json
        self.my_id = self.me['id']

        my_followers = []
        for page in tweepy.Cursor(self.api.followers, id=self.my_id, wait_on_rate_limit=True, count=200).pages():
            try:
                my_followers.extend([self.get_id_from_json(x) for x in page])
            except tweepy.TweepError as e:
                print("Going to sleep ", e)
                time.sleep(60)

        target_user_followers = []
        for page in tweepy.Cursor(self.api.followers, id=self.target_user_id, wait_on_rate_limit=True, count=200).pages():
            try:
                target_user_followers.extend([self.get_id_from_json(x) for x in page])
            except tweepy.TweepError as e:
                print("Going to sleep ", e)
                time.sleep(60)
        
        
        #Find mutuals and destroy friendship
        mutuals = set(my_followers).intersection(target_user_followers)
        mutuals = list(mutuals)
        
        # Threading since there is no batch version of unfollowing, this saves time as the number of mutuals increases
        threads = []
        for i in mutuals:
            t = threading.Thread(target=self.api.destroy_friendship, args=(i,), daemon=True)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    
    def delete_statuses(self):
        target_statuses = []
        # Method to get all statuses and retrieve the id of those which mention the target user
        for page in tweepy.Cursor(self.api.user_timeline, id=self.my_id, wait_on_rate_limit=True).pages():
            for i in page:
                if self.target_user_id in self.get_user_mentions_id(i):
                    target_statuses.append(self.get_id_from_json(i))
                if len(self.alt_names) != 0:
                    for j in self.alt_names:
                        if j.lower() in i._json['text'].lower():
                            target_statuses.append(self.get_id_from_json(i))
        
        print("Found {} tweets mentioning the user, these will all now be deleted".format(len(target_statuses)))
        
        # Again, threading to save time
        if len(target_statuses) > 0:
            threads = []
            for i in target_statuses:
                t = threading.Thread(target=self.api.destroy_status, args=(i,), daemon=True)
                threads.append(t)
            for t in threads:
                t.start()
            for t in threads:
                t.join()

t = TwitterPurge()
if not t.authenticate():
    print("Authentication Error")
    exit(-1)

t.print_me()

# t.get_target_user()
# t.unfriend_mutuals()
# t.delete_statuses()
