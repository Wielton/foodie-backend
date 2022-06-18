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

    
# Client register, login, logout
# TODO client info UPDATE and account delete
# Response Codes: 
#   1. 200 = Success client creation
#   2. 204 = success with No Content, which would be if nothing was edited in the user profile
# 
# Error Codes: 
#   1. 401 = Access Denied becuase of lack of valid session token
#   2. 422 = Unprocessable because of lacking required info from client 
#   3. 500 = Internal Server Error


@app.get('/api/client')
def get_client_info():
    params = request.args
    current_token = params.get('token')
    if not current_token:
        return jsonify("Session token not found!"), 401
    client_info = run_query("SELECT * FROM client LEFT JOIN client_session ON client_session.client_id=client.id WHERE client_session.token=?",[current_token])
    print(client_info)
    resp = []
    for item in client_info:
        client = {}
        client['id'] = item[0]
        client['email'] = item[1]
        client['username'] = item[2]
        client['firstName'] = item[4]
        client['lastName'] = item[5]
        client['createdAt'] = item[6]
        client['pictureUrl'] = item[7]
        resp.append(client)
    return jsonify(resp), 200


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
    if not email:
        return jsonify("Email required"), 422
    if not username:
        return jsonify("Username required"), 422
    if not first_name:
        return jsonify("First Name required"), 422
    if not last_name:
        return jsonify("Last name required"), 422
    if not password_input:
        return jsonify("Password required"), 422
    run_query("INSERT INTO client (email, username, password, first_name, last_name, picture_url) VALUES (?,?,?,?,?,?)", [email, username, password, first_name, last_name, picture_url])
    client_data = run_query("SELECT * FROM client WHERE username=?", [username])
    login_token = uuid.uuid4()
    client_id = client_data[0][0]
    client = {}
    client['id'] = client_data[0][0]
    client['username'] = client_data[0][2]
    client['token'] = login_token
    run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [login_token, client_id])
    return jsonify(''),201


@app.patch('/api/client')
def edit_profile():
    params = request.args
    session_token = params.get('token')
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    picture_url = data.get('pictureUrl')
    if not session_token:
        return jsonify("Session token not found!"), 401
    user_data = run_query("SELECT client_id FROM client_session WHERE token=?",[session_token])
    if not user_data:
        return jsonify("Server encountered an error. Please try again"),500
    user_id = user_data[0][0]
    run_query("UPDATE client SET (email, username, password, first_name, last_name, picture_url) WHERE id=?", [email,username,password,first_name, last_name, picture_url, user_id])
    # Create error(500) for the server time out, or another server issue during the update process
    return jsonify("Your info was successfully edited"), 200


@app.delete('/api/client')
def delete_account():
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    session = run_query("SELECT * FROM client_session WHERE token=?",[session_token])
    user_id = session[0][3]
    run_query("DELETE FROM client_session WHERE token=?",[session_token])
    run_query("DELETE FROM client WHERE id=?",[user_id])
    return jsonify(""), 201