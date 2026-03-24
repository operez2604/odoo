from odoo import models, api
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, order, draft, existing_order):
        # procesamos la orden normalmente primero
        result = super()._process_order(order, draft, existing_order)

        # obtenemos la orden creada
        pos_order = self.browse(result)

        for line in pos_order.lines:
            product = line.product_id

            # verificamos si el producto es un libro
            book = self.env['library.book'].search([
                ('name', '=', product.name),
                ('state', '=', 'available'),
            ], limit=1)

            if book:
                partner = pos_order.partner_id

                # verificamos si el cliente es socio
                if not partner or not partner.is_library_member:
                    raise ValidationError(
                        'El cliente debe ser socio de la biblioteca para realizar un préstamo.'
                    )

                # verificamos que no tenga 5 préstamos activos
                active_loans = self.env['library.loan'].search_count([
                    ('member_id', '=', partner.id),
                    ('state', '=', 'active'),
                ])
                if active_loans >= 5:
                    raise ValidationError(
                        f'El socio {partner.name} ya tiene 5 préstamos activos.'
                    )

                # creamos el préstamo automáticamente
                self.env['library.loan'].create({
                    'book_id': book.id,
                    'member_id': partner.id,
                    'state': 'active',
                })

                # marcamos el libro como prestado
                book.state = 'loaned'

        return result