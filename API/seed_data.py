from datetime import date

from app import create_app
from models import Categoria, Porcao
from database import db


def seed_data():
    app = create_app()
    with app.app_context():
        categorias = [
            {
                "nome": "Carboidrato",
                "porcoes": [
                    ("Arroz cozido", "Cozido", 4, date(2026, 7, 1), date(2026, 7, 20)),
                    ("Batata assada", "Assado", 3, date(2026, 7, 2), date(2026, 7, 21)),
                    ("Macarrão alho e óleo", "Macerado", 2, date(2026, 7, 3), date(2026, 7, 22)),
                    ("Purê de batata", "Cozido", 5, date(2026, 7, 4), date(2026, 7, 23)),
                    ("Quinoa", "Cozido", 2, date(2026, 7, 5), date(2026, 7, 24)),
                ],
            },
            {
                "nome": "Proteína",
                "porcoes": [
                    ("Frango desfiado", "Grelhado", 4, date(2026, 7, 1), date(2026, 7, 19)),
                    ("Carne moída", "Cozida", 3, date(2026, 7, 2), date(2026, 7, 20)),
                    ("Peito de frango", "Assado", 2, date(2026, 7, 3), date(2026, 7, 21)),
                    ("Tilápia", "Grelhada", 3, date(2026, 7, 4), date(2026, 7, 22)),
                    ("Ovo cozido", "Cozido", 6, date(2026, 7, 5), date(2026, 7, 23)),
                ],
            },
            {
                "nome": "Vegetal",
                "porcoes": [
                    ("Brócolis", "Cozido", 4, date(2026, 7, 1), date(2026, 7, 18)),
                    ("Cenoura baby", "Assada", 5, date(2026, 7, 2), date(2026, 7, 19)),
                    ("Abobrinha grelhada", "Grelhada", 3, date(2026, 7, 3), date(2026, 7, 20)),
                    ("Mix de legumes", "Refogado", 2, date(2026, 7, 4), date(2026, 7, 21)),
                    ("Espinafre salteado", "Salteado", 4, date(2026, 7, 5), date(2026, 7, 22)),
                ],
            },
            {
                "nome": "Prato Pronto",
                "porcoes": [
                    ("Lasanha congelada", "Assada", 2, date(2026, 7, 1), date(2026, 7, 25)),
                    ("Feijão tropeiro", "Cozido", 3, date(2026, 7, 2), date(2026, 7, 24)),
                    ("Strogonoff de carne", "Cozido", 2, date(2026, 7, 3), date(2026, 7, 23)),
                    ("Pizza de frango", "Assada", 2, date(2026, 7, 4), date(2026, 7, 22)),
                    ("Taco de carne", "Frito", 3, date(2026, 7, 5), date(2026, 7, 21)),
                ],
            },
            {
                "nome": "Sobremesa",
                "porcoes": [
                    ("Pudim de leite", "Assado", 3, date(2026, 7, 1), date(2026, 7, 17)),
                    ("Salada de frutas", "Cru", 4, date(2026, 7, 2), date(2026, 7, 18)),
                    ("Banana caramelada", "Caramelizada", 2, date(2026, 7, 3), date(2026, 7, 19)),
                    ("Mousse de maracujá", "Gelado", 3, date(2026, 7, 4), date(2026, 7, 20)),
                    ("Pavê de chocolate", "Gelado", 2, date(2026, 7, 5), date(2026, 7, 21)),
                ],
            },
        ]

        db.create_all()

        for grupo in categorias:
            categoria = Categoria.query.filter_by(nome=grupo["nome"]).first()
            if not categoria:
                categoria = Categoria(nome=grupo["nome"])
                db.session.add(categoria)
                db.session.flush()

            existentes = {p.nome.lower(): p for p in categoria.porcoes}
            for nome, tipo, quantidade, data_preparo, validade in grupo["porcoes"]:
                if nome.lower() not in existentes:
                    porcao = Porcao(
                        nome=nome,
                        categoria_id=categoria.id,
                        tipo_preparo=tipo,
                        quantidade_disponivel=quantidade,
                        data_preparo=data_preparo,
                        validade_estimada=validade,
                    )
                    db.session.add(porcao)
                    existentes[nome.lower()] = porcao

        db.session.commit()

        print("Dados iniciais cadastrados com sucesso.")
        for categoria in Categoria.query.order_by(Categoria.id).all():
            print(f"{categoria.nome}: {len(categoria.porcoes)} porções")


if __name__ == "__main__":
    seed_data()
