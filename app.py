import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Разрешает браузеру отправлять запросы на этот сервер

# Переменная для хранения текущей пары в памяти сервера
current_data = {"pair": "Ожидание..."}

@app.route('/set_pair', methods=['POST'])
def set_pair():
    data = request.get_json()
    if data and 'pair' in data:
        current_data['pair'] = data['pair']
        return jsonify({"status": "success", "pair": current_data['pair']}), 200
    return jsonify({"status": "error"}), 400

@app.route('/get_pair', methods=['GET'])
def get_pair():
    return jsonify(current_data), 200

if __name__ == '__main__':
    # Порт, который автоматически выдаст Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
