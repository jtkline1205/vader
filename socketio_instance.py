from flask_socketio import SocketIO, emit

socketio = SocketIO(cors_allowed_origins="http://localhost:3000")

@socketio.on('connect', namespace='/')
def connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/')
def disconnect():
    print('Client disconnected')

@socketio.on('data_changed', namespace = '/')
def handle_data_change():
    emit('data_changed', broadcast=True)