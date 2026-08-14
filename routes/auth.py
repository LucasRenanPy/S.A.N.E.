
from flask import (
    Blueprint,
    flash,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from extensions import mysql, bcrypt

import logging
logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    logger.info("Entrou na função login")

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()

        logger.info("Tentativa de login para %s", email)

        cur = mysql.connection.cursor()
        
        try:
            cur.execute("SELECT id, senha_hash FROM usuarios WHERE email = %s", (email,))
            user = cur.fetchone()

            logger.debug("Resultado da consulta: %s", user)

            if user and bcrypt.check_password_hash(user[1], senha):
                logger.info("Login realizado com sucesso para %s", email)
                session['usuario_id'] = user[0]

                # Busca a empresa vinculada ao usuário autenticado
                cur.execute("SELECT identificador_url FROM empresas WHERE usuario_id = %s", (user[0],))
                empresa = cur.fetchone()
                if empresa:
                    return redirect(f'/{empresa[0]}/admin')
                else:
                    flash("Empresa não vinculada ao usuário.", "danger")
                    return redirect(url_for("auth.login"))
            else:
                logger.warning("Falha de login para %s", email)
                flash("Login inválido.", "danger")
                return redirect(url_for("auth.login"))
        finally:
            cur.close()

    return render_template('auth/login.html')

@auth_bp.route('/cadastrar', methods=['POST'])
def cadastrar():
    
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip().lower()
    senha = request.form.get('senha', '').strip()
    senha2 = request.form.get("senha2", "").strip()
    identificador = request.form.get('identificador_url', '').strip().lower().replace(" ", "-")
    
    logger.info("Tentativa de cadastro para %s", email)

    if not nome or not email or not senha or not identificador:
        flash("Preencha todos os campos obrigatórios.", "warning")
        return redirect(url_for("auth.login"))
    
    if len(senha) < 8:
            flash("A senha deve possuir pelo menos 8 caracteres.", "warning")
            return redirect(url_for("auth.login"))
    
    if senha != senha2:
        flash("As senhas não coincidem.", "warning")
        return redirect(url_for("auth.login"))

    cur = mysql.connection.cursor()
    
    try:
    
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        
        if cur.fetchone():
            flash("E-mail já cadastrado.", "warning")
            return redirect(url_for("auth.login"))
        
        cur.execute(
            "SELECT id FROM empresas WHERE identificador_url = %s",
            (identificador,)
            )

        if cur.fetchone():
            flash("Identificador de URL já em uso.", "warning")
            return redirect(url_for("auth.login"))
    
        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        
        cur.execute("INSERT INTO usuarios (email, senha_hash) VALUES (%s, %s)", (email, senha_hash))

        usuario_id = cur.lastrowid
        

        cur.execute("INSERT INTO empresas (usuario_id, nome, identificador_url) VALUES (%s, %s, %s)", (usuario_id, nome, identificador))
        mysql.connection.commit()
        logger.info("Usuário %s cadastrou a empresa %s", email, identificador)
        
    except Exception:
        mysql.connection.rollback()
        logger.exception("Erro ao cadastrar empresa %s", identificador)
        raise
        
    finally:
        cur.close()
        
    flash("Cadastro realizado com sucesso!", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route("/logout")
def logout():
    logger.info(
    "Usuário %s realizou logout",
    session.get("usuario_id")
)
    session.clear()
    return redirect(url_for("auth.login"))