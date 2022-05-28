
from src.database import users_col


users = users_col.find()
for user in users:
    users_col.update_one({'_id': user["_id"]}, {'$set': {'code': str(user['code']).replace(' ', '') if user['code'] else ''}})
