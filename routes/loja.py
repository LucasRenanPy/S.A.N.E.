from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    url_for
)

from extensions import mysql

import logging
logger = logging.getLogger(__name__)

loja_bp = Blueprint("loja", __name__)


@loja_bp.route('/loja/<identificador>')
def loja_publica(identificador):

    cur = mysql.connection.cursor()

    try:

        # Busca a empresa pelo identificador público
        cur.execute(
            """
            SELECT id, nome
            FROM empresas
            WHERE identificador_url = %s
            """,
            (identificador,)
        )

        empresa = cur.fetchone()

        if not empresa:
            logger.warning(
                "Tentativa de acesso à loja inexistente: %s",
                identificador
            )

            flash("Empresa não encontrada.", "warning")
            return redirect(url_for("auth.login"))

        empresa_id = empresa["id"]
        nome_empresa = empresa["nome"]

        logger.info(
            "Loja pública acessada: %s",
            identificador
        )

        # Busca produtos e serviços da empresa
        cur.execute(
            """
            SELECT
                id,
                nome,
                categoria,
                descricao,
                preco_base,
                preco_promocional,
                estoque,
                imagem,
                tipo,
                promocao_percentual,
                promocao_data_limite,
                permitir_agendamento,
                duracao_minutos
            FROM produtos
            WHERE empresa_id = %s
            ORDER BY nome
            """,
            (empresa_id,)
        )

        produtos = cur.fetchall()

    except Exception:

        logger.exception(
            "Erro ao carregar loja pública: %s",
            identificador
        )

        raise

    finally:
        cur.close()

    return render_template(
        "loja/publica.html",
        nome=nome_empresa,
        identificador=identificador,
        produtos=produtos
    )