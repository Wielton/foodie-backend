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
    current_token = params.get('token')
    if not current_token:   # If no session found then return error
        return jsonify("Session token not found!"), 401
    # If valid token then retrieve client info 
    client_info = run_query("SELECT * FROM client LEFT JOIN client_session ON client_session.client_id=client.id WHERE client_session.token=?",[current_token])
    print(client_info)
    # Collect client info in resp list and return to client
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
    if not client_info:
        return jsonify("Server encountered an error. Please try again"),500
    client_id = client_info[0][0]
    # client_username = client_info[0][2]
    # client_password = client_info[0][3]
    # client_first_name = client_info[0][4]
    # client_last_name = client_info[0][5]
    # client_picture_url= client_info[0][7]
    data = request.json
    build_statement = ""
    build_vals = []
    if data.get('username'):
        new_username = data.get('username')
        build_statement+="username=?, "
        build_vals.append(new_username)
        print(build_statement)
    else:
        pass
    if data.get('password'):
        new_password_input = data.get('password')
        new_password = encrypt_password(new_password_input)
        build_statement+="password=?, "
        build_vals.append(new_password)
        print(build_statement)
    else:
        pass
    if data.get('firstName'):
        new_first_name = data.get('firstName')
        build_statement.append("first_name=? ")
        build_vals.append(new_first_name)
    else:
        pass
    if data.get('lastName'):
        new_last_name = data.get('lastName')
        build_statement += "last_name=? "
        build_vals.append(new_last_name)
    else:
        pass
    if data.get('pictureUrl'):
        new_picture_url = data.get('pictureUrl')
        build_statement += "picture_url=? "
        build_vals.append(new_picture_url)
    else:
        pass
    
    # SELECT client session table data and JOIN client table data.  Set client data to variables then use those variables as the old values. 
    # The old value will be used in the UPDATE statement to either keep it or change it depending on client input.
    build_vals.append(client_id)
    statement = str(build_statement)
    print("UPDATE client SET "+statement+" WHERE id=?", build_vals)
    run_query("UPDATE client SET "+statement+" WHERE id=?", build_vals)
    # Create error(500) for the server time out, or another server issue during the update process
    return jsonify("Your info was successfully edited"), 204


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
    return jsonify(""), 204