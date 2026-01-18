-- =====================================================
-- Base de datos: FerreApp
-- Tabla: producto
-- =====================================================

-- 1) Crear base de datos
DROP DATABASE IF EXISTS FerreApp;
CREATE DATABASE IF NOT EXISTS FerreApp
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2) Usar la base de datos
USE FerreApp;

-- 3) Crear tabla producto
CREATE TABLE producto (
  id_producto INT UNSIGNED AUTO_INCREMENT,
  nombre VARCHAR(80) NOT NULL,
  descripcion VARCHAR(255) NULL,
  precio DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL,
  categoria VARCHAR(50) NOT NULL,
  codigo_sku VARCHAR(20) NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE,

  CONSTRAINT pk_producto PRIMARY KEY (id_producto),
  CONSTRAINT uq_producto_sku UNIQUE (codigo_sku)
);

-- =====================================================
-- 4) Datos de ejemplo (seed data)
-- =====================================================

INSERT INTO producto (nombre, descripcion, precio, stock, categoria, codigo_sku, activo) VALUES
('Martillo 16oz', 'Martillo de acero con mango ergonómico', 12.50, 25, 'Herramientas', 'MART-16OZ', TRUE),
('Destornillador plano', 'Destornillador plano 5mm', 4.20, 40, 'Herramientas', 'DEST-PL-5', TRUE),
('Taladro eléctrico', 'Taladro eléctrico 500W', 65.99, 10, 'Herramientas eléctricas', 'TAL-500W', TRUE),
('Caja de tornillos', 'Tornillos acero M6 x 40 (100 unidades)', 8.75, 15, 'Tornillería', 'TOR-M6-40', TRUE),
('Llave inglesa', 'Llave ajustable 10 pulgadas', 14.30, 20, 'Herramientas', 'LLAV-10P', TRUE),
('Broca para metal', 'Broca HSS 6mm', 2.80, 60, 'Accesorios', 'BROC-HSS-6', TRUE),
('Cinta métrica', 'Cinta métrica 5 metros', 6.90, 30, 'Medición', 'CINT-5M', TRUE),
('Guantes de trabajo', 'Guantes reforzados talla M', 5.50, 50, 'Seguridad', 'GUANT-M', TRUE),
('Nivel de burbuja', 'Nivel de aluminio 40cm', 9.95, 18, 'Medición', 'NIV-40', TRUE),
('Sierra manual', 'Sierra manual para madera', 11.20, 12, 'Corte', 'SIER-MAD', TRUE);
-- =====================================================
-- Usuario de base de datos para la aplicación FerreApp
-- =====================================================

-- Crear usuario (si no existe)
CREATE USER IF NOT EXISTS 'ferreapp'@'localhost'
IDENTIFIED BY 'ferreapp123';

-- Otorgar todos los permisos SOLO sobre la base FerreApp
GRANT ALL PRIVILEGES ON FerreApp.* TO 'ferreapp'@'localhost';

-- Aplicar cambios de privilegios
FLUSH PRIVILEGES;
