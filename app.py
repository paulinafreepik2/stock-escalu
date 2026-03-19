from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONEXIÓN A MONGODB (Pon tu clave real aquí) ---
MONGO_URL = "mongodb+srv://ADMIN:12345@stockescalu.mikltkh.mongodb.net/?retryWrites=true&w=majority&appName=STOCKESCALU"
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_database("ESCALU_DB")
coleccion = db.get_collection("inventario")

class Mueble(BaseModel):
    ref: str
    descripcion: str
    color: str
    recepcionadas: int
    vendido: int
    seccion: str

@app.get("/stock/{seccion}")
async def obtener_stock(seccion: str):
    cursor = coleccion.find({"seccion": seccion.upper()})
    productos = await cursor.to_list(length=100)
    for p in productos:
        p["_id"] = str(p["_id"])
    return productos

@app.post("/stock/agregar")
async def agregar_mueble(mueble: Mueble):
    nuevo = await coleccion.insert_one(mueble.dict())
    return {"status": "ok", "id": str(nuevo.inserted_id)}

@app.delete("/stock/eliminar/{id}")
async def eliminar_mueble(id: str):
    await coleccion.delete_one({"_id": ObjectId(id)})
    return {"status": "borrado"}

@app.put("/stock/vender/{id}")
async def vender_mueble(id: str, vendido: int):
    await coleccion.update_one({"_id": ObjectId(id)}, {"$set": {"vendido": vendido}})
    return {"status": "actualizado"}

@app.get("/")
def inicio():
    return {"mensaje": "Servidor ESCALU OK"}