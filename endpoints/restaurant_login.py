from app import app
from flask import jsonify, request
from helpers.db_helpers import *
import bcrypt
import uuid



# Restaurant login/logout endpoint

@app.post('/api/restaurant-login')
def restaurant_login():
    data = request.json
    email = data.get('email')
    password_input = data.get('password')
    if not email:
        return jsonify("Email required"), 422
    if not password_input:
        return jsonify("Password required"), 422
    restaurant_info = run_query("SELECT * FROM restaurant WHERE email=?", [email])
    if not restaurant_info:
        return jsonify("Server encountered an error. Please try again"),500
    restaurant_password = restaurant_info[0][2]
    if not bcrypt.checkpw(password_input.encode(), restaurant_password.encode()):
        return jsonify("Credentials don't match"),401
    restaurant_id = restaurant_info[0][0]
    login_token = str(uuid.uuid4().hex)
    logged_in = run_query("SELECT * FROM restaurant_session WHERE restaurant_id=?",[restaurant_id])
    if not logged_in:
        run_query("INSERT INTO restaurant_session (token,restaurant_id) VALUES (?,?)", [login_token,restaurant_id])
    elif restaurant_id == logged_in[0][3]:
        # I could UPDATE here but I chose to delete then create a new session instance as I figured this is a better thing to do because of token lifecycles and other errors that could occur from just updating one column
        run_query("DELETE FROM restaurant_session WHERE restaurant_id=?",[restaurant_id])
        run_query("INSERT INTO restaurant_session (token,restaurant_id) VALUES (?,?)", [login_token,restaurant_id])
    return jsonify("Successfully logged in"),201


@app.delete('/api/restaurant-login')
def restaurant_logout():
    params = request.args
    session_token = params.get('token')
    if session_token is not None:
        session = run_query("SELECT * FROM restaurant_session WHERE token=?",[session_token])
        if session is not None:
            run_query("DELETE FROM restaurant_session WHERE token=?",[session_token])
            return jsonify("Logged out"),204
        else:
            return jsonify("Failed to logout, please try again"), 500
    else:
        return jsonify("Session not found"), 500