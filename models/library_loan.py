from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Préstamo de Biblioteca'

    book_id = fields.Many2one('library.book', string='Libro', required=True)
    member_id = fields.Many2one('res.partner', string='Socio', 
                                domain=[('is_library_member', '=', True)], required=True)
    loan_date = fields.Date('Fecha de préstamo', default=fields.Date.today, required=True)
    return_date = fields.Date('Fecha de devolución')
    
    state = fields.Selection([
        ('active', 'Activo'),
        ('returned', 'Devuelto'),
        ('overdue', 'Vencido'),
    ], string='Estado', compute='_compute_state', store=True, default='active')

    @api.depends('loan_date', 'return_date')
    def _compute_state(self):
        today = fields.Date.today()
        for loan in self:
            if loan.return_date:
                loan.state = 'returned'
            elif loan.loan_date:
                limit_date = loan.loan_date + timedelta(days=30)
                if limit_date < today:
                    loan.state = 'overdue'
                else:
                    loan.state = 'active'
            else:
                loan.state = 'active'

    @api.constrains('book_id')
    def _check_book_available(self):
        for loan in self:
            if loan.state != 'returned' and loan.book_id.state != 'available':
                raise ValidationError('El libro no está disponible para préstamo.')

    @api.constrains('member_id')
    def _check_member_loans(self):
        for loan in self:
            active_loans = self.search_count([
                ('member_id', '=', loan.member_id.id),
                ('state', 'in', ['active', 'overdue']),
            ])
            if active_loans > 5:
                raise ValidationError('El socio ya tiene el límite de 5 préstamos no devueltos.')

    # ESTAS FUNCIONES DEBEN ESTAR DENTRO DE LA CLASE (INDENTADAS)
    @api.model_create_multi
    def create(self, vals_list):
        records = super(LibraryLoan, self).create(vals_list)
        for loan in records:
            if loan.state in ('active', 'overdue'):
                loan.book_id.state = 'loaned'
        return records

    def action_return_book(self):
        for loan in self:
            loan.return_date = fields.Date.today()
            if loan.book_id:
                loan.book_id.state = 'available'