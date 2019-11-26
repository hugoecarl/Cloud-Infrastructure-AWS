import pymongo

connection = pymongo.MongoClient('54.174.65.72', 27017)

database = connection['mydb_1']

collection = database['mycol_1']

data = {
        'id':1,
        'title': u'Hugo Carl',
        'description': u'Programa Python',
        'done': False
    }
data1 = {
        'id':2,
        'title': u'Gabriel M',
        'description': u'Banco de dados SQL',
        'done': False
    }

collection.insert_one(data)
collection.insert_one(data1)

for i in collection.find({}):
    print(i)
