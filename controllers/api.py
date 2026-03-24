from odoo import http
from odoo.http import request
import json


class LibraryAPI(http.Controller):

    # endpoint REST para consultar disponibilidad por ISBN
    # ejemplo: GET /api/library/book?isbn=978-3-16-148410-0
    @http.route('/api/library/book', type='http', auth='public', methods=['GET'], csrf=False)
    def get_book_availability(self, isbn=None, **kwargs):

        # si no se envió ISBN retorna error 400
        if not isbn:
            return request.make_response(
                json.dumps({'error': 'ISBN requerido'}),
                headers=[('Content-Type', 'application/json')],
                status=400,
            )

        # busca el libro por ISBN en la BD
        book = request.env['library.book'].sudo().search([
            ('isbn', '=', isbn)
        ], limit=1)

        # si no existe retorna error 404
        if not book:
            return request.make_response(
                json.dumps({'error': 'Libro no encontrado'}),
                headers=[('Content-Type', 'application/json')],
                status=404,
            )

        # si existe retorna disponibilidad en JSON
        return request.make_response(
            json.dumps({
                'id': book.id,
                'title': book.name,
                'isbn': book.isbn,
                'available': book.state == 'available',
                'state': book.state,
            }),
            headers=[('Content-Type', 'application/json')],
            status=200,
        )