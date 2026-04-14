# mini_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    print("Health called")
    return jsonify({'status': 'ok'})

@app.route('/api/polling/register_player', methods=['POST'])
def register():
    print("=" * 50)
    print("REGISTER PLAYER CALLED!")
    print(f"Headers: {dict(request.headers)}")
    print(f"Data: {request.json}")
    print("=" * 50)
    return jsonify({'status': 'ok', 'message': 'Registered'})

@app.route('/api/polling/send_chat', methods=['POST'])
def send_chat():
    print("SEND CHAT CALLED!")
    return jsonify({'status': 'ok'})

@app.route('/api/polling/messages', methods=['GET'])
def messages():
    print("GET MESSAGES CALLED!")
    return jsonify([])

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("MINI TEST SERVER STARTED")
    print("=" * 50)
    print("\nRoutes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    print("\n" + "=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)