from pymongo import MongoClient
from pymongo.collection import Collection

from config import mongo_ip, mongo_port

client = MongoClient(mongo_ip, mongo_port)
db = client.forum_bot

users_col: Collection = db.users
# users_col {'tg_id': '', 'username': '', 'full_name': '', 'admin': Bool, 'code': '', 'platform': ''}

events_col: Collection = db.events
# events_col {'category': '', 'name': '', 'desc': '', 'dt': '', users: []}

day_program_col: Collection = db.day_program
# day_program_col {'date': '', 'platform': '', "events": [{"event_name": '', "event_time": ''}]}

quest_col: Collection = db.questions
# quest_col {'category': '', 'question': '', 'answer': '', 'who_ask': {'tg_id': '', 'full_name': ''}, 'who_answer': {'tg_id': '', 'full_name': ''}}
