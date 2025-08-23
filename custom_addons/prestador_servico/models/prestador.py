from odoo import models, fields, api
import requests

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




    @api.onchange('cep', 'logradouro', 'numero', 'cidade', 'uf')
    def _onchange_endereco(self):
        print("\n=== Método onchange_endereco sendo executado ===")
        """
        Faz a requisição para a API Nominatim para obter latitude e longitude.
        """
        BASE_URL = "https://nominatim.openstreetmap.org/search"
        
        endereco_completo = f"{self.logradouro}, {self.numero}, {self.bairro}, {self.cidade}, {self.uf}, {self.cep}"
        print(f"Endereço a ser pesquisado: {endereco_completo}")
        
        if self.logradouro and self.numero and self.cidade and self.uf:
            try:
                params = {
                    'q': endereco_completo,
                    'format': 'json',
                    'limit': 1,
                }
                
                # É uma boa prática definir um User-Agent para a API
                headers = {
                    'User-Agent': 'OdooPrestadorServicoModule' 
                }
                
                response = requests.get(BASE_URL, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                print(f"Resposta da API Nominatim: {data}")
                
                if data:
                    result = data[0]
                    self.latitude = float(result.get('lat'))
                    self.longitude = float(result.get('lon'))
                    print(f"Latitude e Longitude encontradas: {self.latitude}, {self.longitude}")

                else:
                    print("API retornou uma lista vazia. Endereço não encontrado.")
                    self.latitude = 0.0
                    self.longitude = 0.0
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição da API: {e}")
                self.latitude = 0.0
                self.longitude = 0.0
        else:
            print("AVISO: Campos de endereço incompletos, onchange não fará a requisição.")

