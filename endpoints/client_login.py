from app import app
from flask import jsonify, request
from helpers.db_helpers import *
import bcrypt
import uuid



# Client login/logout endpoint

@app.post('/api/client-login')
def client_login():
    data = request.json
    email_input = data.get('email')
    password_input = data.get('password')
    if not email_input:
        return jsonify("Email required"), 422
    if not password_input:
        return jsonify("Password required"), 422
    client_info = run_query("SELECT * FROM client WHERE email=?", [email_input])
    if client_info is not None:
        client_password = client_info[0][3]
        if not bcrypt.checkpw(password_input.encode(), client_password.encode()):
            return jsonify("Error"),401
        client_id = client_info[0][0]
        login_token = str(uuid.uuid4().hex)
        print(login_token)
        logged_in = run_query("SELECT * FROM client_session WHERE client_id=?",[client_id])
        if not logged_in:
            run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [login_token,client_id])
        elif client_id == logged_in[0][3]:
            # I could UPDATE here but I chose to delete then create a new session instance as I figured this is a better thing to do because of token lifecycles and other errors that could occur from just updating one column
            run_query("DELETE FROM client_session WHERE client_id=?",[client_id])
            run_query("INSERT INTO client_session (token,client_id) VALUES (?,?)", [login_token,client_id])
        return jsonify("Client signed in"),201
    else:
        return jsonify("Email not found.  PLease try again"), 500


@app.delete('/api/client-login')
def client_logout():
    params = request.args
    session_token = params.get('token')
    session = run_query("SELECT * FROM client_session WHERE token=?",[session_token])
    if session is not None:
        run_query("DELETE FROM client_session WHERE token=?",[session_token])
        return jsonify("Client logged out"),204
    else:
        return jsonify("You must be logged in to delete your account."), 500