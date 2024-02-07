from flask import Flask
from flask_cors import CORS
from app.socketio_instance import socketio
from app.routes.chip_routes import chip_bp
from app.routes.bill_routes import bill_bp
from app.routes.button_routes import button_bp
from app.routes.other_routes import other_bp

import logging

app = Flask(__name__)
app.register_blueprint(chip_bp)
app.register_blueprint(bill_bp)
app.register_blueprint(button_bp)
app.register_blueprint(other_bp)

socketio.init_app(app)
CORS(app, origins="http://192.168.1.203:3000")  # Allow connections from http://localhost:3000
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)    

if __name__ == '__main__':
    socketio.run(app, host='192.168.1.203', port=5000)
