from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class LibraryPortal(CustomerPortal):

    # agrega "Mis Préstamos" al menú del portal
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'loan_count' in counters:
            # cuenta los préstamos activos del socio actual
            values['loan_count'] = request.env['library.loan'].search_count([
                ('member_id', '=', request.env.user.partner_id.id),
                ('state', '=', 'active'),
            ])
        return values

    # página principal "Mis Préstamos"
    @http.route('/my/loans', type='http', auth='user', website=True)
    def my_loans(self, **kwargs):
        # busca todos los préstamos del socio actual
        loans = request.env['library.loan'].search([
            ('member_id', '=', request.env.user.partner_id.id),
        ])
        return request.render('library_management.portal_my_loans', {
            'loans': loans,
        })

    # endpoint para renovar un préstamo
    @http.route('/my/loans/<int:loan_id>/renew', type='http', auth='user', website=True)
    def renew_loan(self, loan_id, **kwargs):
        # busca el préstamo por su ID
        loan = request.env['library.loan'].browse(loan_id)

        # verifica que el préstamo pertenece al socio actual
        if loan.member_id != request.env.user.partner_id:
            return request.redirect('/my/loans')

        # solo se puede renovar si está activo (no vencido)
        if loan.state == 'active':
            # extiende 30 días más desde hoy
            from datetime import date, timedelta
            loan.loan_date = date.today()

        return request.redirect('/my/loans')