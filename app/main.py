from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Annotated
from decimal import Decimal

from app.database import fetch_all_productos, fetch_producto_by_id, insert_producto, update_producto, delete_producto

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


@app.get("/productos/{producto_id}", response_model=Producto)
def obtener_producto(producto_id: int):
    """
    Devuelve un producto específico por su ID.
    
    - Obtiene datos raw de MySQL
    - Mapea a ProductoDB (convierte tipos incompatibles)
    - Valida estructura con Pydantic
    - Retorna el Producto o lanza HTTPException 404 si no existe
    """
    # 1. Obtener datos desde MySQL
    row = fetch_producto_by_id(producto_id)
    
    # 2. Validar que el producto existe
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con ID {producto_id} no encontrado"
        )
    
    # 3. Mapear a ProductoDB (conversión de tipos)
    productos_db = map_rows_to_productos([row])
    
    # 4. Retornar el primer (y único) elemento
    return productos_db[0]


@app.post("/productos", response_model=Producto, status_code=201)
def crear_producto(producto: ProductoCreate):
    """
    Crea un nuevo producto en la base de datos.
    
    - Valida datos con Pydantic (ProductoCreate)
    - Inserta en MySQL
    - Retorna el producto creado con ID asignado
    """
    # 1. Insertar el producto en MySQL (retorna ID)
    nuevo_id = insert_producto(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        stock=producto.stock,
        categoria=producto.categoria,
        codigo_sku=producto.codigo_sku,
        activo=producto.activo
    )
    
    # 2. Validar que la inserción fue exitosa
    if not nuevo_id or nuevo_id == 0:
        raise HTTPException(
            status_code=500,
            detail="Error al insertar el producto en la base de datos"
        )
    
    # 3. Recuperar el producto creado desde la BD
    row = fetch_producto_by_id(nuevo_id)
    
    if not row:
        raise HTTPException(
            status_code=500,
            detail="Error al recuperar el producto recién creado"
        )
    
    # 4. Mapear y retornar
    productos_db = map_rows_to_productos([row])
    return productos_db[0]


@app.put("/productos/{producto_id}", response_model=Producto)
def actualizar_producto(producto_id: int, producto: ProductoUpdate):
    """
    Actualiza un producto existente en la base de datos.
    
    - Valida que el producto existe (404 si no)
    - Valida datos con Pydantic (ProductoUpdate)
    - Actualiza en MySQL
    - Retorna el producto actualizado
    """
    # 1. Validar que el producto existe
    row_existente = fetch_producto_by_id(producto_id)
    
    if not row_existente:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con ID {producto_id} no encontrado"
        )
    
    # 2. Actualizar el producto en MySQL
    actualizado = update_producto(
        producto_id=producto_id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        stock=producto.stock,
        categoria=producto.categoria,
        codigo_sku=producto.codigo_sku,
        activo=producto.activo
    )
    
    # 3. Validar que la actualización fue exitosa
    if not actualizado:
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el producto en la base de datos"
        )
    
    # 4. Recuperar el producto actualizado desde la BD
    row_actualizado = fetch_producto_by_id(producto_id)
    
    if not row_actualizado:
        raise HTTPException(
            status_code=500,
            detail="Error al recuperar el producto actualizado"
        )
    
    # 5. Mapear y retornar
    productos_db = map_rows_to_productos([row_actualizado])
    return productos_db[0]


@app.delete("/productos/{producto_id}", status_code=200)
def eliminar_producto(producto_id: int):
    """
    Elimina un producto existente de la base de datos.
    
    - Valida que el producto existe (404 si no)
    - Elimina de MySQL
    - Retorna mensaje de éxito
    """
    # 1. Validar que el producto existe
    row_existente = fetch_producto_by_id(producto_id)
    
    if not row_existente:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con ID {producto_id} no encontrado"
        )
    
    # 2. Eliminar el producto de MySQL
    eliminado = delete_producto(producto_id)
    
    # 3. Validar que la eliminación fue exitosa
    if not eliminado:
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el producto de la base de datos"
        )
    
    # 4. Retornar mensaje de éxito
    return {
        "mensaje": "Producto eliminado exitosamente",
        "id_producto": producto_id
    }
