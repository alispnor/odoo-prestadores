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



    @api.onchange('cep', 'logradouro', 'numero', 'cidade', 'uf', 'bairro')
    def _onchange_endereco(self):
        import logging, requests
        _logger = logging.getLogger(__name__)
        BASE_URL = "https://nominatim.openstreetmap.org/search"
        UA = "OdooPrestadorServico/1.0 (contato: alispnor@gmail.com)"  # ajuste

        for rec in self:
            cep = (rec.cep or "").replace("-", "").replace(".", "").strip()
            logradouro = (rec.logradouro or "").strip()
            numero = (rec.numero or "").strip()
            bairro = (rec.bairro or "").strip()
            cidade = (rec.cidade or "").strip()
            uf = (rec.uf or "").strip().upper()

            # Só tenta quando endereço está completo o suficiente
            if logradouro and numero and cidade and uf:
                endereco = ", ".join(filter(None, [f"{logradouro}", f"{numero}", bairro, cidade, uf, cep]))
                params = {"q": endereco, "format": "json", "limit": 1}
                headers = {"User-Agent": UA}
                try:
                    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=5)
                    resp.raise_for_status()
                    data = resp.json() or []
                    if data:
                        rec.latitude = float(data.get("lat") or 0.0)
                        rec.longitude = float(data.get("lon") or 0.0)
                        _logger.debug("Geocode OK: %s => (%s, %s)", endereco, rec.latitude, rec.longitude)
                    else:
                        _logger.info("Geocode vazio para: %s", endereco)
                        # opcional: não zerar em falha; comente as linhas abaixo se quiser manter valores anteriores
                        # rec.latitude = 0.0
                        # rec.longitude = 0.0
                except requests.RequestException as e:
                    _logger.warning("Erro Nominatim (%s): %s", endereco, e)
                    # opcional: não zerar em falha temporária
                    # rec.latitude = 0.0
                    # rec.longitude = 0.0
            else:
                # Endereço incompleto: defina comportamento (zerar ou manter)
                rec.latitude = 0.0
                rec.longitude = 0.0
