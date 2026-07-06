from datetime import date

try:
    from .database import db
except ImportError:
    from database import db


# ─────────────────────────────────────────────────────────
# Tabela associativa (N:N) — declarada ANTES de Refeicao
# porque a classe Refeicao faz referência a ela pelo nome.
# Não é uma entidade do domínio, só armazena a relação.
# ─────────────────────────────────────────────────────────
refeicao_porcao = db.Table('refeicao_porcao',
    db.Column('refeicao_id', db.Integer,
              db.ForeignKey('refeicao.id'), primary_key=True),
    db.Column('porcao_id',   db.Integer,
              db.ForeignKey('porcao.id'),   primary_key=True)
)


class Categoria(db.Model):
    __tablename__ = 'categoria'

    id   = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)

    # Conveniência Python: categoria.porcoes → lista todas as porções
    porcoes = db.relationship('Porcao', backref='categoria', lazy=True)

    def to_dict(self):
        """Converte o objeto Python em dicionário serializável para JSON."""
        return {
            'id':   self.id,
            'nome': self.nome
        }


class Porcao(db.Model):
    __tablename__ = 'porcao'

    id                   = db.Column(db.Integer, primary_key=True)
    nome                 = db.Column(db.String(100), nullable=False)
    categoria_id         = db.Column(db.Integer,
                                     db.ForeignKey('categoria.id'),
                                     nullable=False)
    tipo_preparo         = db.Column(db.String(50))
    quantidade_disponivel = db.Column(db.Integer, default=1)
    data_preparo         = db.Column(db.Date, default=date.today)
    validade_estimada    = db.Column(db.Date)

    def to_dict(self):
        return {
            'id':                    self.id,
            'nome':                  self.nome,
            'categoria_id':          self.categoria_id,
            'categoria_nome':        self.categoria.nome,   # via backref
            'tipo_preparo':          self.tipo_preparo,
            'quantidade_disponivel': self.quantidade_disponivel,
            # Converte date → string ISO 8601 (ex: "2026-06-30")
            # pois JSON não tem tipo nativo para datas
            'data_preparo':       self.data_preparo.isoformat()
                                  if self.data_preparo else None,
            'validade_estimada':  self.validade_estimada.isoformat()
                                  if self.validade_estimada else None,
        }


class Refeicao(db.Model):
    __tablename__ = 'refeicao'

    id             = db.Column(db.Integer, primary_key=True)
    nome           = db.Column(db.String(100), nullable=False)
    data_planejada = db.Column(db.Date, default=date.today)

    # secondary aponta para a tabela associativa declarada acima
    porcoes = db.relationship('Porcao', secondary='refeicao_porcao',
                              backref='refeicoes')

    def to_dict(self):
        return {
            'id':             self.id,
            'nome':           self.nome,
            'data_planejada': self.data_planejada.isoformat()
                              if self.data_planejada else None,
            # Lista as porções que compõem esta refeição
            'porcoes': [p.to_dict() for p in self.porcoes]
        }
