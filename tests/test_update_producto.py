import sys
from pathlib import Path

# Agregar la ra�z del proyecto al path para los imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import update_producto

if __name__ == "__main__":
    try:
        # Validar que se haya pasado el ID como par�metro
        if len(sys.argv) < 2:
            print('\u274c Error: Debes proporcionar el ID del producto')
            print('Uso: python tests/test_update_producto.py <ID>')
            sys.exit(1)
        
        # Obtener el ID del producto desde los argumentos
        producto_id = int(sys.argv[1])
        resultado = update_producto(
            producto_id=producto_id,
            nombre='producto modificado por el test',
            descripcion='Martillo de acero reforzado con mango antideslizante',
            precio=14.90,
            stock=20,
            categoria='Herramientas',
            codigo_sku='MART-16OZxxxxx',
            activo=True
        )

        if resultado:
            print(f'\u2705 Producto {producto_id} actualizado correctamente')
        else:
            print(f'\u26a0\ufe0f Producto {producto_id} no encontrado')
    except ValueError:
        print('\u274c Error: El ID debe ser un n�mero entero')
        sys.exit(1)
    except Exception as e:
        print('\u274c Error al actualizar producto \u2192', e)

# ===== EJECUCI�N DESDE CMD =====
# python tests/test_update_producto.py 1