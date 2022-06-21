from app import app
from flask import jsonify, request
from helpers.db_helpers import *




# Create menu items

@app.post('/api/menu')
def create_menu_item():
    params = request.args
    data = request.json
    login_token = params.get('token')
    if not login_token:
        return jsonify("You must be logged in to create a new menu item"), 401
    restaurant_id = params.get('id')
    current_token = run_query("SELECT * FROM restaurant_session WHERE token=?",[login_token])
    if login_token != current_token:    
        return jsonify("Error, you need to be signed in to create a menu item"),403
    else:
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        image_url = data.get('imageUrl')
        run_query("INSERT INTO menu_item (name, description, price, image_url, restaurant_id) VALUES (?,?,?,?,?)",[name, description, price, image_url, restaurant_id])
        print("The item was added successfully")
    return jsonify("Complete")


# Get menu items
# SUCCESS HTTP CODE: 200
# ERROR HTTP CODES: 401, 422

@app.get('/api/menu')
def get_menu_item():
    params = request.args
    restaurant_id = params.get('restaurantId')
    menu_id = params.get('menuId')
    # Got parameters
    # If no parameters and client wants to search menu items:
    if not restaurant_id and not menu_id:
        # Get all menu items and restaurant name from menu_item table 
        menu_items = run_query("SELECT *, restaurant.name FROM menu_item JOIN restaurant ON restaurant_id=restaurant.id")
        # Build the menu items list with restaurant name joined
        resp = []
        for item in menu_items:
            an_obj = {} 
            an_obj['id'] = item[0]
            an_obj['name'] = item[1]
            an_obj['description'] = item[2]
            an_obj['price'] = float(item[3])
            an_obj['image'] = item[4]
            an_obj['restaurantName'] = item[9]
            # Fetch cities, find the matching id's, then add to city name to corresponding restaurant in menu items list
            cities = run_query("SELECT * FROM city")
            for city in cities:
                    if city[0] == item[15]:
                        an_obj['city'] = city[1]
            resp.append(an_obj)        
        print(resp)
        return jsonify(resp), 200
    # If client clicks on a specific restaurant, their corresponding menu will populate then handle response same as above
    elif restaurant_id and not menu_id:
        menu_items = run_query("SELECT * FROM menu_item WHERE restaurant_id=?",[restaurant_id])
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
    # This will fetch the specific menu item from its restaurant
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

@app.patch('/api/menu')
def edit_menu():
    params = request.args
    menu_id= params.get('menuId')
    session_token = params.get('token')
    restaurant_id = params.get('restaurantId')
    logged_in = run_query("SELECT * FROM restaurant_session WHERE token=? AND restaurant_id=?",[session_token,restaurant_id])
    if not logged_in:
        return jsonify("You must be logged in to create a new menu item"), 401
    data = request.json
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    image = data.get('imageUrl')
    run_query("UPDATE menu_item SET (name=?, description=?, price=?, image_url=?) WHERE id=? AND restaurant_id=?",[name, description, price, image, menu_id,restaurant_id])
    return jsonify(""), 204
    

# Delete menu item
@app.delete('/api/menu')
def delete_menu_item():
    params = request.args
    session_token = params.get('token')
    menu_id = params.get('menuId')
    restaurant_id = params.get('restaurantId')
    logged_in = run_query("SELECT * FROM restaurant_session WHERE token=? AND restaurant_id=?",[session_token,restaurant_id])
    if not logged_in:
        return jsonify("You must be logged in to delete menu item"), 401
    run_query("DELETE FROM menu_item WHERE id=? AND restaurant_id=?",[menu_id,restaurant_id])
    return jsonify(""), 204
    
        