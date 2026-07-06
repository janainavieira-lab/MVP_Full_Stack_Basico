from flask_sqlalchemy import SQLAlchemy

# Objeto central que gerencia toda comunicação com o SQLite.
# Criado aqui e importado pelos outros módulos para evitar
# referências circulares (importar A dentro de B que importa A).
db = SQLAlchemy()
