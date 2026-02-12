from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'meme-reactor-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@app.route('/')
def index():
    return "🚀 MemeReactor Server is running!"

@socketio.on('connect')
def handle_connect():
    print(f'✅ Client connected: {request.sid}')

@socketio.on('create_room')
def handle_create_room():
    room_id = datetime.now().strftime('%H%M%S')
    rooms[room_id] = {
        'host': request.sid,
        'users': [request.sid]
    }
    join_room(room_id)
    emit('room_created', {'room_id': room_id})
    print(f'🎮 Room created: {room_id}')

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        join_room(room_id)
        rooms[room_id]['users'].append(request.sid)
        emit('room_joined', {'success': True, 'room_id': room_id})
        print(f'🔗 User joined room: {room_id}')
    else:
        emit('room_joined', {'success': False})
        print(f'❌ Room not found: {room_id}')

@socketio.on('send_meme')
def handle_send_meme(data):
    room_id = data.get('room_id')
    meme_data = data.get('meme_data')
    if room_id in rooms:
        emit('new_meme', {'meme_data': meme_data}, room=room_id, skip_sid=request.sid)
        print(f'🎨 Meme sent to room: {room_id}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)