from app import app
from flask import jsonify, request
from helpers.db_helpers import *
import bcrypt
import uuid

# URL : /api/order
#    - The order endpoint allows creating, reading and updating orders. 
#    - Deleting is not allowed. Canceletion of orders is done through PATCH, 
#      leaving cancelled orders in the order history. 
#    - User of request must either be the client that made the order or the restaurant completing the order 



# Clients: GET all orders they made.  Optional arg to get info about specific order 
#
# Restaurants: GET all orders made to them.  Optional arg to get info about specific order

# SUCCESS HTTP CODES: 200, 204
# ERROR HTTP CODES: 401, 422, 500

# An error will be returned if the token is not valid or missing

# Headers: {token : "abcd123"}

# Optional fields: {"orderId" : 5}
# Sample response
# [{
#     "clientId": 5,
#     "createdAt": "2022-04-24 23:29:28",
#     "isCancelled": true,
#     "isComplete": true,
#     "isConfirmed": true,
#     "items": [
#         1, 5, 6
#     ],
#     "orderId": 1,
#     "restaurantId": 3
#     }
# ]


# Client GET
@app.get('/api/order')
def client_order_get():
    return jsonify("Hello"), 200
    
    
    
    
    
# The POST for this endpoint allows creating orders.
# Orders can only contain items from a single restaurant 
# and can only be placed by signed-in clients
# The items in an order are a mandatory field and must be in list form. 
# The list of items corresponds to the menu item IDs
# An error will be returned if the token is not valid or missing
# SUCCESS HTTP CODES: 201
# ERROR HTTP CODES: 401, 422, 500
# Headers: {token : "abcd123"}
# Mandatory fields:
#     {
#         "restaurantId" : 5,
#         "items": [5,6,12]
#     }
# Client POST order
@app.post('/api/order')
def add_to_order():
    params = request.args
    data = request.json
    item = data.get('id')
    session_token = params.get('token')
    session = run_query("SELECT * FROM client_session WHERE token=? AND client_id=?",session_token)
    if not session:
        return jsonify("You must be logged in to place order"), 401
    # I want to get the items' id and restaurant_id from the menu_item table as a list
    # menu_item = run_query("SELECT id, restaurant_id FROM menu_item WHERE id=?", item)
    # Then take that item and ("INSERT INTO order_menu_item) table
    run_query("INSERT INTO order_menu_item (menu_item_id) SELECT id FROM menu_item WHERE menu_item.id=",item)
    # Once the client is finished adding the items, the items are added (as a list)
    # to the orders table ("INSERT INTO ")
    return jsonify("Item added to order"), 201
    

    
# The PATCH for this endpoint allows updating the status of orders 
# Both a client owner of an order and the restaurant can use this endpoint 
# This endpoint DOES NOT allow changing the contents of an order, only the status

# For clients, PATCH allows cancelling existing orders, using the 'cancelOrder' boolean
# For restaurants, PATCH allows confirming and completing orders, using the 'confirmOrder' and 'completeOrder' booleans
# An error will be returned if the token is not valid or missing

# SUCCESS HTTP CODES: 200, 204
# ERROR HTTP CODES: 401, 422, 500

# Headers: {token : "abcd123"}
# Mandatory fields: {"orderId" : 5}
# Optional fields for client: {"cancelOrder" : true}
# Optional fields for restaurant (note that both cannot be used at the same time):
#     {"confirmOrder" : true OR "completeOrder" : true}