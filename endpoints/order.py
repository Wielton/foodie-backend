from app import app
from flask import jsonify, request
from helpers.db_helpers import *

# URL : /api/order
#    - The order endpoint allows creating, reading and updating orders. 
#    - Deleting is not allowed. Canceletion of orders is done through PATCH, 
#      leaving cancelled orders in the order history. 
#    - User of request must either be the client that made the order or the restaurant completing the order 

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
def get_order():
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 422
    # Clients: GET all orders they made.  Optional arg to get info about specific order 
    session = run_query("SELECT client_id FROM client_session WHERE token=?",[session_token])
    if session is not None:
        client_id = session[0][0]
        resp = []
        all_orders = run_query("SELECT orders.id,orders.created_at,restaurant.name FROM orders JOIN restaurant ON restaurant.id=orders.restaurant_id WHERE client_id=?",[client_id])
        for orders in all_orders:
            order = {}
            order['id'] = orders[0]
            order['createdAt'] = orders[1]
            order['restaurantName'] = orders[2]
            resp.append(order)
    else:
        session = run_query("SELECT restaurant_id FROM restaurant_session WHERE token=?",[session_token])
        if session is not None:
            restaurant_id = session[0][0]
            all_orders = run_query("SELECT * FROM orders WHERE restaurant_id=?",[restaurant_id])
            print(all_orders)
            # items_list = run_query("SELECT menu_item_id FROM order_menu_item")
            resp = []
            for orders in all_orders:
                # order_items = int(order_items_str)
                # print(order_items)
                # - The result is returning an INT 
                #    but I need to convert that into a string reading: "true" or "false" 
                # - I need to group the result into the same order and get the items
                print(orders)
                order = {}
                order['orderId'] = orders[0]
                order['createdAt'] = orders[1]
                is_confirmed = str(orders[2])
                is_completed = str(orders[3])
                is_cancelled = str(orders[4])
                if is_confirmed == "0" or is_completed == "0" or is_cancelled == "0":
                    is_confirmed = "false"
                    is_completed = "false"
                    is_cancelled = "false"
                else:
                    is_confirmed = "true"
                    is_completed = "true"
                    is_cancelled = "true"
                order['isConfirmed'] = is_confirmed
                order['isCompleted'] = is_completed
                order['isCancelled'] = is_cancelled
                order['clientId'] = orders[5]
                order['restaurantId'] = orders[6]
                order_items = run_query("SELECT menu_item_id FROM order_menu_item WHERE order_id=?",[orders[0]])
                print(order_items)
                item_list = []
                if order_items is not None:
                    for item in order_items:
                        item_list.append(item)
                order['items'] = order_items
                resp.append(order)
            # for item in all_items:
            #     print(item)
            # order['items'] = item_list
            
        # item_list = run_query("SELECT menu_item_id FROM order_menu_item WHERE order_id=",[orders_id])
        # print(item_list)
    return jsonify(resp), 200
            
    # # Collect client info in resp list and return to client
    #     for orders in order_info:
    #         order = {}
    #         order['orderId'] = orders[0]
    #         order['createdAt'] = orders[1]
    #         order['menuItemId'] = orders[2]
    #         order['itemName'] = orders[3]
    #         order['itemPrice'] = orders[4]
    #         order['restaurantName'] = orders[4]

    
    
    
    
    
    
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
def post_order():
    # - A list of order items[(menuId's)] from a client(clientId), from one restaurant(restaurantId) 
    #   will be received from frontend
    # - The order needs to be created first, with the clientId and restaurantId, for an orders.id 
    # - Each item in the items[] needs to be extracted and inserted into the order_menu_item table
    #   using the menu_item.id and corresponding orders.id where the restaurant_id is matching
    # - Once all the items have been placed into the order_menu_item, 
    #   the order is then confirmed.
    params = request.args
    data = request.json
    menu_items = data.get('items')
    restaurant_id = data.get('restaurantId')
    # restaurant_id = data.get('restaurantId')
    session_token = params.get('token')
    current_session = run_query("SELECT client_id FROM client_session WHERE token=?",[session_token])
    if current_session is not None:
        # Create the order in the orders table with client_id and restaurant_id and use id for order_menu_item
        # Use cursor.lastRowId() to extract the most recent row created from the search parameters
        client_id = current_session[0][0]
        run_query("INSERT INTO orders (client_id,restaurant_id) VALUES (?,?)", [client_id,restaurant_id])
        menu_id = run_query("SELECT id FROM orders WHERE client_id=? AND restaurant_id=?",[client_id,restaurant_id])
        menu_item_id = menu_id[0][0]
        # - Now the items can be individually inserted into the order_menu_item table along with the orders.id 
        # - Optimize by taking each item, attaching the corresponding orders.id, then insert as one query.
        #    instead of the below solution which could potentially encounter partial errors being 
        #    fulfilled because of a missing menu item id
        for item in menu_items:
            run_query("INSERT INTO order_menu_item (menu_item_id,order_id) VALUES (?,?)",[item,menu_item_id])
            print(item)
        # First thing I need to do is create an order in the order table using the menu_item.id a
        # I want to get the id and restaurant_id from the menu_item table as a list
        # menu_item = run_query("SELECT id, restaurant_id FROM menu_item WHERE id=?", item)
        # Then take that item and ("INSERT INTO order_menu_item) table
        # run_query("SELECT menu_item.id, orders.id INTO order_menu_item FROM orders RIGHT JOIN menu_item ON menu_item.restaurant_id=orders.restaurant_id WHERE restaurant.id=?",restaurant_id)
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

