from flask import Flask, jsonify, request, send_file
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
import pandas as pd
import io
import math
import os
from datetime import datetime
from datetime import datetime, timezone

app = Flask(__name__)
# BLINDAMOS EL CORS PARA QUE NO BLOQUEE LOS BOTONES
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de MongoDB
app.config["MONGO_URI"] = os.environ["MONGO_URI"]
mongo = PyMongo(app)

@app.route('/')
def home():
    return send_file('index.html')

# --- RUTAS DE STOCK ---
@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    productos = list(mongo.db.stock.find({"seccion": seccion}))
    for p in productos:
        p['_id'] = str(p['_id'])
    return jsonify(productos)
# REGISTRAR FECHA DE RECEPCIÓN O VENTA
@app.route('/stock/movimiento/<id>', methods=['POST'])
def registrar_movimiento(id):
    try:
        tipo = request.args.get('tipo')
        cantidad = int(float(request.args.get('cantidad', 0)))

        if tipo not in ('rec', 'ven') or cantidad == 0:
            return jsonify({'msg': 'Movimiento no válido'}), 400

        mongo.db.stock.update_one({'_id': ObjectId(id)}, {'$push': {'movimientos': {
            'tipo': tipo,
            'cantidad': cantidad,
            'fecha': datetime.now(timezone.utc).isoformat()
        }}})
        return jsonify({'msg': 'Movimiento guardado'})
    except Exception as e:
        print(f"Error en movimiento: {e}")
        return jsonify({"error": str(e)}), 500

# PUNTOS DE CADA MUEBLE
@app.route('/stock/puntos/<id>', methods=['PUT', 'OPTIONS'])
def poner_puntos(id):
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    try:
        puntos = float(request.args.get('puntos', ''))
    except ValueError:
        return jsonify({"error": "Puntos no válidos"}), 400
    if not math.isfinite(puntos) or puntos < 0:
        return jsonify({"error": "Puntos no válidos"}), 400
    if puntos.is_integer():
        puntos = int(puntos)
    mongo.db.stock.update_one({"_id": ObjectId(id)}, {"$set": {"puntos": puntos}})
    return jsonify({"msg": "OK"})

@app.route('/stock/agregar', methods=['POST', 'OPTIONS'])
def add_product():
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    data = request.json
    nuevo_id = mongo.db.stock.insert_one(data).inserted_id
    return jsonify({"msg": "OK", "id": str(nuevo_id)})

@app.route('/stock/actualizar/<id>', methods=['PUT', 'OPTIONS'])
def actualizar_stock(id):
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200

    tipo = request.args.get('tipo')
    cantidad = int(request.args.get('cantidad', 0))

    if tipo == 'rec':
        mongo.db.stock.update_one({"_id": ObjectId(id)}, {"$inc": {"recepcionadas": cantidad}})
    elif tipo == 'ven':
        mongo.db.stock.update_one({"_id": ObjectId(id)}, {"$inc": {"vendido": cantidad}})

    return jsonify({"msg": "OK"})

@app.route('/stock/eliminar/<id>', methods=['DELETE', 'OPTIONS'])
def delete_product(id):
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    mongo.db.stock.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "OK"})

# AQUÍ ESTÁ EL BOTÓN NUCLEAR CON LA SANGRÍA PERFECTA
@app.route('/stock/eliminar_seccion/<seccion>', methods=['DELETE', 'OPTIONS'])
def eliminar_toda_seccion(seccion):
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    mongo.db.stock.delete_many({"seccion": seccion})
    return jsonify({"msg": "OK"})

# --- RUTAS DE PEDIDOS ---
@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    pedidos = list(mongo.db.pedidos.find({"estado": {"$ne": "finalizado"}}))
    for p in pedidos:
        p['_id'] = str(p['_id'])
    return jsonify(pedidos)

@app.route('/pedidos/crear', methods=['POST', 'OPTIONS'])
def crear_pedido():
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    data = request.json
    data["fecha"] = datetime.now().strftime("%d/%m/%Y")
    if "cantidad" not in data: data["cantidad"] = 1
    data["estado"] = "activo"
    mongo.db.pedidos.insert_one(data)
    return jsonify({"msg": "OK"})

@app.route('/pedidos/actualizar/<id>', methods=['PUT', 'OPTIONS'])
def actualizar_pedido(id):
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    cantidad = request.args.get('cantidad')
    mongo.db.pedidos.update_one({"_id": ObjectId(id)}, {"$set": {"cantidad": int(cantidad)}})
    return jsonify({"msg": "OK"})

@app.route('/pedidos/finalizar/<id>', methods=['PUT', 'OPTIONS'])
def finalizar_pedido(id):
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    mongo.db.pedidos.update_one({"_id": ObjectId(id)}, {"$set": {"estado": "finalizado"}})
    return jsonify({"msg": "Archivado"})

@app.route('/pedidos/eliminar/<id>', methods=['DELETE', 'OPTIONS'])
def eliminar_pedido(id):
    if request.method == 'OPTIONS':
        return jsonify({"msg": "OK"}), 200
    mongo.db.pedidos.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "OK"})

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
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='Pedidos.xlsx')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
