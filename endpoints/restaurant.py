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
    restaurant_list = run_query("SELECT * FROM restaurant LEFT JOIN city ON city.id=restaurant.city")
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
        run_query("INSERT INTO restaurant (email, password, name, address, phone_num, bio, profile_url, banner_url, city) VALUES (?,?,?,?,?,?,?,?,?)", [email, password, name, address, phone_num, bio, profile_url, banner_url, city_id])
        print("Restaurant registered")
    restaurant_data = run_query("SELECT * FROM restaurant WHERE email=?", [email])
    print(restaurant_data[0])
    login_token = uuid.uuid4()
    restaurant = {}
    restaurant['id'] = restaurant_data[0][0]
    restaurant['name'] = restaurant_data[0][3]
    restaurant['token'] = login_token
    restaurant_id = restaurant_data[0][0]
    run_query("INSERT INTO restaurant_session (token, restaurant_id) VALUES (?,?)", [login_token, restaurant_id])
    print(jsonify(restaurant))
    return jsonify(restaurant),201