@app.patch('/api/order')
def handle_order():
    # GET params for session check and data for order id
    params = request.args
    data = request.json
    order_id = data.get('orderId')
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 422
    if data.get('cancelOrder'):
        client_info = run_query("SELECT * FROM client_session WHERE token=?",[session_token])
        if not client_info:
            return jsonify("Please sign in"),401
        else:
            client_id = client_info[0][3]
            order_status = run_query("SELECT * FROM orders WHERE id=? AND client_id=?",[order_id,client_id])
            print(order_status)
            if (order_status[0][2] == 0) and (order_status[0][3] == 0) and (order_status[0][4] == 0):
                run_query("UPDATE orders SET is_cancelled=1 WHERE id=? AND client_id=?",[order_id,client_id])
                # run_query("UPDATE orders SET is_cancelled=1 WHERE id=? AND client_id=?",[order_id,client_id])
                return jsonify("Your order has been cancelled"), 204
            elif (order_status[0][2] == 1):
                return jsonify("Order already confirmed and can no longer be processed"), 500
            elif (order_status[0][3] == 1):
                return jsonify("Order already complete and in delivery"), 500
    else:   
        restaurant_info = run_query("SELECT * FROM restaurant_session WHERE token=?",[session_token])
        if not restaurant_info:
            return jsonify("Session not valid, please sign back in"),401
        else:
            restaurant_id = restaurant_info[0][3]
            order_status = run_query("SELECT * FROM orders WHERE id=? AND restaurant_id=?",[order_id,restaurant_id])
            if (order_status[0][4] == 1):
                return jsonify("Order has been cancelled"), 500
            else:
                if data.get('confirmOrder'):
                    run_query("UPDATE orders SET is_confirmed=1 WHERE id=? AND restaurant_id=?",[order_id,restaurant_id])
                    return jsonify("Order is confirmed"), 204
                elif data.get('completeOrder'):
                    run_query("UPDATE orders SET is_completed=1 WHERE id=? AND restaurant_id=?",[order_id,restaurant_id])
                    run_query("UPDATE orders SET is_confirmed=0 WHERE id=? AND restaurant_id=?",[order_id,restaurant_id])
                    return jsonify("Order is complete"), 204
    # Create error(500) for the server time out, or another server issue during the update process