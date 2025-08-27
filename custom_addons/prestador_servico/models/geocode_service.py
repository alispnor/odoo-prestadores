from odoo import models, api
import requests
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class GeocodeService(models.TransientModel):
    _name = 'geocode.service'
    _description = 'Serviço de Geocodificação'

    @api.model
    def geocode_address(self, address_string, provider='nominatim'):
        """
        Geocodifica um endereço usando diferentes provedores
        
        Args:
            address_string (str): Endereço completo para geocodificar
            provider (str): Provedor a usar ('nominatim', 'viacep', 'google')
            
        Returns:
            dict: Resultado da geocodificação
        """
        if not address_string or not address_string.strip():
            return {'success': False, 'error': 'Endereço vazio'}

        # Tenta diferentes provedores em ordem de prioridade
        providers = [provider, 'nominatim', 'viacep'] if provider != 'nominatim' else ['nominatim', 'viacep']
        
        for current_provider in providers:
            try:
                if current_provider == 'nominatim':
                    result = self._geocode_nominatim(address_string)
                elif current_provider == 'viacep':
                    result = self._geocode_viacep(address_string)
                elif current_provider == 'google':
                    result = self._geocode_google(address_string)
                else:
                    continue
                    
                if result.get('success'):
                    result['provider'] = current_provider
                    return result
                    
            except Exception as e:
                _logger.warning(f"Erro no provedor {current_provider}: {str(e)}")
                continue
        
        return {'success': False, 'error': 'Todos os provedores falharam'}

    def _geocode_nominatim(self, address):
        """Geocodifica usando OpenStreetMap Nominatim"""
        url = "https://nominatim.openstreetmap.org/search"
        headers = {
            'User-Agent': 'OdooPrestadorServico/1.0 (alispnor@gmail.com)'
        }
        params = {
            'q': address,
            'format': 'json',   
            'limit': 1,
            'countrycodes': 'br'  # Limita ao Brasil
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                location = data[0]
                return {
                    'success': True,
                    'latitude': float(location.get('lat', 0)),
                    'longitude': float(location.get('lon', 0)),
                    'display_name': location.get('display_name', ''),
                    'provider': 'nominatim'
                }
            else:
                return {'success': False, 'error': 'Endereço não encontrado'}
                
        except requests.RequestException as e:
            _logger.error(f"Erro Nominatim: {str(e)}")
            return {'success': False, 'error': f'Erro de conexão: {str(e)}'}

    def _geocode_viacep(self, address):
        """Geocodifica usando ViaCEP (funciona melhor com CEPs brasileiros)"""
        # Extrai CEP do endereço se presente
        import re
        cep_match = re.search(r'\b\d{5}[-.]?\d{3}\b', address)
        
        if not cep_match:
            return {'success': False, 'error': 'CEP não encontrado no endereço'}
        
        cep = re.sub(r'[^0-9]', '', cep_match.group())
        
        try:
            # Busca dados do CEP
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('erro'):
                return {'success': False, 'error': 'CEP não encontrado'}
            
            # ViaCEP não retorna coordenadas, usa Nominatim como fallback
            full_address = f"{data.get('logradouro', '')}, {data.get('bairro', '')}, {data.get('localidade', '')}, {data.get('uf', '')}"
            return self._geocode_nominatim(full_address)
            
        except requests.RequestException as e:
            _logger.error(f"Erro ViaCEP: {str(e)}")
            return {'success': False, 'error': f'Erro ViaCEP: {str(e)}'}

    def _geocode_google(self, address):
        """
        Geocodifica usando Google Maps API
        Requer configuração da chave API no sistema
        """
        api_key = self.env['ir.config_parameter'].sudo().get_param('google.maps.api_key')
        
        if not api_key:
            return {'success': False, 'error': 'Google Maps API key não configurada'}
        
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': api_key,
            'region': 'br'  # Prefere resultados do Brasil
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                location = data['results'][0]['geometry']['location']
                return {
                    'success': True,
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'display_name': data['results'][0]['formatted_address'],
                    'provider': 'google'
                }
            else:
                return {'success': False, 'error': f"Google API: {data.get('status', 'Erro desconhecido')}"}
                
        except requests.RequestException as e:
            _logger.error(f"Erro Google Maps: {str(e)}")
            return {'success': False, 'error': f'Erro Google Maps: {str(e)}'}

    @api.model
    def batch_geocode(self, record_ids, model_name='prestador.servico'):
        """Geocodifica múltiplos registros em lote"""
        records = self.env[model_name].browse(record_ids)
        results = []
        
        for record in records:
            if hasattr(record, '_perform_geocoding'):
                record._perform_geocoding()
                results.append({
                    'id': record.id,
                    'status': record.geocode_status,
                    'lat': record.latitude,
                    'lng': record.longitude
                })
        
        return results
