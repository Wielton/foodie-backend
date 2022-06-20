from app import app
from flask import jsonify, request
from helpers.db_helpers import *
import bcrypt
import uuid

def encrypt_password(password):
    salt = bcrypt.gensalt(rounds=5)
    hash_result = bcrypt.hashpw(password.encode(), salt)
    print(hash_result)
    decrypted_password = hash_result.decode()
    return decrypted_password


# Restaurant get, signup and edit

@app.get('/api/restaurant')
def get_restaurants():
    params = request.args
    restaurant_id = params.get('id')
    if restaurant_id:
        restaurant_list = run_query("SELECT * FROM restaurant LEFT JOIN city ON city.id=restaurant.city WHERE id=?", [restaurant_id])
    else:
        restaurant_list = run_query("SELECT * FROM restaurant LEFT JOIN city ON city.id=restaurant.city")
    if not restaurant_list:
        return jsonify("Server encountered an error"), 422
    resp = []
    for item in restaurant_list:
        restaurant = {}
        restaurant['id'] = item[0]
        restaurant['name'] = item[3]
        restaurant['address'] = item[4]
        restaurant['phoneNum'] = item[5]
        restaurant['bio'] = item[6]
        restaurant['profileUrl'] = item[7]
        restaurant['bannerUrl'] = item[8]
        restaurant['city'] = item[11]
        resp.append(restaurant)
    return jsonify(resp), 200

@app.post('/api/restaurant')
def restaurant_register():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify("Email required"), 422
    password_input = data.get('password')
    if not password_input:
        return jsonify("Password required"), 422
    password = encrypt_password(password_input)
    name = data.get('name')
    if not name:
        return jsonify("Name required"), 422
    address = data.get('address')
    if not address:
        return jsonify("Address required"), 422
    phone_num = data.get('phoneNum')
    if not phone_num:
        return jsonify("Phone number required"), 422
    bio = data.get('bio')
    if not bio:
        return jsonify("Bio required"), 422
    profile_url = data.get('profileUrl')
    banner_url = data.get('bannerUrl')
    city_input = data.get('city')
    if not city_input:
        return jsonify("City required"), 422
    city_list = run_query("SELECT * FROM city WHERE name=?", [city_input])
    if not city_list:
        return jsonify("Please select a valid city."), 422
    city_id = city_list[0][0]
    run_query("INSERT INTO restaurant (email, password, name, address, phone_num, bio, profile_url, banner_url, city) VALUES (?,?,?,?,?,?,?,?,?)", [email, password, name, address, phone_num, bio, profile_url, banner_url, city_id])
    restaurant_data = run_query("SELECT * FROM restaurant WHERE email=?", [email])
    if not restaurant_data:
        return jsonify("Server experienced an error."), 500
    restaurant_id = restaurant_data[0][0]
    login_token = str(uuid.uuid4().hex)
    run_query("INSERT INTO restaurant_session (token, restaurant_id) VALUES (?,?)", [login_token, restaurant_id])
    return jsonify("Restaurant successfully created"), 201

@app.patch('/api/restaurant')
def edit_restaurant_profile():
    params = request.args
    restuarant_id = params.get('id')
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    data = request.json
    email = data.get('email')
    name = data.get('name')
    address = data.get('address')
    phone_num = data.get('phoneNum')
    bio = data.get('bio')
    picture_url = data.get('profileUrl')
    banner_url = data.get('bannerUrl')
    city = data.get('city')
    city_list = run_query("SELECT * FROM city WHERE name=?", [city])
    if not city_list:
        return jsonify("City is not valid."), 422
    city_id = city_list[0][0]
    run_query("UPDATE restaurant SET (email, name, address, phone_num, bio, profile_url, banner_url, city) WHERE id=?", [email,name,address, phone_num, bio, picture_url, banner_url, city_id, restuarant_id])
    # Create error(500) for the server time out, or another server issue during the update process
    return jsonify("Your info was successfully edited"), 204