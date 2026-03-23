from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# Configuración de MongoDB (Asegúrate de tener tu variable de entorno en Render)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "tu_mongodb_uri_aqui")
mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor IMMINENT Funcionando"

# 1. OBTENER STOCK POR SECCIÓN
@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    productos = list(mongo.db.stock.find({'seccion': seccion}))
    for p in productos:
        p['_id'] = str(p['_id'])
    return jsonify(productos)

# 2. AÑADIR NUEVO PRODUCTO
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

# 3. ACTUALIZAR (VENTAS O RECIBIDAS) - ¡ESTA ES LA QUE HEMOS ARREGLADO!
@app.route('/stock/vender/<id>', methods=['PUT'])
def vender_mueble(id):
    vendido = request.args.get('vendido')
    recepcionadas = request.args.get('recepcionadas')
    
    update_fields = {}
    
    # Si enviamos 'vendido' por la URL, lo actualiza
    if vendido is not None:
        update_fields['vendido'] = int(vendido)
        
    # Si enviamos 'recepcionadas' (el botón +), lo actualiza
    if recepcionadas is not None:
        update_fields['recepcionadas'] = int(recepcionadas)
        
    if update_fields:
        mongo.db.stock.update_one({'_id': ObjectId(id)}, {'$set': update_fields})
        return jsonify({'msg': 'Datos actualizados'})
    
    return jsonify({'msg': 'No se enviaron datos'}), 400

# 4. ELIMINAR PRODUCTO
@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def eliminar_mueble(id):
    mongo.db.stock.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': 'Eliminado'})

if __name__ == '__main__':
    app.run(debug=True)