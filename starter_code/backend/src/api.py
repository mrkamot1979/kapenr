from ast import Try
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    if request.method == "GET":
        drinks_all = Drink.query.all()
        drinks = [drink.short() for drink in drinks_all]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    if request.method == "GET":
        drinks_all = Drink.query.all()
        drinks = [drink.long() for drink in drinks_all]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    if request.method == "POST":
        body = request.get_json()
        print(body)
        try:
            recipe = body['recipe']
            if type(recipe) is dict:
                recipe = [recipe]

            title = body['title']
            drink = Drink(title=title, recipe=json.dumps(recipe))
            drink.insert()
            drinks = [drink.long()]

            return jsonify({
                'success':True,
                'drinks': drinks
            })

        except:
            abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    if request.method == "PATCH":
        body = request.get_json()
        print(body)

        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not drink:
            abort(404)
        
        try:
            title = body.get('title', None)

            recipe = body.get('recipe', None)

            if title != None:
                drink.title = title

            if recipe != None:
                drink.recipe = json.dumps(body['recipe'])

            drink.update()
            drinks = [drink.long()]

            return jsonify({
                'success': True,
                'drinks': drinks
            }), 200
         
        except print(0):
            abort(422)
            

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    if request.method == "DELETE":
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()

        if not drink:
            abort(404)

        try:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': drink.id
            }), 200
        except:
            abort(422)



# Error Handling
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code



@app.errorhandler(400)
def error_bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad request"
    }), 400

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def error_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Not found"
    }), 404


'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def error_unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
Internal Server Error
'''

@app.errorhandler(500)
def error_internal_server(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': "Internal Server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

if __name__ == "__main__":
    app.debug = True
    app.run()
