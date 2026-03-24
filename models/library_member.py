from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campos requeridos por las vistas XML
    is_library_member = fields.Boolean(string='Es Socio de la Biblioteca', default=False)
    member_code = fields.Char(string='Código de Socio', readonly=True, copy=False)
    # Agregamos este campo porque el error de Odoo indicaba que no existía en el XML
    membership_date = fields.Date(string='Fecha de Alta', default=fields.Date.today)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Si se marca como socio y no tiene código, intentamos asignar uno
            if vals.get('is_library_member') and not vals.get('member_code'):
                # Busca la secuencia. Si no existe, pone 'NUEVO'
                seq = self.env['ir.sequence'].next_by_code('library.member.sequence')
                vals['member_code'] = seq or 'NUEVO'
        return super(ResPartner, self).create(vals_list)


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Préstamo de Biblioteca'
    _order = 'loan_date desc'

    book_id = fields.Many2one('library.book', string='Libro', required=True)
    member_id = fields.Many2one(
        'res.partner', 
        string='Socio', 
        domain=[('is_library_member', '=', True)], 
        required=True
    )
    loan_date = fields.Date(string='Fecha de préstamo', default=fields.Date.today, required=True)
    return_date = fields.Date(string='Fecha de devolución')
    
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
                # El préstamo vence a los 30 días
                limit_date = loan.loan_date + timedelta(days=30)
                loan.state = 'overdue' if limit_date < today else 'active'
            else:
                loan.state = 'active'

    @api.constrains('book_id', 'state')
    def _check_book_available(self):
        for loan in self:
            # Solo validamos disponibilidad si se está creando un préstamo activo
            if loan.state != 'returned' and loan.book_id.state != 'available':
                raise ValidationError(_('El libro "%s" no está disponible para préstamo.') % loan.book_id.name)

    @api.constrains('member_id')
    def _check_member_loans(self):
        for loan in self:
            active_loans = self.search_count([
                ('member_id', '=', loan.member_id.id),
                ('state', 'in', ['active', 'overdue']),
                ('id', '!=', loan.id) # No contarse a sí mismo si es edición
            ])
            if active_loans >= 5:
                raise ValidationError(_('El socio %s ya tiene el límite de 5 préstamos activos.') % loan.member_id.name)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(LibraryLoan, self).create(vals_list)
        for loan in records:
            # Al crear el préstamo, marcamos el libro como prestado
            if loan.state in ('active', 'overdue') and loan.book_id:
                loan.book_id.state = 'loaned'
        return records

    def action_return_book(self):
        """ Método para el botón de devolver en la vista """
        for loan in self:
            loan.return_date = fields.Date.today()
            if loan.book_id:
                loan.book_id.state = 'available'