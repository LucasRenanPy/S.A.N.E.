from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import json

from extensions import mysql, get_cursor

import os

from werkzeug.utils import secure_filename

from uuid import uuid4

from flask import current_app

import logging

logger = logging.getLogger(__name__)

def salvar_imagem(imagem):
    if not imagem or imagem.filename == "":
        return None
    
    if "." not in imagem.filename:
        raise ValueError("Arquivo inválido.")

    extensao = imagem.filename.rsplit(".", 1)[1].lower()

    if extensao not in current_app.config["ALLOWED_EXTENSIONS"]:
        raise ValueError("Formato de imagem inválido.")

    nome_arquivo = f"{uuid4().hex}.{extensao}"

    caminho = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        nome_arquivo
    )

    imagem.save(caminho)

    return f"uploads/{nome_arquivo}"

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/produto/cadastrar", methods=["POST"])
def cadastrar_produto():
    
    logger.info("Entrou em cadastrar_produto")
    
    if "usuario_id" not in session:
        flash("Faça login.", "warning")
        return redirect(url_for("auth.login"))
    
    tipo = request.form.get("tipo")

    nome = request.form.get("nome", "").strip()

    categoria = request.form.get("categoria", "").strip()
    
    descricao = request.form.get("descricao", "").strip()

    try:
        preco_base = float(request.form.get("preco_base") or 0)
    except ValueError:
        flash("Preço inválido.", "warning")
        return redirect(request.referrer)

    if tipo == "produto":
        try:
            estoque = int(request.form.get("estoque") or 0)
        except ValueError:
            flash("Estoque inválido.", "warning")
            return redirect(request.referrer)
    else:
        estoque = 0

    imagem = request.files.get("imagem")
    
    try:
        caminho_imagem = salvar_imagem(imagem)
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(request.referrer)

    permitir_agendamento = bool(request.form.get("permitir_agendamento"))

    try:
        duracao_minutos = int(request.form.get("duracao_minutos") or 60)
    except ValueError:
        duracao_minutos = 60
    
    if not all([nome, categoria]):
        flash("Preencha todos os campos obrigatórios.", "warning")
        return redirect(request.referrer)
    
    if preco_base < 0:
        flash("O preço não pode ser negativo.", "warning")
        return redirect(request.referrer)
    
    if estoque < 0:
        flash("O estoque não pode ser negativo.", "warning")
        return redirect(request.referrer)
    
    cur = get_cursor()
    
    try:
        
        cur.execute("""SELECT id FROM empresas WHERE usuario_id = %s""", (session["usuario_id"],))
        empresa = cur.fetchone()
    
        if not empresa:
            flash("Empresa não encontrada.", "danger")
            return redirect(url_for("auth.login"))
        
        empresa_id = empresa["id"]
        
        cur.execute(
            """INSERT INTO produtos(empresa_id, nome, categoria, descricao, preco_base, estoque, imagem, tipo, permitir_agendamento, duracao_minutos)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)""",
            (
                empresa_id,
                nome,
                categoria,
                descricao,
                preco_base,
                estoque,
                caminho_imagem,
                tipo,
                permitir_agendamento,
                duracao_minutos
            )
        )

        mysql.connection.commit()
        logger.info("Produto '%s' cadastrado na empresa %s", nome, empresa_id)
        
    except Exception:
        mysql.connection.rollback()
        logger.exception("Erro ao cadastrar produto '%s'", nome)
        raise
    
    finally:
        cur.close()
    
    flash("Produto cadastrado com sucesso!", "success")
    return redirect(request.referrer)

