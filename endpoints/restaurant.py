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
    restaurant_id = params.get('restaurantId')
    if restaurant_id is None:
        restaurant_list = run_query("SELECT * FROM restaurant JOIN city ON city.id=restaurant.city")
    else:
        restaurant_list = run_query("SELECT * FROM restaurant LEFT JOIN city ON city.id=restaurant.city WHERE restaurant.id=?", [restaurant_id])
    if restaurant_list is not None:
        resp = []
        for item in restaurant_list:
            restaurant = {}
            restaurant['restaurantId'] = item[0]
            restaurant['name'] = item[3]
            restaurant['address'] = item[4]
            restaurant['phoneNum'] = item[5]
            restaurant['bio'] = item[6]
            restaurant['profileUrl'] = item[7]
            restaurant['bannerUrl'] = item[8]
            restaurant['city'] = item[11]
            resp.append(restaurant)
        return jsonify(resp), 200
    else:
        return jsonify("Restaurant not found"), 500

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
    
    # if not phone_num:
    #     return jsonify("Phone number required"), 422
    bio = data.get('bio')
    if not bio:
        return jsonify("Bio required"), 422
    phone_num = data.get('phoneNum')
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
    restaurant_info = {}
    restaurant_info['restaurantId'] = restaurant_id
    restaurant_info['restaurantSessionToken'] = login_token
    return jsonify(restaurant_info)

@app.patch('/api/restaurant')
def edit_restaurant_profile():
    params = request.args
    session_token = params.get('restaurantSessionToken')
    session = run_query("SELECT * FROM restaurant_session WHERE token=?",[session_token])
    if session is not None:
        restaurant_id = session[0][3]
        data = request.json
        build_statement = ""
        # string join
        build_vals = []
        if data.get('password'):
            new_password = data.get('password')
            build_vals.append(new_password)
            build_statement+="password=?"
        else:
            pass
        if data.get('name'):
            new_name = data.get('name')
            build_vals.append(new_name)
            if ("password" in build_statement):
                build_statement+=",name=?"
            else:
                build_statement+="name=?"
        else:
            pass
        if data.get('address'):
            new_address = data.get('address')
            build_vals.append(new_address)
            if ("password" in build_statement) or ("name" in build_statement):
                build_statement+=",address=?"
            else:
                build_statement+="address=?"
        else:
            pass
        if data.get('phoneNum'):
            new_phone_num = data.get('phoneNum')
            build_vals.append(new_phone_num)
            if ("password" in build_statement) or ("name" in build_statement) or ("address" in build_statement):
                build_statement+=",phone_num=?"
            else:
                build_statement+="phone_num=?"
        else:
            pass
        if data.get('bio'):
            new_bio = data.get('bio')
            build_vals.append(new_bio)
            if ("password" in build_statement) or ("name" in build_statement) or ("address" in build_statement) or ("phone_num" in build_statement):
                build_statement+=",bio=?"
            else:
                build_statement+="bio=?"
        else:
            pass
        if data.get('profileUrl'):
            new_profile_url = data.get('profileUrl')
            build_vals.append(new_profile_url)
            if ("password" in build_statement) or ("name" in build_statement) or ("address" in build_statement) or ("phone_num" in build_statement) or ("bio" in build_statement):
                build_statement+=",profile_url=?"
            else:
                build_statement+="profile_url=?"
        else:
            pass
        if data.get('bannerUrl'):
            new_banner_url = data.get('bannerUrl')
            build_vals.append(new_banner_url)
            if ("password" in build_statement) or ("name" in build_statement) or ("address" in build_statement) or ("phone_num" in build_statement) or ("bio" in build_statement) or ("profile_url" in build_statement):
                build_statement+=",banner_url=?"
            else:
                build_statement+="banner_url=?"
        else:
            pass
        if data.get('city'):
            new_city = data.get('city')
            city_list = run_query("SELECT * FROM city WHERE name=?", [new_city])
            if not city_list:
                return jsonify("City is not valid."), 422
            city_id = city_list[0][0]
            build_vals.append(city_id)
            if ("password" in build_statement) or ("name" in build_statement) or ("address" in build_statement) or ("phone_num" in build_statement) or ("bio" in build_statement) or ("profile_url" in build_statement) or ("banner_url" in build_statement):
                build_statement+=",city=?"
            else:
                build_statement+="city=?"
        else:
            pass
        build_vals.append(restaurant_id)
        statement = str(build_statement)
        print(statement)
        run_query("UPDATE restaurant SET "+statement+" WHERE id=?", build_vals)
        # Create error(500) for the server time out, or another server issue during the update process
        return jsonify("Your info was successfully edited"), 204
    else:
        return jsonify("Session token not found!"), 500
    


    