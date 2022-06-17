from flask import Flask, request, jsonify, session, redirect, url_for
from helpers.db_helpers import *
import sys
import random
import string
import bcrypt

app = Flask(__name__)


def encrypt_password(password):
    salt = bcrypt.gensalt(rounds=5)
    hash_result = bcrypt.hashpw(password.encode(), salt)
    print(hash_result)
    decrypted_password = hash_result.decode()
    return decrypted_password




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
@app.post('/restaurant/signup')
def restaurant_register():
    data = request.json
    password = data.get('password')
    name = data.get('name')
    address = data.get('address')
    phone_num = data.get('phoneNumber')
    bio = data.get('bio')
    profile_url = data.get('profileUrl')
    banner_url = data.get('bannerUrl')
    city = data.get('city')
    city_list = run_query("SELECT * FROM city WHERE city=?", [city])
    if not city_list:
        return jsonify("Please select a valid city.")
    else:
        run_query("INSERT INTO restaurant (password, name, address, phone_num, bio, profile_url, banner_Url, city) VALUES (?,?,?,?,?,?,?,?)", [password, name, address, phone_num, bio, profile_url, banner_url, city])

# Client register, login, logout
# TODO client info UPDATE and account delete

@app.post('/api/client/signup')
def client_register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    password_input = data.get('password')
    password = encrypt_password(password_input)
    picture_url = data.get('pictureUrl')
    run_query("INSERT INTO client (email, username, password, first_name, last_name, picture_url) VALUES (?,?,?,?,?,?)", [email, username, password, first_name, last_name, picture_url])
    client_data = run_query("SELECT * FROM client WHERE username=?", [username])
    login_token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    client = {}
    client['id'] = client_data[0][0]
    client['username'] = client_data[0][2]
    client['token'] = login_token
    client_id = client_data[0][0]
    run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [login_token, client_id])
    return jsonify(client),201
    

@app.post('/api/client/login')
def client_login():
    data = request.json
    username_input = data.get('username')
    password_input = data.get('password')
    client_info = run_query("SELECT * FROM client WHERE username=?", [username_input])
    client_password = client_info[0][3]
    if bcrypt.checkpw(password_input.encode(), client_password.encode()):
        print("You are now logged in")
    else:
        print("Credentials don't match")
    client_id = client_info[0][0]
    client_username = client_info[0][2]
    client_password = client_info[0][3]
    login_token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    client = {}
    client['id'] = client_id
    client['username'] = client_username
    client['token'] = login_token
    logged_in = run_query("SELECT * FROM client_session WHERE client_id=?",[client_id])
    if not logged_in:
        run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [login_token,client_id])
    elif client_id == logged_in[0][3]:
        run_query("DELETE FROM client_session WHERE client_id=?",[client_id])
        run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [login_token,client_id])
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