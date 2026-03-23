from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN CON TU USUARIO ADMIN Y CONTRASEÑA ADMIN ---
# He añadido 'stock_db' al final para que sepa exactamente a qué base de datos ir
app.config["MONGO_URI"] = "mongodb+srv://ADMIN:ADMIN@stockescalu.mikltkh.mongodb.net/stock_db?retryWrites=true&w=majority"
# --------------------------------------------------------------

mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor IMMINENT Funcionando"

@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    try:
        # Buscamos en la coleccion 'stock'
        productos = list(mongo.db.stock.find({'seccion': seccion}))
        for p in productos:
            p['_id'] = str(p['_id'])
        return jsonify(productos)
    except Exception as e:
        print(f"Error en GET: {e}")
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
        
        return jsonify({'error': 'No hay datos'}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def eliminar_mueble(id):
    try:
        mongo.db.stock.delete_one({'_id': ObjectId(id)})
        return jsonify({'msg': 'Eliminado'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Usamos el puerto que nos dé Render o el 5000 por defecto
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
