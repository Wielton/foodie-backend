from distutils.command.build_clib import build_clib
from click import pass_obj
from app import app
from flask import jsonify, request
from helpers.db_helpers import *
import bcrypt
import uuid


# Bcrypt password encryption handling

def encrypt_password(password):
    salt = bcrypt.gensalt(rounds=5)
    hash_result = bcrypt.hashpw(password.encode(), salt)
    print(hash_result)
    decrypted_password = hash_result.decode()
    return decrypted_password

# TODO client info UPDATE and account delete
# Response Codes: 
#   1. 200 = Success client creation
#   2. 204 = success with No Content, which would be if nothing was edited in the user profile

# Error Codes: 
#   1. 401 = Access Denied becuase of lack of valid session token
#   2. 422 = Unprocessable because of lacking required info from client 
#   3. 500 = Internal Server Error

# Get client info

@app.get('/api/client')
def get_client_info():
    params = request.args
    # Check for valid session token
    current_token = params.get('sessionToken')
    if current_token is None:   # If no session found then return error
        return jsonify("Session token not found!"), 401
    # If valid token then retrieve client info 
    client_info = run_query("SELECT * FROM client LEFT JOIN client_session ON client_session.client_id=client.id WHERE client_session.token=?",[current_token])
    if client_info is not None:
        print(client_info)
        # Collect client info in resp list and return to client
        resp = []
        for item in client_info:
            client = {}
            client['clientId'] = item[0]
            client['email'] = item[1]
            client['username'] = item[2]
            client['firstName'] = item[4]
            client['lastName'] = item[5]
            client['createdAt'] = item[6]
            client['pictureUrl'] = item[7]
            resp.append(client)
        return jsonify(resp), 200
    else:
        return jsonify("No session found"), 500


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
    login_token = str(uuid.uuid4().hex)
    client_id = client_data[0][0]
    run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [login_token, client_id])
    return jsonify('Client account created successfully.'),201  # Client redirected to logged-in restaurant list


@app.patch('/api/client')
def edit_profile():
    # GET params for session check
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    client_info = run_query("SELECT * FROM client JOIN client_session ON client_session.client_id=client.id WHERE token=?",[session_token])
    if client_info is not None:
        client_id = client_info[0][0]
        data = request.json
        build_statement = ""
        # string join
        build_vals = []
        if data.get('username'):
            new_username = data.get('username')
            build_vals.append(new_username)
            build_statement+="username=?"
        else:
            pass
        if data.get('password'):
            new_password_input = data.get('password')
            new_password = encrypt_password(new_password_input)
            build_vals.append(new_password)
            if ("username" in build_statement):
                build_statement+=",password=?"
            else:
                build_statement+="password=?"
        else:
            pass
        if data.get('firstName'):
            new_first_name = data.get('firstName')
            build_vals.append(new_first_name)
            if ("username" in build_statement) or ("password" in build_statement):
                build_statement+=",first_name=?"
            else:
                build_statement+="first_name=?"
        else:
            pass
        if data.get('lastName'):
            new_last_name = data.get('lastName')
            build_vals.append(new_last_name)
            if ("username" in build_statement) or ("password" in build_statement) or ("first_name" in build_statement):
                build_statement+=",last_name=?"
            else:
                build_statement+="last_name=?"
        else:
            pass
        if data.get('pictureUrl'):
            new_picture_url = data.get('pictureUrl')
            build_vals.append(new_picture_url)
            if ("username" in build_statement) or ("password" in build_statement) or ("first_name" in build_statement) or ("last_name" in build_statement):
                build_statement+=",picture_url=?"
            else:
                build_statement+="picture_url=?"
        else:
            pass
        build_vals.append(client_id)
        statement = str(build_statement)
        run_query("UPDATE client SET "+statement+" WHERE id=?", build_vals)
        # Create error(500) for the server time out, or another server issue during the update process
        return jsonify("Your info was successfully edited"), 204
    else:
        return jsonify("Session not found"), 500

@app.delete('/api/client')
def delete_account():
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    session = run_query("SELECT * FROM client_session WHERE token=?",[session_token])
    if session is not None:
        user_id = session[0][3]
        run_query("DELETE FROM client_session WHERE token=?",[session_token])
        run_query("DELETE FROM client WHERE id=?",[user_id])
        return jsonify("Account deleted"), 204
    else:
        return jsonify("You must be logged in to delete your account"), 500