from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    session,
    url_for
)


from extensions import mysql, get_cursor

import logging
logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/<identificador>/admin')
def painel_admin(identificador):
    if 'usuario_id' not in session:
        flash("Faça login para continuar.", "warning")
        return redirect(url_for("auth.login"))

    cur = get_cursor()
    
    try:
        cur.execute("SELECT id, nome FROM empresas WHERE identificador_url = %s AND usuario_id = %s", (identificador, session['usuario_id']))
    
        empresa = cur.fetchone()
    
        if not empresa:
            logger.warning("Usuário %s tentou acessar %s", session["usuario_id"], identificador,)
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for("auth.login"))

        empresa_id = empresa["id"]
        nome_empresa = empresa["nome"]
        
        logger.info("Painel administrativo acessado (%s)", identificador)
    
        cur.execute("""SELECT
                    id, 
                    nome,
                    categoria,
                    preco_base,
                    estoque,
                    imagem
                    FROM produtos WHERE empresa_id = %s
                    AND tipo = 'produto' 
                    ORDER BY nome
                    """, (empresa_id,))
    
        produtos = cur.fetchall()
        
        logger.info(
            "Produtos encontrados: %s",
            produtos
                )
        
        cur.execute("""SELECT
                    id, 
                    nome,
                    categoria,
                    preco_base,
                    imagem,
                    permitir_agendamento,
                    duracao_minutos
                    FROM produtos WHERE empresa_id = %s
                    AND tipo = 'servico' 
                    ORDER BY nome
                    """, (empresa_id,))
        
        servicos = cur.fetchall()
        
        cur.execute("""SELECT
                    p.nome AS produto_nome,
                    v.quantidade,
                    v.metodo_pagamento,
                    v.valor_total,
                    v.status_pagamento,
                    v.data
                    FROM vendas v
                    JOIN produtos p
                    ON p.id = v.item_id
                    WHERE p.empresa_id = %s
                    AND p.tipo = 'produto'
                    ORDER BY v.data DESC""", (empresa_id,))

        vendas_produtos = cur.fetchall()
        
        cur.execute("""SELECT
                    p.nome AS produto_nome,
                    v.metodo_pagamento,
                    v.valor_total,
                    v.status_pagamento,
                    v.data
                    FROM vendas v
                    JOIN produtos p
                    ON p.id = v.item_id
                    WHERE p.empresa_id = %s
                    AND p.tipo = 'servico'
                    ORDER BY v.data DESC""", (empresa_id,))

        vendas_servicos = cur.fetchall()
        
    except Exception:
        logger.exception("Erro ao carregar painel administrativo (%s)", identificador)
        raise
    
    finally:
        cur.close()

    return render_template(
    "admin/painel.html",
    nome=nome_empresa,
    identificador=identificador,
    produtos=produtos,
    servicos=servicos,
    vendas_produtos=vendas_produtos,
    vendas_servicos=vendas_servicos
)