@produtos_bp.route("/produto/editar/<int:id>", methods=["POST"])
def editar_produto(id):

    if "usuario_id" not in session:
        flash("Faça login.", "warning")
        return redirect(url_for("auth.login"))

    nome = request.form.get("nome", "").strip()
    categoria = request.form.get("categoria", "").strip()
    descricao = request.form.get("descricao", "").strip()
    imagem = request.files.get("imagem")
    
    dias_disponiveis = request.form.getlist("dias_disponiveis")
    dias_json = json.dumps(dias_disponiveis)
    
    horarios_lista = [
    horario.strip()
    for horario in request.form.getlist("horarios_disponiveis")
    if horario.strip()
]

    horarios_json = json.dumps(horarios_lista)

    try:
        preco_base = float(request.form.get("preco_base") or 0)
    except ValueError:
        flash("Preço inválido.", "warning")
        return redirect(request.referrer)

    try:
        estoque = int(request.form.get("estoque") or 0)
    except ValueError:
        estoque = 0

    permitir_agendamento = bool(
        request.form.get("permitir_agendamento")
    )

    try:
        duracao_minutos = int(
            request.form.get("duracao_minutos") or 60
        )
    except ValueError:
        duracao_minutos = 60

    if not nome or not categoria:
        flash("Preencha os campos obrigatórios.", "warning")
        return redirect(request.referrer)

    if preco_base < 0:
        flash("O preço não pode ser negativo.", "warning")
        return redirect(request.referrer)

    if estoque < 0:
        flash("O estoque não pode ser negativo.", "warning")
        return redirect(request.referrer)

    cur = get_cursor()

    try:

        # Descobre a empresa do usuário
        cur.execute(
            """
            SELECT id
            FROM empresas
            WHERE usuario_id = %s
            """,
            (session["usuario_id"],)
        )

        empresa = cur.fetchone()

        if not empresa:
            flash("Empresa não encontrada.", "danger")
            return redirect(url_for("auth.login"))

        empresa_id = empresa["id"]

        # Confirma que o produto pertence à empresa
        cur.execute(
            """
            SELECT id, tipo, imagem
            FROM produtos
            WHERE id = %s
            AND empresa_id = %s
            """,
            (id, empresa_id)
        )

        produto = cur.fetchone()

        if not produto:
            flash("Produto ou serviço não encontrado.", "danger")
            return redirect(request.referrer)

        tipo = produto["tipo"]
        
        caminho_imagem = None

        if imagem and imagem.filename:
            try:
                caminho_imagem = salvar_imagem(imagem)
            except ValueError as e:
                flash(str(e), "warning")
                return redirect(request.referrer)

        # Atualização específica para produto
        if tipo == "produto":
           

            if caminho_imagem:
                cur.execute(
                    """
                    UPDATE produtos
                    SET nome = %s,
                        categoria = %s,
                        descricao = %s,
                        preco_base = %s,
                        estoque = %s,
                        imagem = %s
                    WHERE id = %s
                    AND empresa_id = %s
                    """,
                    (
                        nome,
                        categoria,
                        descricao,
                        preco_base,
                        estoque,
                        caminho_imagem,
                        id,
                        empresa_id
                    )
                )
            else:
                cur.execute(
                    """
                    UPDATE produtos
                    SET nome = %s,
                        categoria = %s,
                        descricao = %s,
                        preco_base = %s,
                        estoque = %s
                    WHERE id = %s
                    AND empresa_id = %s
                    """,
                    (
                        nome,
                        categoria,
                        descricao,
                        preco_base,
                        estoque,
                        id,
                        empresa_id
                    )
                )

        # Atualização específica para serviço
        else:

            if caminho_imagem:
                cur.execute(
                    """
                    UPDATE produtos
                    SET nome = %s,
                        categoria = %s,
                        descricao = %s,
                        preco_base = %s,
                        permitir_agendamento = %s,
                        duracao_minutos = %s,
                        imagem = %s,
                        dias_disponiveis = %s,
                        horarios_disponiveis = %s
                    WHERE id = %s
                    AND empresa_id = %s
                    """,
                    (
                        nome,
                        categoria,
                        descricao,
                        preco_base,
                        permitir_agendamento,
                        duracao_minutos,
                        caminho_imagem,
                        dias_json,
                        horarios_json,
                        id,
                        empresa_id
                    )
                )

            else:
                cur.execute(
                    """
                    UPDATE produtos
                    SET nome = %s,
                        categoria = %s,
                        descricao = %s,
                        preco_base = %s,
                        permitir_agendamento = %s,
                        duracao_minutos = %s,
                        dias_disponiveis = %s,
                        horarios_disponiveis = %s
                    WHERE id = %s
                    AND empresa_id = %s
                    """,
                    (
                        nome,
                        categoria,
                        descricao,
                        preco_base,
                        permitir_agendamento,
                        duracao_minutos,
                        dias_json,
                        horarios_json,
                        id,
                        empresa_id
                    )
                )
            
        mysql.connection.commit()

        logger.info(
                "Item %s atualizado pela empresa %s",
                id,
                empresa_id
            )

        flash("Item atualizado com sucesso!", "success")
            
    except Exception:
        
        mysql.connection.rollback()
        logger.exception(
            "Erro ao editar item %s",
            id
        )
        raise

    finally:
        cur.close()

    return redirect(request.referrer)

@produtos_bp.route("/produto/excluir/<int:id>", methods=["POST"])
def excluir_produto(id):

    if "usuario_id" not in session:
        flash("Faça login.", "warning")
        return redirect(url_for("auth.login"))

    cur = get_cursor()

    try:

        cur.execute(
            """
            SELECT id
            FROM empresas
            WHERE usuario_id = %s
            """,
            (session["usuario_id"],)
        )

        empresa = cur.fetchone()

        if not empresa:
            flash("Empresa não encontrada.", "danger")
            return redirect(url_for("auth.login"))

        empresa_id = empresa["id"]

        cur.execute(
            """
            SELECT id
            FROM produtos
            WHERE id = %s
            AND empresa_id = %s
            """,
            (id, empresa_id)
        )

        produto = cur.fetchone()

        if not produto:
            flash("Produto ou serviço não encontrado.", "danger")
            return redirect(request.referrer)

        cur.execute(
            """
            DELETE FROM produtos
            WHERE id = %s
            AND empresa_id = %s
            """,
            (id, empresa_id)
        )

        mysql.connection.commit()

        logger.info(
            "Item %s excluído pela empresa %s",
            id,
            empresa_id
        )

        flash("Item excluído com sucesso!", "success")

    except Exception:

        mysql.connection.rollback()

        logger.exception(
            "Erro ao excluir item %s",
            id
        )

        raise

    finally:
        cur.close()

    return redirect(request.referrer)