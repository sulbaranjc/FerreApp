from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Annotated
from decimal import Decimal

from app.database import fetch_all_productos

app = FastAPI(
    title="FerreApp API",
    version="1.0.0",
    description="API REST desacoplada para gestión de productos de ferretería"
)


# ========================
# Modelos Pydantic
# ========================

class ProductoBase(BaseModel):
    """Modelo base con validaciones compartidas para Producto."""
    nombre: Annotated[str, Field(min_length=1, max_length=80)]
    descripcion: Optional[Annotated[str, Field(max_length=255)]] = None
    precio: float = Field(ge=0)
    stock: int = Field(ge=0)
    categoria: Annotated[str, Field(min_length=1, max_length=50)]
    codigo_sku: Annotated[str, Field(min_length=1, max_length=20)]
    activo: bool = True

    @field_validator('nombre', 'categoria')
    @classmethod
    def validar_nombre_categoria(cls, v: str) -> str:
        """Valida nombre y categoría."""
        if not v or not v.strip():
            raise ValueError('El campo no puede estar vacío')
        return v.strip()

    @field_validator('codigo_sku')
    @classmethod
    def validar_codigo_sku(cls, v: str) -> str:
        """Valida código SKU."""
        v = v.strip().upper()
        if not v:
            raise ValueError('El SKU no puede estar vacío')
        return v

    @field_validator('descripcion')
    @classmethod
    def validar_descripcion(cls, v: Optional[str]) -> Optional[str]:
        """Valida descripción."""
        if v is None or v.strip() == '':
            return None
        return v.strip()


class ProductoDB(BaseModel):
    """Modelo para lectura desde BD (sin validaciones estrictas para datos históricos)."""
    id_producto: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    categoria: str
    codigo_sku: str
    activo: bool


class ProductoCreate(ProductoBase):
    """Modelo para crear nuevo producto (sin ID)."""
    pass


class ProductoUpdate(ProductoBase):
    """Modelo para actualizar producto (sin ID)."""
    pass


class Producto(ProductoBase):
    """Modelo completo de Producto (con ID y validaciones)."""
    id_producto: int


# ========================
# Funciones Helper
# ========================

def map_rows_to_productos(rows: List[dict]) -> List[ProductoDB]:
    """
    Convierte las filas del SELECT * FROM producto (dict) 
    en objetos ProductoDB. Maneja conversión de tipos incompatibles
    como Decimal → float.
    """
    productos_db = []
    for row in rows:
        # Preparar datos para ProductoDB
        producto_data = dict(row)
        
        # Convertir Decimal a float si es necesario
        if isinstance(producto_data.get("precio"), Decimal):
            producto_data["precio"] = float(producto_data["precio"])
        
        # Garantizar booleano para activo
        producto_data["activo"] = bool(producto_data.get("activo", False))
        
        # Crear objeto ProductoDB desempacando el diccionario
        producto = ProductoDB(**producto_data)
        productos_db.append(producto)

    return productos_db


# ========================
# Endpoints
# ========================

@app.get("/ping")
def ping():
    """Endpoint de prueba."""
    return {"message": "pong"}


@app.get("/productos", response_model=List[Producto])
def listar_productos():
    """
    Devuelve la lista de todos los productos desde la base de datos.
    
    - Obtiene datos raw de MySQL
    - Mapea a ProductoDB (convierte tipos incompatibles)
    - Valida estructura con Pydantic
    - Retorna lista de Productos
    """
    # 1. Obtener datos desde MySQL
    rows = fetch_all_productos()

    # 2. Mapear a ProductoDB (conversión de tipos)
    productos_db = map_rows_to_productos(rows)

    # 3. Retornar como Producto (con validación de Pydantic)
    return productos_db
