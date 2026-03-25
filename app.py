from flask import Flask, jsonify, request, send_file
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
import pandas as pd
import io
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config["MONGO_URI"] = "mongodb+srv://usuario_web:FEh8oeAhmoSPFqhn@stockescalu.mikltkh.mongodb.net/ESCALU_DB?retryWrites=true&w=majority&authSource=admin"
mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor ESCALU OK"

# --- RUTAS DE STOCK ---

@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    productos = list(mongo.db.stock.find({"seccion": seccion}))
    for p in productos:
        p['_id'] = str(p['_id'])
    return jsonify(productos)

@app.route('/stock/agregar', methods=['POST'])
def add_product():
    data = request.json
    mongo.db.stock.insert_one(data)
    return jsonify({"msg": "OK"})

@app.route('/stock/vender/<id>', methods=['PUT'])
def update_stock(id):
    vendido = request.args.get('vendido')
    recep = request.args.get('recepcionadas')
    update_data = {}
    if vendido is not None:
        update_data["vendido"] = int(vendido)
    if recep is not None:
        update_data["recepcionadas"] = int(recep)
    mongo.db.stock.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return jsonify({"msg": "OK"})

@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def delete_product(id):
    mongo.db.stock.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "OK"})

@app.route('/stock/descargar', methods=['GET'])
def descargar_excel():
    productos = list(mongo.db.stock.find({}, {"_id": 0}))
    df = pd.DataFrame(productos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Stock')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='Stock_Real.xlsx')

# --- RUTAS DE PEDIDOS ---

@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    # Solo devolvemos los pedidos que NO están finalizados
    pedidos = list(mongo.db.pedidos.find({"estado": {"$ne": "finalizado"}}))
    for p in pedidos:
        p['_id'] = str(p['_id'])
    return jsonify(pedidos)

@app.route('/pedidos/crear', methods=['POST'])
def crear_pedido():
    data = request.json
    data["fecha"] = datetime.now().strftime("%d/%m/%Y")
    if "cantidad" not in data:
        data["cantidad"] = 1
    data["estado"] = "activo"
    mongo.db.pedidos.insert_one(data)
    return jsonify({"msg": "Pedido anotado"})

@app.route('/pedidos/actualizar/<id>', methods=['PUT'])
def actualizar_pedido(id):
    cantidad = request.args.get('cantidad')
    mongo.db.pedidos.update_one({"_id": ObjectId(id)}, {"$set": {"cantidad": int(cantidad)}})
    return jsonify({"msg": "OK"})

@app.route('/pedidos/eliminar/<id>', methods=['DELETE'])
def eliminar_pedido(id):
    mongo.db.pedidos.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "Pedido borrado"})

@app.route('/pedidos/finalizar/<id>', methods=['PUT'])
def finalizar_pedido(id):
    mongo.db.pedidos.update_one({"_id": ObjectId(id)}, {"$set": {"estado": "finalizado"}})
    return jsonify({"msg": "Pedido archivado"})

@app.route('/pedidos/historial', methods=['GET'])
def get_historial():
    historial = list(mongo.db.pedidos.find({"estado": "finalizado"}))
    for h in historial:
        h['_id'] = str(h['_id'])
    return jsonify(historial)

@app.route('/pedidos/descargar', methods=['GET'])
def descargar_pedidos():
    pedidos = list(mongo.db.pedidos.find({"estado": {"$ne": "finalizado"}}, {"_id": 0}))
    df = pd.DataFrame(pedidos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pedidos')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='Pedidos_Clientes.xlsx')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
