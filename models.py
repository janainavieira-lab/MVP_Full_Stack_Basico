from database import db

class Categoria(db.Model):
    __tablename__ = 'categoria'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

    # Relacionamento: uma categoria tem várias porções
    porcoes = db.relationship('Porcao', backref='categoria', lazy=True)

    from datetime import date

class Porcao(db.Model):
    __tablename__ = 'porcao'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    tipo_preparo = db.Column(db.String(50))
    quantidade_disponivel = db.Column(db.Integer, default=1)
    data_preparo = db.Column(db.Date, default=date.today)
    validade_estimada = db.Column(db.Date)

refeicao_porcao = db.Table('refeicao_porcao',
    db.Column('refeicao_id', db.Integer, db.ForeignKey('refeicao.id'), primary_key=True),
    db.Column('porcao_id', db.Integer, db.ForeignKey('porcao.id'), primary_key=True)
)

class Refeicao(db.Model):
    __tablename__ = 'refeicao'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_planejada = db.Column(db.Date, default=date.today)

    # Relacionamento N:N via tabela associativa (definida abaixo)
    porcoes = db.relationship('Porcao', secondary='refeicao_porcao', backref='refeicoes')

