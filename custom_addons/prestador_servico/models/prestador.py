from odoo import models, fields, api

class PrestadorServico(models.Model):
    _name = "prestador.servico"
    _description = "Prestador de Serviço"

    name = fields.Char(string="Nome", required=True)
    cpf_cnpj = fields.Char(string="CPF/CNPJ", required=True)
    celular = fields.Char(string="Celular")
    email = fields.Char(string="E-mail")
    categoria = fields.Selection([
        ('mecanico', 'Mecânico'),
        ('autoeletrico', 'Autoelétrico'),
        ('guincho', 'Guincho'),
    ], string="Categoria", required=True)

    cep = fields.Char(string="CEP")
    logradouro = fields.Char(string="Logradouro")
    numero = fields.Char(string="Número")
    complemento = fields.Char(string="Complemento")
    bairro = fields.Char(string="Bairro")
    cidade = fields.Char(string="Cidade")
    uf = fields.Char(string="UF")
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")

    ativo = fields.Boolean(string="Ativo", default=True)

    def action_toggle_status(self):
        for record in self:
            record.ativo = not record.ativo
