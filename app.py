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


# Restaurant get, signup and edit

@app.get('/api/restaurant')
def get_restaurants():
    restaurant_list = run_query("SELECT * FROM restaurant LEFT JOIN city ON city.id=restaurant.city")
    resp = []
    for restaurant in restaurant_list:
        an_obj = {}
        an_obj['id'] = restaurant[0]
        an_obj['name'] = restaurant[3]
        an_obj['address'] = restaurant[4]
        an_obj['phoneNum'] = restaurant[5]
        an_obj['bio'] = restaurant[6]
        an_obj['profileUrl'] = restaurant[7]
        an_obj['bannerUrl'] = restaurant[8]
        an_obj['city'] = restaurant[11]
        resp.append(an_obj)
    return jsonify(resp), 200

@app.post('/api/restaurant')
def restaurant_register():
    data = request.json
    email = data.get('email')
    password_input = data.get('password')
    password = encrypt_password(password_input)
    name = data.get('name')
    address = data.get('address')
    phone_num = data.get('phoneNumber')
    bio = data.get('bio')
    profile_url = data.get('profileUrl')
    banner_url = data.get('bannerUrl')
    city_input = data.get('city')
    city_list = run_query("SELECT * FROM city WHERE name=?", [city_input])
    city_id = city_list[0][0]
    city_name = city_list[0][1]
    print(city_id, city_name)
    if city_name != city_input:
        return jsonify("Please select a valid city.")
    else:
        run_query("INSERT INTO restaurant (email, password, name, address, phone_num, bio, profile_url, banner_Url, city) VALUES (?,?,?,?,?,?,?,?,?)", [email, password, name, address, phone_num, bio, profile_url, banner_url, city_id])
        print("Restaurant registered")
    restaurant_data = run_query("SELECT * FROM restaurant WHERE email=?", [email])
    print(restaurant_data[0])
    login_token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    restaurant = {}
    restaurant['id'] = restaurant_data[0][0]
    restaurant['name'] = restaurant_data[0][3]
    restaurant['token'] = login_token
    restaurant_id = restaurant_data[0][0]
    run_query("INSERT INTO restaurant_session (token, restaurant_id) VALUES (?,?)", [login_token, restaurant_id])
    print(jsonify(restaurant))
    return jsonify(restaurant),201

# Create menu items
@app.post('/api/menu')
def create_menu_item():
    params = request.args
    data = request.json
    
    login_token = params.get('token')
    restaurant_id = params.get('id')
    current_token = run_query("SELECT * FROM restaurant_session WHERE token=?",[login_token])
    
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    image_url = data.get('image_url')
    if login_token is None:
        print("You must be logged in to create a menu item")
    else:
        run_query("INSERT INTO menu_item (name, description, price, image_url, restaurant_id) VALUES (?,?,?,?,?)",[name, description, price, image_url, restaurant_id])
        print("The item was added successfully")
    return jsonify("Complete")

@app.get('/api/menu')
def get_menu_item():
    params = request.args
    restaurant_id = params.get('restaurant_id')
    menu_id = params.get('id')
    if restaurant_id and not menu_id:
        menu_items = run_query("SELECT * FROM menu_item WHERE restaurant_id=?",[restaurant_id])
    else:
        menu_items = run_query("SELECT * FROM menu_item WHERE restaurant_id=? AND id=?",[restaurant_id,menu_id])
    resp = []
    for item in menu_items:
        an_obj = {}
        an_obj['id'] = item[0]
        an_obj['name'] = item[1]
        an_obj['description'] = item[2]
        an_obj['price'] = float(item[3])
        an_obj['image'] = item[4]
        resp.append(an_obj)
    return jsonify(resp), 200


# TODO Restaurant register and login





# Client register, login, logout
# TODO client info UPDATE and account delete

@app.post('/api/client')
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
    


    

    
# @app.patch('/api/client')
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

# Client login/logout endpoint

@app.post('/api/client-login')
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

@app.delete('/api/client-login')
def client_logout():
    params = request.args
    session_token = params.get('token')
    session = run_query("SELECT * FROM client_session WHERE token=?",[session_token])
    if session[0][1]:
        run_query("DELETE FROM client_session WHERE token=?",[session_token])
        return jsonify("Client logged out"),200
    else:
        return jsonify("Error, token not found."),500


# Application launch parameters

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