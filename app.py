from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = "mongodb+srv://usuario_web:FEh8oeAhmoSPFqhn@stockescalu.mikltkh.mongodb.net/ESCALU_DB?retryWrites=true&w=majority&authSource=admin"
mongo = PyMongo(app)

@app.route('/')
def home():
    return "Servidor ESCALU OK"

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
    if vendido is not None: update_data["vendido"] = int(vendido)
    if recep is not None: update_data["recepcionadas"] = int(recep)
    mongo.db.stock.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return jsonify({"msg": "OK"})

@app.route('/stock/eliminar/<id>', methods=['DELETE'])
def delete_product(id):
    mongo.db.stock.delete_one({"_id": ObjectId(id)})
    return jsonify({"msg": "OK"})

@app.route('/stock/importar', methods=['POST'])
def importar_excel():
    try:
        if 'file' not in request.files: return jsonify({"error": "No file"}), 400
        file = request.files['file']
        df = pd.read_excel(file)
        # Limpieza de datos
        df['vendido'] = df['vendido'].fillna(0).astype(int)
        df['recepcionadas'] = df['recepcionadas'].fillna(0).astype(int)
        df['ref'] = df['ref'].astype(str).str.upper()
        df['seccion'] = df['seccion'].astype(str).str.upper()
        
        datos = df.to_dict(orient='records')
        mongo.db.stock.insert_many(datos)
        return jsonify({"msg": f"¡Éxito! {len(datos)} productos cargados."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
