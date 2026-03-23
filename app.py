from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os

app = Flask(__name__)
# Permitimos CORS para que tu nueva web de GitHub Pages pueda hablar con Render
CORS(app)

# --- CONFIGURACIÓN DE CONEXIÓN ---
# He puesto /test que es donde suelen guardarse los datos por defecto
app.config["MONGO_URI"] = "mongodb+srv://ADMIN:ADMIN@stockescalu.mikltkh.mongodb.net/test?retryWrites=true&w=majority"
# ---------------------------------

mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor IMMINENT Funcionando en Plan Starter"

@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    try:
        # Buscamos en la colección 'stock' dentro de la base de datos
        productos = list(mongo.db.stock.find({'seccion': seccion}))
        for p in productos:
            p['_id'] = str(p['_id'])
        return jsonify(productos)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([]), 200

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

@app.route('/stock/vender/<id>', methods=['PUT'])
def vender_mueble(id):
    try:
        vendido = request.args.get('vendido')
        recepcionadas = request.args.get('recepcionadas')
        update_data = {}
        
        if vendido is not None:
            update_data['vendido'] = int(float(vendido))
            
        if recepcionadas is not None:
            update_data['recepcionadas'] = int(float(recepcionadas))

        if update_data:
            mongo.db.stock.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            return jsonify({'status': 'ok'}), 200
        
        return jsonify({'error': 'No hay datos para actualizar'}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def eliminar_mueble(id):
    try:
        mongo.db.stock.delete_one({'_id': ObjectId(id)})
        return jsonify({'msg': 'Eliminado con éxito'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Configuración necesaria para Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
