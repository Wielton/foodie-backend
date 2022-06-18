from flask import Flask

app = Flask(__name__)

from endpoints import client, client_login, restaurant, restaurant_login, menu, order