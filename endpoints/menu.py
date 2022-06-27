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
    session = run_query("SELECT * FROM restaurant_session WHERE token=?",[login_token])
    if session is not None:    
        restaurant_id = session[0][3]
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        image_url = data.get('imageUrl')
        if not name:
            return jsonify("Item namerequired"), 422
        if not description:
            return jsonify("Item description required"), 422
        if not price:
            return jsonify("Item price required"), 422
        run_query("INSERT INTO menu_item (name, description, price, image_url, restaurant_id) VALUES (?,?,?,?,?)",[name, description, price, image_url, restaurant_id])
        return jsonify("Menu item successfully created"), 204
    else:
        return jsonify("You must be logged in to create a new menu item"), 500


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
    session_token = params.get('token')
    session = run_query("SELECT * FROM restaurant_session WHERE token=?",[session_token])
    if session is not None:
        data = request.json
        menu_id = params.get('menuId')
        build_statement = ""
        # string join
        build_vals = []
        if data.get('name'):
            new_name = data.get('name')
            build_vals.append(new_name)
            build_statement+="name=?"
        else:
            pass
        if data.get('description'):
            new_description = data.get('description')
            build_vals.append(new_description)
            if ("name" in build_statement):
                build_statement+=",description=?"
            else:
                build_statement+="description=?"
        else:
            pass
        if data.get('price'):
            new_price = data.get('price')
            build_vals.append(new_price)
            if ("name" in build_statement) or ("description" in build_statement):
                build_statement+=",price=?"
            else:
                build_statement+="price=?"
        else:
            pass
        if data.get('imageUrl'):
            new_image = data.get('imageUrl')
            build_vals.append(new_image)
            if ("name" in build_statement) or ("description" in build_statement) or ("price" in build_statement):
                build_statement+=",image_url=?"
            else:
                build_statement+="image_url=?"
        else:
            pass
        build_vals.append(menu_id)
        statement = str(build_statement)
        print(statement)
        run_query("UPDATE menu_item SET "+statement+" WHERE id=?", build_vals)
        # Create error(500) for the server time out, or another server issue during the update process
        return jsonify("Item has been successfully edited"), 204
    else:
        return jsonify("You must be logged in to edit menu item"), 401

# client_info = run_query("SELECT * FROM client JOIN client_session ON client_session.client_id=client.id WHERE token=?",[session_token])
#     if not client_info:
#         return jsonify("Server encountered an error. Please try again"),500
#     client_id = client_info[0][0]
#     data = request.json
#     
#     return jsonify("Your info was successfully edited"), 204
    

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
    
        