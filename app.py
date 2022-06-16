from flask import Flask, request, jsonify, session, redirect, url_for
from helpers.db_helpers import *
import sys
import random
import string

app = Flask(__name__)

# Restaurant and relating menu GET requests

@app.get('/api/restaurants')
def get_restaurants():
    restaurant_list = run_query("SELECT * FROM restaurant")
    resp = []
    for restaurant in restaurant_list:
        an_obj = {}
        an_obj['name'] = restaurant[1]
        an_obj['address'] = restaurant[2]
        an_obj['phone_num'] = restaurant[3]
        an_obj['bio'] = restaurant[4]
        an_obj['profile_img'] = restaurant[5]
        an_obj['banner_img'] = restaurant[6]
        resp.append(an_obj)
    return jsonify(resp), 200

@app.get('/api/restaurants/menu')
def get_menu():
    # TODO: db SELECT
    menu_items = run_query("SELECT * FROM menu_item WHERE restaurant_id=restaurant.id")
    resp = []
    for item in menu_items:
        an_obj = {}
        an_obj['name'] = item[1]
        an_obj['description'] = item[2]
        an_obj['price'] = item[3]
        an_obj['image'] = item[4]
        resp.append(an_obj)
    return jsonify(resp), 200

# TODO Restaurant register and login


# Client register, login, logout
# TODO client info UPDATE and account delete

@app.post('/api/client/signup')
def client_register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    password = data.get('password')
    picture_url = data.get('pictureUrl')
    run_query("INSERT INTO client (email, username, password, first_name, last_name, picture_url) VALUES (?,?,?,?,?,?)", [email, username, password, first_name, last_name, picture_url])
    client_data = run_query("SELECT * FROM client WHERE username=? AND password=?", [username,password])
    print(client_data)
    if client_data:
        loginToken = ''.join([random.choice(string.ascii_letters
            + string.digits) for n in range(32)])
        client = {}
        client['id'] = client_data[0][0]
        client['username'] = client_data[0][1]
        client['token'] = loginToken
        client_id = client_data[0][0]
        run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [loginToken, client_id])
        return jsonify(client),201
    else:
        return jsonify("Error occurred"),

@app.post('/api/client/login')
def client_login():
    data = request.json
    username_input = data.get('username')
    password_input = data.get('password')
    client_data = run_query("SELECT * FROM client WHERE username=? AND password=?", [username_input, password_input])
    if not client_data:
        return jsonify("Couldn't find a record to match the credentials")
    print(client_data[0][3])
    client_id = client_data[0][0]
    client_username = client_data[0][2]
    client_password = client_data[0][3]
    if client_username != username_input:
        return jsonify("Credentials don't match.  Please try again")
    if client_password != password_input:
        return jsonify("Credentials don't match.  Please try again")
    loginToken = ''.join([random.choice(string.ascii_letters
        + string.digits) for n in range(32)])
    client = {}
    client['id'] = client_id
    client['username'] = client_username
    client['token'] = loginToken
    logged_in = run_query("SELECT * FROM client_session WHERE client_id=?",[client_id])
    if not logged_in:
        run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [loginToken,client_id])
    elif client_id == logged_in[0][3]:
        run_query("DELETE FROM client_session WHERE client_id=?",[client_id])
        run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [loginToken,client_id])
    return jsonify(client),201
    

    
# @app.patch('/api/client/profile')
# def edit_profile():
#     params = request.args
#     email = params.get('email')
#     username = params.get('username')
#     password = params.get('password')
#     first_name = params.get('firstName')
#     last_name = params.get('lastName')
#     picture_url = params.get('pictureUrl')
#     data = request.json
#     email = data.get('email')
#     username = data.get('username')
#     password = data.get('password')
#     first_name = data.get('firstName')
#     last_name = data.get('lastName')
#     picture_url = data.get('pictureUrl')
#     run_query("UPDATE client SET (email, username, password, first_name, last_name, picture_url) WHERE id=?", [])
#     return jsonify("Your info was successfully edited"), 200

@app.delete('/api/client/logout')
def client_logout():
    params = request.args
    client_id = params.get('id')
    run_query("DELETE FROM client_session WHERE client_id=?",[client_id])
    return jsonify("Client logged out"),200



if (len(sys.argv) > 1):
    mode = sys.argv[1]
else:
    print("No mode argument: testing | production")
    exit()    
    
if mode == "testing":
    from flask_cors import CORS
    CORS(app)    # Only want CORS on testing servers
    app.run(debug=True)
elif mode == "production":
    import bjoern
    bjoern.run(app, "0.0.0.0", 5004)
    print('Running in development mode!')
else:
    print("Invalid mode.  Must be testing or production")