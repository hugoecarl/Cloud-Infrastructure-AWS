from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
import pymongo

app = Flask(__name__, static_url_path="")
api = Api(app)

tasks = []

connection = pymongo.MongoClient('35.175.190.82', 27017)

database = connection['mydb_1']

collection = database['mycol_1']

for i in collection.find({}):
    tasks.append(i)

task_fields = {
    'id' : fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean

}


class HealthCheck(Resource):
    def get(self):
        return 200




class TaskListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        return {'tasks': [marshal(task, task_fields) for task in collection.find({})]}

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'id': tasks[-1]['id'] + 1 if len(tasks) > 0 else 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        tasks.append(task)
        collection.insert_one(task)
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = [task for task in collection.find({}) if task['id'] == id]
        if len(task) == 0:
            abort(404)
        return {'task': marshal(task[0], task_fields)}

    def put(self, id):
        task = [task for task in collection.find({}) if task['id'] == id]
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
                collection.update({'id' : id},{'$set' : {k : v}})
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = [task for task in collection.find({}) if task['id'] == id]
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        collection.remove({'id':id})
        return {'result': True}


api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/tasks/<int:id>', endpoint='task')
api.add_resource(HealthCheck, '/healthcheck/', endpoint='healthcheck')



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
