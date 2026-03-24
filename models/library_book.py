from odoo import models,fields,api #models para asignar el modelo a la bd, fields para las columnas de la tabla y api para que sepan cuando ejecutarse los metodos
from datetime import date

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Libro de Biblioteca'

    name = fields.Char('Título', required=True)
    author = fields.Char('Autor', required=True)
    isbn = fields.Char('ISBN', required=True)
    publication_date = fields.Date('Fecha de Publicación')
    state = fields.Selection([
        ('available', 'Disponible'),
        ('loaned', 'Prestado'),
    ], string='Estado', default='available', required=True)

    years_since_publication = fields.Integer(
        string='Años desde publicación',
        compute='_compute_years',
        store=True,
    )

    @api.depends('publication_date')
    def _compute_years(self):
        for book in self:
            if book.publication_date:
                book.years_since_publication = date.today().year - book.publication_date.year
            else:
                book.years_since_publication = 0