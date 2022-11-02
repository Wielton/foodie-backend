from app import app
from flask import jsonify, request
from helpers.db_helpers import *


# Client GET
@app.get('/api/order-items')
def get_order_items():
    params = request.args
    if params.get('sessionToken'):
        session_token = params.get('sessionToken')
        session = run_query("SELECT client_id FROM client_session WHERE token=?",[session_token])
        if session is not None:
            client_id = session[0][0]
            resp = []
            # Get the orderId, restaurant name, and time created.
            all_order_items = run_query("SELECT order_menu_item.menu_item_id, menu_item.* FROM order_menu_item RIGHT JOIN menu_item ON order_menu_item.menu_item_id=menu_item.id WHERE client_id=?",[client_id])
            for orders in all_orders:
                order = {}
                order['orderId'] = orders[0]
                order['createdAt'] = orders[1]
                order['restaurantName'] = orders[7]
                if orders[2] is 1:
                    order['isConfirmed'] = orders[2]
                elif orders[3] is 1:
                    order['isCompleted'] = orders[3]
                elif orders[4] is 1:
                    order['isCancelled'] = orders[4]
                resp.append(order)
    else:
        restaurant_session_token = params.get('restaurantSessionToken')
        session = run_query("SELECT restaurant_id FROM restaurant_session WHERE token=?",[restaurant_session_token])
        if session is None:
            return jsonify("You must be logged in")
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