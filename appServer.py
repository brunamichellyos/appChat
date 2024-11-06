from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

users = {}  # Dicionário para manter o controle dos usuários conectados

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    users[request.sid] = username  # Armazena o usuário na sessão atual

    # Atualiza a lista de usuários para todos
    emit('user_list', list(users.values()), broadcast=True)

    # Emite uma mensagem de entrada com o formato esperado pelo cliente
    emit('message', {'sender': 'Sistema', 'message': f"{username} entrou no chat.", 'isPrivate': False}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    username = users.get(request.sid, "Anônimo")
    # Envia a mensagem para todos os usuários no formato correto
    emit('message', {'sender': username, 'message': data, 'isPrivate': False}, broadcast=True)

@socketio.on('private_message')
def handle_private_message(data):
    sender = users.get(request.sid, "Anônimo")
    recipient_name = data['to']
    message = data['message']
    
    # Encontrar o ID do destinatário
    recipient_sid = None
    for sid, name in users.items():
        if name == recipient_name:
            recipient_sid = sid
            break

    if recipient_sid:
        # Envia a mensagem privada para o destinatário e para o remetente no formato correto
        emit('message', {'sender': sender, 'message': message, 'isPrivate': True}, room=recipient_sid)
        emit('message', {'sender': sender, 'message': f"[Você]: {message}", 'isPrivate': True}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    username = users.pop(request.sid, "Anônimo")
    # Envia uma mensagem de saída com o formato correto
    emit('message', {'sender': 'Sistema', 'message': f"{username} saiu do chat.", 'isPrivate': False}, broadcast=True)
    emit('user_list', list(users.values()), broadcast=True)  # Atualiza a lista de usuários para todos

if __name__ == '__main__':
    # Definindo IP e porta para a aplicação
    socketio.run(app, host='192.168.8.39', port=5000)