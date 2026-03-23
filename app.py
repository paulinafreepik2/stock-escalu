from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# Tu conexión directa
app.config["MONGO_URI"] = "mongodb+srv://ADMIN:ADMIN@stockescalu.mikltkh.mongodb.net/stock_db?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor IMMINENT Funcionando"

@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    try:
        # Importante: buscamos en la base de datos que conectamos
        productos = list(mongo.db.stock.find({'seccion': seccion}))
        for p in productos:
            p['_id'] = str(p['_id'])
        return jsonify(productos)
    except Exception as e:
        return jsonify([]), 200

@app.route('/stock/vender/<id>', methods=['PUT'])
def vender_mueble(id):
    try:
        vendido = request.args.get('vendido')
        recepcionadas = request.args.get('recepcionadas')
        update_data = {}
        if vendido is not None: update_data['vendido'] = int(float(vendido))
        if recepcionadas is not None: update_data['recepcionadas'] = int(float(recepcionadas))
        
        if update_data:
            mongo.db.stock.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            return jsonify({'status': 'ok'}), 200
        return jsonify({'error': 'No data'}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock/agregar', methods=['POST'])
def agregar_mueble():
    try:
        datos = request.json
        nuevo_id = mongo.db.stock.insert_one({
            'ref': datos['ref'],
            'descripcion': datos['descripcion'],
            'color': datos['color'],
            'recepcionadas': int(datos['recepcionadas']),
            'vendido': int(datos['vendido']),
            'seccion': datos['seccion']
        }).inserted_id
        return jsonify({'id': str(nuevo_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def eliminar_mueble(id):
    try:
        mongo.db.stock.delete_one({'_id': ObjectId(id)})
        return jsonify({'msg': 'Eliminado'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Quitamos el app.run de aquí abajo, Gunicorn no lo necesita
