from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import os

app = Flask(__name__)
# Permite la comunicación entre GitHub Pages y Render
CORS(app)

# --- CONEXIÓN CON EL NUEVO USUARIO Y CONTRASEÑA ---
# Usamos el usuario 'usuario_web' y la contraseña que has generado
app.config["MONGO_URI"] = "mongodb+srv://usuario_web:FEh8oeAhmoSPFqhn@stockescalu.mikltkh.mongodb.net/ESCALU_DB?retryWrites=true&w=majority&authSource=admin"
# -------------------------------------------------

mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor ESCALU funcionando en Starter - Conexión OK"

# 1. OBTENER STOCK POR SECCIÓN
@app.route('/stock/<seccion>', methods=['GET'])
def get_stock(seccion):
    try:
        # Buscamos en la colección 'stock' dentro de 'ESCALU_DB'
        productos = list(mongo.db.stock.find({'seccion': seccion}))
        for p in productos:
            p['_id'] = str(p['_id'])
        return jsonify(productos)
    except Exception as e:
        print(f"Error en GET: {e}")
        return jsonify([]), 200

# 2. AÑADIR NUEVO PRODUCTO
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
        print(f"Error en POST: {e}")
        return jsonify({"error": str(e)}), 500

# 3. ACTUALIZAR (VENTAS O RECIBIDAS)
@app.route('/stock/vender/<id>', methods=['PUT'])
def vender_mueble(id):
    try:
        vendido = request.args.get('vendido')
        recepcionadas = request.args.get('recepcionadas')
        
        update_fields = {}
        
        if vendido is not None:
            update_fields['vendido'] = int(float(vendido))
            
        if recepcionadas is not None:
            update_fields['recepcionadas'] = int(float(recepcionadas))
            
        if update_fields:
            mongo.db.stock.update_one({'_id': ObjectId(id)}, {'$set': update_fields})
            return jsonify({'msg': 'Datos actualizados'})
        
        return jsonify({'msg': 'No se enviaron datos'}), 400
    except Exception as e:
        print(f"Error en PUT: {e}")
        return jsonify({"error": str(e)}), 500

# 4. ELIMINAR PRODUCTO
@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def eliminar_mueble(id):
    try:
        mongo.db.stock.delete_one({'_id': ObjectId(id)})
        return jsonify({'msg': 'Eliminado'})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# CONFIGURACIÓN PARA RENDER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
