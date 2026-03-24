📚 Library Management - Odoo 19
Módulo integral de gestión bibliotecaria diseñado para Odoo 19 Community Edition.
Esta solución transforma el estándar de contactos de Odoo en un sistema de socios con control de préstamos, catálogo automatizado y servicios web.

🛠️ Requisitos del Sistema
Lenguaje: Python 3.12
Base de datos: PostgreSQL 14+
Plataforma: Odoo 19.0 CE
Dependencias de Odoo: base, account, point_of_sale, website

🚀 Despliegue del Entorno

1. Preparación del Código (Bash)
# Clonar Odoo 19
   git clone https://github.com/odoo/odoo.git -b 19.0 --depth 1
   cd odoo
# Crear y activar entorno virtual
  py -3.12 -m venv venv312
  .\venv312\Scripts\activate  # Windows
2. Instalación de Dependencias (Bash)
  pip install -r requirements.txt
3. Configuración de Base de Datos
Asegúrate de tener una instancia de PostgreSQL corriendo y crea la base de datos:
  Bashcreatedb -U postgres bdticom
4. Estructura de Carpetas
El módulo debe residir en la carpeta de complementos personalizados:
Plaintextodoo/
└── custom_addons/
    └── library_management/
5. Ejecución y Actualización Forzada
Usa este comando para inicializar el módulo y cargar los cambios de Python y XML de forma limpia:
(Bash)
python odoo-bin -r operez -w 75136560 --addons-path=addons,custom_addons -d bdticom -u library_management --stop-after-init

Funcionalidades Core:

👤 Gestión Avanzada de Socios
Heredado de res.partner: Mantiene la compatibilidad con el ecosistema Odoo.
Identificación Automática: Generación de member_code (ej. LIB-0001) mediante secuencias nativas.
Control de Estado: Campo booleano para distinguir clientes de socios activos.

📑 Catálogo Inteligente
Estados del Libro: Disponible, Prestado.
Metadatos: Autor, ISBN, Fecha de publicación y años de antigüedad calculados en tiempo real.
Vistas Optimización: Agrupación por autor y filtros rápidos de disponibilidad.

🔄 Ciclo de Préstamos y Devoluciones
Lógica de Negocio:Máximo de 5 préstamos activos por socio.Bloqueo automático de libros ya prestados.
Automatización: Cron job diario que marca como "Vencido" cualquier préstamo que supere los 30 días.

🌐 Ecosistema Extendido
REST API: Endpoint /api/library/book para consultas externas de stock mediante ISBN.

🧪 Casos de Prueba (QA)Caso de Prueba

| ID | Caso de Prueba | Acción Realizada | Resultado Esperado |
|:---:|:---|:---|:---|
| **01** | **Registro de Socio** | Activar el check "Es Socio" en la ficha de un contacto. | El sistema genera el `member_code` (ej. LIB-0001) automáticamente. |
| **02** | **Validación de Cupo** | Intentar asignar un 6to préstamo activo al mismo socio. | Odoo lanza una `ValidationError` impidiendo la creación del registro. |
| **03** | **Disponibilidad de Libro** | Intentar prestar un libro cuyo estado es "Prestado". | El sistema bloquea la acción informando que el libro no está disponible. |
| **04** | **Consistencia de Stock** | Confirmar la creación de un nuevo préstamo. | El campo `state` del libro cambia de "Disponible" a "Prestado" instantáneamente. |
| **05** | **Vencimiento Automático** | Ejecutar manualmente el cron `Check Overdue Loans`. | Los préstamos con >30 días cambian su estado a "Vencido". |
| **06** | **Seguridad por Rol** | Acceder al catálogo con un usuario de rol "Público". | Solo son visibles los libros con estado "Disponible". |
| **07** | **REST API (Success)** | Realizar un GET a `/api/library/book` con un ISBN válido. | Retorno de un JSON con los datos del libro y status 200. |
| **08** | **REST API (Fail)** | Realizar un GET con un ISBN que no existe en el catálogo. | Retorno de un JSON con mensaje de error y status 404. |

👤 Autor
Oscar Pérez
Estudiante de Ingeniería en Ciencias de la Computación integrada
Instituto Kriete de Ingeniería y Ciencias
