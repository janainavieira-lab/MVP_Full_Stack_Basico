from flask import Flask, render_template_string
from flask_cors import CORS
from flasgger import Swagger

try:
    from .database import db
    from .models import Categoria, Porcao, Refeicao  # garante que os models são lidos antes do create_all()
    from .routes.categorias import categorias_bp
    from .routes.porcoes import porcoes_bp
    from .routes.refeicoes import refeicoes_bp
except ImportError:
    from database import db
    from models import Categoria, Porcao, Refeicao  # garante que os models são lidos antes do create_all()
    from routes.categorias import categorias_bp
    from routes.porcoes import porcoes_bp
    from routes.refeicoes import refeicoes_bp


# Configuração central da especificação OpenAPI.
# Este dicionário gera o cabeçalho exibido na página /apidocs.
# Seguindo a estrutura obrigatória do OpenAPI 2.0 (formato suportado
# pelo Flasgger por padrão).
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/swagger-json",   # URL do JSON bruto da especificação
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": False,
    "specs_route": "/swagger-json"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "MarmitApp API",
        "description": (
            "API REST para gerenciamento de meal prep. "
            "Permite cadastrar porções congeladas por categoria, "
            "montar refeições balanceadas e obter sugestões automáticas."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "Desenvolvedor",
            "email": "dev@marmitapp.local"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "host": "127.0.0.1:5000",
    "basePath": "/",
    "schemes": ["http"],
    # Tags agrupam as rotas na interface visual — cada tag vira uma seção
    "tags": [
        {
            "name": "Categorias",
            "description": "Gerenciamento das categorias de porções (ex: Carboidrato, Proteína)"
        },
        {
            "name": "Porções",
            "description": "Gerenciamento das porções congeladas disponíveis no freezer"
        },
        {
            "name": "Refeições",
            "description": "Montagem e consulta de refeições compostas por porções"
        }
    ],
    "consumes": ["application/json"],   # formato que a API aceita nas requisições
    "produces": ["application/json"]    # formato que a API retorna nas respostas
}


def create_app():
    """
    Factory function: padrão recomendado pela documentação do Flask.
    Em vez de criar o app no escopo global, encapsulamos a criação
    em uma função — facilita testes unitários e configurações diferentes
    (desenvolvimento vs produção).
    """
    app = Flask(__name__)

    # Configuração do banco SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meal_prep.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Conecta o objeto db a esta aplicação
    db.init_app(app)

    # CORS: permite que o front-end (arquivo local) acesse a API
    CORS(app)

    # Inicializa o Swagger com a configuração e o template definidos acima.
    Swagger(app, config=swagger_config, template=swagger_template)

    @app.route('/apidocs')
    def apidocs():
        return render_template_string("""
        <!doctype html>
        <html lang="pt-BR">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>MarmitApp API - Swagger</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
            <style>
                body {
                    margin: 0;
                    background: #0f172a;
                    font-family: Arial, sans-serif;
                    color: #e2e8f0;
                }
                .hero {
                    padding: 24px 32px;
                    background: linear-gradient(135deg, #1d4ed8, #0f766e);
                    box-shadow: 0 4px 16px rgba(0,0,0,.2);
                }
                .hero h1 {
                    margin: 0 0 8px;
                    font-size: 1.7rem;
                }
                .hero p {
                    margin: 0;
                    opacity: 0.95;
                }
                #swagger-ui {
                    padding: 16px;
                    background: #fff;
                }
            </style>
        </head>
        <body>
            <div class="hero">
                <h1>MarmitApp API</h1>
                <p>Documentação interativa para categorias, porções, refeições e sugestões.</p>
            </div>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
                window.onload = () => {
                    SwaggerUIBundle({
                        url: "/swagger-json",
                        dom_id: "#swagger-ui",
                        deepLinking: true,
                        presets: [SwaggerUIBundle.presets.apis],
                        layout: "BaseLayout",
                        docExpansion: "list",
                        persistAuthorization: true,
                        supportedSubmitMethods: ["get", "post", "put", "delete"]
                    });
                };
            </script>
        </body>
        </html>
        """)

    # Registra os blueprints
    app.register_blueprint(categorias_bp)
    app.register_blueprint(porcoes_bp)
    app.register_blueprint(refeicoes_bp)

    # Cria as tabelas no banco se ainda não existirem
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
