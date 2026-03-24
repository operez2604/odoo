{
    'name':'Library Management',
    'version': '19.0.1.0.0',
    'summary': 'Gestión de biblioteca: Libros, préstamos y socios',
    'description': 'Módulo para gestionar socios, préstamos y catálogos de libros',
    'author' : 'operez',
    'category' : 'Services',
    'depends' : [
        'base',
        'account',
        'contacts',
        'mail',
        'point_of_sale',
        'portal',
    ],
    'data': [
        'security/library_security.xml', #Regla fija en Odoo para acceder a modelos
        'security/ir.model.access.csv', #Para acceder a grupos y roles 
        'data/sequences.xml',
        'data/cron_jobs.xml',
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_loan_views.xml',
        'views/portal_templates.xml',
    ],
    'application':True,
    'installable':True,
    'license': 'LGPL-3',
}