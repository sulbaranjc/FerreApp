from dotenv import load_dotenv, find_dotenv
import os
import mysql.connector
from typing import List, Dict, Any, cast
from mysql.connector.cursor import MySQLCursorDict  # opción C si la prefieres

# Carga .env desde la raíz
load_dotenv(find_dotenv())

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),        # <— corregidos nombres
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ferreapp"),
        port=int(os.getenv("DB_PORT", "3306")),
        charset="utf8mb4"
    )

def fetch_all_productos() -> List[Dict[str, Any]]:
    """
    Ejecuta SELECT * FROM producto y devuelve una lista de dicts.
    """
    conn = None
    try:
        conn = get_connection()

        # Opción C (anotación explícita del cursor)
        cur: MySQLCursorDict
        cur = conn.cursor(dictionary=True)  # type: ignore[assignment]

        try:
            cur.execute(
                """
                SELECT
                    id_producto,
                    nombre,
                    descripcion,
                    precio,
                    stock,
                    categoria,
                    codigo_sku,
                    activo
                FROM producto;
                """
            )

            # Opción A: cast para contentar al type checker
            rows = cast(List[Dict[str, Any]], cur.fetchall())
            return rows

            # Opción B alternativa (sin cast):
            # return [dict(row) for row in cur.fetchall()]

        finally:
            cur.close()

    finally:
        if conn:
            conn.close()

def insert_producto(
    nombre: str,
    descripcion: str | None,
    precio: float,
    stock: int,
    categoria: str,
    codigo_sku: str,
    activo: bool = True
) -> int:
    """
    Inserta un nuevo producto en la base de datos.
    Retorna el ID del producto insertado.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO producto
                    (nombre, descripcion, precio, stock, categoria, codigo_sku, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    nombre,
                    descripcion,
                    precio,
                    stock,
                    categoria,
                    codigo_sku,
                    activo
                )
            )
            conn.commit()
            return cur.lastrowid or 0
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()


def delete_producto(producto_id: int) -> bool:
    """
    Elimina un producto de la base de datos por su ID.
    Retorna True si se eliminó correctamente, False si no se encontró.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "DELETE FROM producto WHERE id_producto = %s",
                (producto_id,)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()


def fetch_producto_by_id(producto_id: int) -> Dict[str, Any] | None:
    """
    Obtiene un producto por su ID.
    Retorna un dict con los datos del producto o None si no existe.
    """
    conn = None
    try:
        conn = get_connection()

        # Cursor tipado explícitamente (mismo patrón)
        cur: MySQLCursorDict
        cur = conn.cursor(dictionary=True)  # type: ignore[assignment]

        try:
            cur.execute(
                """
                SELECT
                    id_producto,
                    nombre,
                    descripcion,
                    precio,
                    stock,
                    categoria,
                    codigo_sku,
                    activo
                FROM producto
                WHERE id_producto = %s
                """,
                (producto_id,)
            )
            result = cur.fetchone()
            return dict(result) if result else None
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()


def update_producto(
    producto_id: int,
    nombre: str,
    descripcion: str | None,
    precio: float,
    stock: int,
    categoria: str,
    codigo_sku: str,
    activo: bool
) -> bool:
    """
    Actualiza los datos de un producto existente.
    Retorna True si se actualizó correctamente, False si no se encontró.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE producto
                SET
                    nombre = %s,
                    descripcion = %s,
                    precio = %s,
                    stock = %s,
                    categoria = %s,
                    codigo_sku = %s,
                    activo = %s
                WHERE id_producto = %s
                """,
                (
                    nombre,
                    descripcion,
                    precio,
                    stock,
                    categoria,
                    codigo_sku,
                    activo,
                    producto_id
                )
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
    finally:
        if conn:
            conn.close()
