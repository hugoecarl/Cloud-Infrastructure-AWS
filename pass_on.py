from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
import requests
import json

connection = "http://34.227.115.205:5000/"

app = Flask(__name__, static_url_path="")
api = Api(app)

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
        con = requests.get(connection+"tasks").json()
        return jsonify(con)
    
    def post(self):
        args = self.reqparse.parse_args()
        con = requests.post(connection+"tasks", json = args).json()
        return con


class TaskAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        con = requests.get(connection+"tasks/"+str(id)).json()
        return jsonify(con)


    def put(self, id):
        args = self.reqparse.parse_args()
        con = requests.put(connection+"tasks/"+str(id), json = args).json()
        return jsonify(con)
    
    def delete(self, id):
        con = requests.delete(connection+"tasks/"+str(id)).json()
        return {'result': True}


api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/tasks/<int:id>', endpoint='task')
api.add_resource(HealthCheck, '/healthcheck/', endpoint='healthcheck')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)


