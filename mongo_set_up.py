# mongod --port 27017 --dbpath=./data
db.credentials.createIndex({'team_id':1},{unique: true})