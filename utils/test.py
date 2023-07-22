import pymongo

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
gks_users = db['gks_users']
users = db['users']


def create_new_users_db():
    queryset = list(gks_users.find({}))
    for user in queryset:
        users.insert_one({
            'ks': user.get('_id'),
            'user_id': user.get('user_id'),
            'username': user.get('username'),
            'prof': 'nachgks',
        })

create_new_users_db()
