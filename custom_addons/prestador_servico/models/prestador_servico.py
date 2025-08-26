from odoo import models, fields, api
from odoo.exceptions import UserError # type: ignore
import logging

_logger = logging.getLogger(__name__)


class PrestadorServico(models.Model):
    _name = "prestador.servico"
    _description = "Prestador de Serviço"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Para usar chatter

    name = fields.Char(string="Nome", required=True, tracking=True)
    cpf_cnpj = fields.Char(string="CPF/CNPJ", required=True)
    celular = fields.Char(string="Celular")
    email = fields.Char(string="E-mail")
    categoria = fields.Selection([
        ('mecanico', 'Mecânico'),
        ('autoeletrico', 'Autoelétrico'),
        ('guincho', 'Guincho'),
    ], string="Categoria", required=True, tracking=True)

    # Campos de endereço
    cep = fields.Char(string="CEP")
    logradouro = fields.Char(string="Logradouro")
    numero = fields.Char(string="Número")
    complemento = fields.Char(string="Complemento")
    bairro = fields.Char(string="Bairro")
    cidade = fields.Char(string="Cidade")
    uf = fields.Selection([
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
        ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
    ], string="UF")
    
    # Coordenadas geográficas
    latitude = fields.Float(string="Latitude", digits=(10, 6))
    longitude = fields.Float(string="Longitude", digits=(10, 6))
    geocode_status = fields.Selection([
        ('pending', 'Pendente'),
        ('success', 'Sucesso'),
        ('failed', 'Falhou'),
        ('incomplete', 'Endereço Incompleto')
    ], string="Status Geocodificação", default='pending', readonly=True, tracking=True)
    last_geocode_attempt = fields.Datetime(string="Última Tentativa", readonly=True)

    ativo = fields.Boolean(string="Ativo", default=True, tracking=True)

    def action_toggle_status(self):
        """Alterna o status ativo/inativo do prestador"""
        for record in self:
            record.ativo = not record.ativo

    def action_force_geocode(self):
        """Força uma nova tentativa de geocodificação"""
        for record in self:
            record._perform_geocoding()

    def action_open_google_maps(self):
        """Abre localização no Google Maps"""
        if self.latitude and self.longitude:
            url = f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        else:
            raise UserError("Coordenadas não disponíveis para este prestador.")

    def action_open_openstreetmap(self):
        """Abre localização no OpenStreetMap"""
        if self.latitude and self.longitude:
            url = f"https://www.openstreetmap.org/?mlat={self.latitude}&mlon={self.longitude}&zoom=16"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        else:
            raise UserError("Coordenadas não disponíveis para este prestador.")

    @api.onchange('cep', 'logradouro', 'numero', 'cidade', 'uf', 'bairro')
    def _onchange_endereco(self):
        """Detecta mudanças no endereço e marca para nova geocodificação"""
        for record in self:
            if record._should_geocode():
                record.geocode_status = 'pending'
                # Agenda geocodificação para depois do save
                record._perform_geocoding()

    def _should_geocode(self):
        """Verifica se deve tentar geocodificar o endereço"""
        required_fields = [self.logradouro, self.numero, self.cidade, self.uf]
        return all(field and field.strip() for field in required_fields)

    def _perform_geocoding(self):
        """Executa a geocodificação usando o serviço"""
        if not self._should_geocode():
            self.geocode_status = 'incomplete'
            self.latitude = 0.0
            self.longitude = 0.0
            return

        geocode_service = self.env['geocode.service']
        result = geocode_service.geocode_address(self._build_address_string())
        
        self.last_geocode_attempt = fields.Datetime.now()
        
        if result.get('success'):
            self.latitude = result.get('latitude', 0.0)
            self.longitude = result.get('longitude', 0.0)
            self.geocode_status = 'success'
            _logger.info(f"Geocodificação sucesso para {self.name}: ({self.latitude}, {self.longitude})")
        else:
            self.geocode_status = 'failed'
            _logger.warning(f"Geocodificação falhou para {self.name}: {result.get('error')}")

    def _build_address_string(self):
        """Constrói string do endereço para geocodificação"""
        parts = []
        
        if self.logradouro and self.numero:
            parts.append(f"{self.logradouro}, {self.numero}")
        
        if self.bairro:
            parts.append(self.bairro)
            
        if self.cidade:
            parts.append(self.cidade)
            
        if self.uf:
            parts.append(self.uf)
            
        if self.cep:
            cep_clean = self.cep.replace("-", "").replace(".", "").strip()
            if cep_clean:
                parts.append(cep_clean)
        
        return ", ".join(parts)

    @api.model
    def cron_geocode_pending(self):
        """Método para CRON processar registros pendentes"""
        pending_records = self.search([('geocode_status', '=', 'pending')], limit=50)
        for record in pending_records:
            record._perform_geocoding()
            self._cr.commit()  # Commit a cada registro para evitar perda em caso de erro
