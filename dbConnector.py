import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

DB_NAME = "chat"

db = client[DB_NAME]

if __name__=="__main__":
	pass
