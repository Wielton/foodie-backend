from app import app
from flask import jsonify, request
from helpers.db_helpers import *

# Create menu items

@app.post('/api/menu')
def create_menu_item():
    params = request.args
    data = request.json
    login_token = params.get('token')
    restaurant_id = params.get('id')
    current_token = run_query("SELECT * FROM restaurant_session WHERE token=?",[login_token])
    if login_token != current_token:    
        return jsonify("Error, you need to be signed in to create a menu item"),403
    else:
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        image_url = data.get('image_url')
        run_query("INSERT INTO menu_item (name, description, price, image_url, restaurant_id) VALUES (?,?,?,?,?)",[name, description, price, image_url, restaurant_id])
        print("The item was added successfully")
    return jsonify("Complete")

# Get menu items

@app.get('/api/menu')
def get_menu_item():
    params = request.args
    restaurant_id = params.get('restaurantId')
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

# Edit menu item

app.post

# Delete menu item