from flask import Flask, request, jsonify, session, redirect, url_for
from helpers.db_helpers import *
import sys

app = Flask(__name__)

# This is the features section with an api to users, 
# where seperate tables are utilized: users, user_posts.

# @app.get('/login')
# def login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
#     user = run_query("SELECT id,username FROM users WHERE username=? AND password=?", [username,password])
#     if user:
#         session['loggedIn']=True
#         session['username']=user[0][1]
#         session['userId']=user[0][0]
#         return jsonify(session),201
#     else:
#         return jsonify("Missing required argument 'Username'"), 422

# @app.post('/login')
# def signup():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
#     run_query("INSERT INTO users (username,password) VALUES (?,?)",[username,password])
#     session['loggedIn']=True
#     return jsonify(session),201
    
# @app.route('/logout')
# def logout():
#     session.pop('loggedIn', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))

# @app.route('/user')
# def create_post():
#     user = session

# @app.post('/api/posts')
# def create_post():
#     data = request.json
#     post = data.get('post')
#     user_id = session['userId']
#     if not user_id:
#         return jsonify("You must be logged in to make a post.")
#     else:
#         run_query("INSERT INTO posts (post,post_user_id) VALUES (?)", [post,user_id])
#         return jsonify("Post created successfully!")


# Basic requirements satisfied.  
@app.get('/api/restaurants')
def get_restaurants():
    # TODO: db SELECT
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

# @app.get('/api/client')
# def client_login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
#     if not username:
#         return jsonify("Missing required field"), 422
#     if not password:
#         return jsonify("Missing required field"), 422
#     client_id = run_query("SELECT id FROM client WHERE username=? AND password=?", [username,password])
#     login_token = {"token" : "tH1suN1qu3unmb3r"}
#     run_query("INSERT INTO client_session SET (token=?,client_id=?)",[login_token,client_id])
#     return jsonify(login_token),200
    
@app.post('/api/client')
def client_register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    password = data.get('password')
    picture_url = data.get('pictureUrl')
    # if not email:
    #     return jsonify("Missing required argument 'Email'"), 422
    # if not username:
    #     return jsonify("Missing required argument 'Username'"), 422
    # if not first_name:
    #     return jsonify("Missing required argument 'First Name'"), 422
    # if not last_name:
    #     return jsonify("Missing required argument 'Last Name'"), 422
    # if not password:
    #     return jsonify("Missing required argument 'Password'"), 422
    # TODO: Error checking the actual values for the arguments
    run_query("INSERT INTO client (email, username, password, first_name, last_name, picture_url) VALUES (?,?,?,?,?,?)", [email, username, password, first_name, last_name, picture_url])
    client_data = run_query("SELECT * FROM client WHERE username=? AND password=?", [username,password])
    if client_data:
        clientId = client_data[0][0]
        loginToken = "tH1suN1qu3unmb3r"
        run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [loginToken,clientId])
        return jsonify(clientId),201
    else:
        return jsonify("Error occurred"),

    
@app.put('/api/posts')
def edit_post():
    params = request.args
    post_id = params.get('id')
    data = request.json
    post_content = data.get('post')
    run_query("UPDATE user_posts SET post = ? WHERE id=?", [post_content, post_id])
    return jsonify("Your post was successfully edited"), 200

@app.delete('/api/posts')
def delete_post():
    params = request.args
    user_id = params.get('id')
    run_query("DELETE FROM user_posts WHERE id=?",[user_id])
    return jsonify("Post deleted"),200



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