# Prestador de Serviço - Módulo Odoo v17
Descrição
Módulo CRUD para gerenciamento de prestadores de serviço no Odoo v17 usando Docker.

🚀 Como rodar
    1. Subir o ambiente
    bash`
    docker-compose up -d`
    2. Acessar o sistema
    `URL: http://localhost:8069`
- 
    Banco: odoo-db

    Usuário: admin

    Senha:  sua senha 

3. Instalar o módulo
Ir em Apps → Update Apps List

Buscar "Prestador de Serviço"

Clicar em Install

- 📋 Funcionalidades
- ✅ CRUD completo (Create, Read, Update, Delete)

- 🔒 Bloquear/Desbloquear prestadores

- 📍 Geolocalização com coordenadas

- 📊 Campos do Prestador
- Dados Pessoais
    -  Nome

    - CPF/CNPJ

    - Celular

    - Email

    - Categoria (Mecânico, Autoelétrico, Guincho)

    - Endereço
    - CEP

    - Logradouro

    - Número

    - Complemento

    - Bairro

    - Cidade

    - UF

    - Latitude

    - Longitude

📁 Estrutura
text
    
    ├── docker-compose.yml
    ├── config/odoo.conf
    ├── custom_addons/prestador_servico/
    │   ├── __manifest__.py
    │   ├── models/prestador_servico.py
    │   ├── views/prestador_views.xml
    │   └── security/ir.model.access.csv
    └── README.md
    
🛠️ Requisitos
- Docker

- Docker Compose

- Odoo v17

- PostgreSQL

📞 Uso
- Menu: Prestadores → Prestadores de Serviço

- Criar: Botão "Novo"

- Bloquear: Botão "Arquivar"

- Editar: Clique no registro

- Excluir: Botão "Ação" → "Excluir"

## Desenvolvido para Odoo v17 com Docker

## 👨‍💻 Autor

**Ali Mohammed **  
[LinkedIn](https://www.linkedin.com/in/alialsalahi) 