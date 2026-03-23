from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# Configuración de MongoDB
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "TU_MONGO_URI_AQUI")
mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor IMMINENT Funcionando"

@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    productos = list(mongo.db.stock.find({'seccion': seccion}))
    for p in productos:
        p['_id'] = str(p['_id'])
    return jsonify(productos)

@app.route('/stock/agregar', methods=['POST'])
def agregar_mueble():
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

# FUNCION CORREGIDA PARA EVITAR ERROR 422
@app.route('/stock/vender/<id>', methods=['PUT'])
def vender_mueble(id):
    # Cogemos los datos de la URL
    vendido = request.args.get('vendido')
    recepcionadas = request.args.get('recepcionadas')
    
    update_data = {}
    
    if vendido is not None:
        try:
            update_data['vendido'] = int(float(vendido))
        except: pass
        
    if recepcionadas is not None:
        try:
            update_data['recepcionadas'] = int(float(recepcionadas))
        except: pass

    if update_data:
        mongo.db.stock.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        return jsonify({'status': 'ok', 'actualizado': update_data}), 200
    
    return jsonify({'error': 'No hay datos'}), 400

@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def eliminar_mueble(id):
    mongo.db.stock.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': 'Eliminado'})

if __name__ == '__main__':
    app.run(debug=True)
