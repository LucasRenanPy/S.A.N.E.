from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    url_for,
    jsonify,
    request
)

from datetime import datetime, timedelta

from utils import (
    normalizar,
    parse_list_field,
    to_minutes,
    safe_parse_date
)

from extensions import get_cursor, mysql

from MySQLdb import IntegrityError

import logging
logger = logging.getLogger(__name__)

loja_bp = Blueprint("loja", __name__)


@loja_bp.route('/loja/<identificador>')
def loja_publica(identificador):

    cur = get_cursor()

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
    
@loja_bp.route('/horarios_disponiveis/<int:servico_id>/<data>')
def horarios_disponiveis(servico_id, data):

    cur = get_cursor()

    try:
        cur.execute(
            """
            SELECT
                duracao_minutos,
                horarios_disponiveis,
                dias_disponiveis,
                permitir_agendamento
            FROM produtos
            WHERE id = %s
            """,
            (servico_id,)
        )

        servico = cur.fetchone()

        if not servico or not servico["permitir_agendamento"]:
            return jsonify([])

        duracao_target = int(
            servico["duracao_minutos"] or 60
        )

        horarios_base = parse_list_field(
            servico["horarios_disponiveis"] or []
        )

        dias_db = parse_list_field(
            servico["dias_disponiveis"] or []
        )

        dias_normalizados = [
            normalizar(dia)
            for dia in dias_db
        ]

        data_obj = safe_parse_date(data)

        if not data_obj:
            return jsonify([])

        weekday_map_pt = [
            "segunda",
            "terca",
            "quarta",
            "quinta",
            "sexta",
            "sabado",
            "domingo"
        ]

        dia_semana_normalizado = weekday_map_pt[
            data_obj.weekday()
        ]

        if dia_semana_normalizado not in dias_normalizados:
            return jsonify([])

        cur.execute(
            """
            SELECT hora, servico_id
            FROM agendamentos
            WHERE data = %s
            """,
            (data,)
        )

        agendamentos = cur.fetchall()
        
        logger.info(
            "AGENDAMENTOS ENCONTRADOS PARA %s: %s",
            data,
            agendamentos
        )

        ocupados = []

        for ag in agendamentos:

            hora = ag["hora"]
            sid = ag["servico_id"]

            if hora is None or not sid:
                continue

            try:

                # Converte TIME retornado pelo MySQL
                # para minutos desde 00:00
                if isinstance(hora, timedelta):

                    total_segundos = int(
                        hora.total_seconds()
                    )

                    start_min = total_segundos // 60

                else:

                    hora_str = str(hora)[:5]

                    start_min = to_minutes(hora_str)

                # Busca a duração do serviço agendado
                cur.execute(
                    """
                    SELECT duracao_minutos
                    FROM produtos
                    WHERE id = %s
                    """,
                    (sid,)
                )

                resultado = cur.fetchone()

                dur_ag = (
                    int(resultado["duracao_minutos"])
                    if resultado and resultado["duracao_minutos"]
                    else 60
                )

                fim_min = start_min + dur_ag

                ocupados.append(
                    (start_min, fim_min)
                )

                logger.info(
                    "OCUPADO ADICIONADO: %s-%s | serviço=%s",
                    start_min,
                    fim_min,
                    sid
                )

            except Exception:

                logger.exception(
                    "ERRO PROCESSANDO AGENDAMENTO: hora=%s, servico=%s",
                    hora,
                    sid
                )

                continue

        horarios_livres = []
        
        logger.info(
            "HORÁRIOS BASE: %s",
            horarios_base
        )

        logger.info(
            "HORÁRIOS OCUPADOS: %s",
            ocupados
        )

        for horario in horarios_base:

            horario = horario.strip()

            try:
                inicio = to_minutes(horario)
                fim = inicio + duracao_target
                
                logger.info(
                    "TESTANDO HORÁRIO: %s | %s-%s",
                    horario,
                    inicio,
                    fim
                )

                conflito = False

                for ocupado_inicio, ocupado_fim in ocupados:

                    if not (
                        fim <= ocupado_inicio
                        or inicio >= ocupado_fim
                    ):
                        conflito = True

                        logger.info(
                            "CONFLITO: %s (%s-%s) x ocupado (%s-%s)",
                            horario,
                            inicio,
                            fim,
                            ocupado_inicio,
                            ocupado_fim
                        )

                        break

                if not conflito:
                    horarios_livres.append(horario)

            except Exception as e:

                logger.exception(
                    "ERRO PROCESSANDO AGENDAMENTO: hora=%s, servico=%s",
                    hora,
                    sid
                )

                continue

        return jsonify(horarios_livres)

    except Exception:

        logger.exception(
            "Erro ao buscar horários disponíveis: serviço=%s, data=%s",
            servico_id,
            data
        )

        return jsonify({
            "error": "Erro ao consultar horários disponíveis."
        }), 500

    finally:
        cur.close()

@loja_bp.route("/comprar/<int:produto_id>", methods=["POST"])
def comprar(produto_id):

    cur = get_cursor()

    identificador = request.form.get("identificador")

    try:

        quantidade = int(
            request.form.get("quantidade", 1)
        )

        metodo_pagamento = request.form.get(
            "metodo_pagamento",
            "dinheiro"
        )

        # Validação da quantidade
        if quantidade < 1:
            flash("Quantidade deve ser positiva.", "warning")

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        # Validação do método de pagamento
        if metodo_pagamento not in [
            "pix",
            "cartao",
            "dinheiro"
        ]:
            flash(
                "Método de pagamento inválido.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        # Busca o produto/serviço
        cur.execute(
            """
            SELECT
                id,
                preco_base,
                preco_promocional,
                estoque,
                tipo,
                promocao_percentual,
                promocao_data_limite
            FROM produtos
            WHERE id = %s
            """,
            (produto_id,)
        )

        item = cur.fetchone()

        if not item:
            flash(
                "Item não encontrado.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for("auth.login")
            )

        # Produtos possuem estoque.
        # Serviços não possuem controle de estoque.
        if item["tipo"] == "produto":

            if item["estoque"] < quantidade:

                flash(
                    "Estoque insuficiente.",
                    "warning"
                )

                return redirect(
                    request.referrer or
                    url_for(
                        "loja.loja_publica",
                        identificador=identificador
                    )
                )

        else:
            quantidade = 1

        # Preço base
        preco = float(item["preco_base"])

        # Verifica se existe promoção válida
        promocao_valida = (
            item["preco_promocional"] is not None
            and item["promocao_data_limite"] is not None
            and item["promocao_data_limite"]
            >= datetime.now().date()
        )

        if promocao_valida:
            preco = float(
                item["preco_promocional"]
            )

        valor_total = round(
            preco * quantidade,
            2
        )

        # Pagamentos que não são dinheiro
        # ficam inicialmente aprovados.
        status = (
            "Aprovado"
            if metodo_pagamento != "dinheiro"
            else "Aguardando"
        )

        # Registra a venda
        cur.execute(
            """
            INSERT INTO vendas (
                item_id,
                quantidade,
                metodo_pagamento,
                valor_total,
                status_pagamento
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                produto_id,
                quantidade,
                metodo_pagamento,
                valor_total,
                status
            )
        )

        # Reduz estoque somente para produtos
        if item["tipo"] == "produto":

            cur.execute(
                """
                UPDATE produtos
                SET estoque = estoque - %s
                WHERE id = %s
                """,
                (
                    quantidade,
                    produto_id
                )
            )

        mysql.connection.commit()

        logger.info(
            "Compra realizada: item_id=%s, quantidade=%s, valor_total=%s",
            produto_id,
            quantidade,
            valor_total
        )

        flash(
            "Compra realizada com sucesso!",
            "success"
        )

    except Exception:

        mysql.connection.rollback()

        logger.exception(
            "Erro ao processar compra: item_id=%s",
            produto_id
        )

        flash(
            "Erro ao processar a compra.",
            "danger"
        )

    finally:
        cur.close()

    return redirect(
        url_for(
            "loja.loja_publica",
            identificador=identificador
        )
    )

@loja_bp.route("/agendar_servico", methods=["POST"])
def agendar_servico():

    cur = get_cursor()

    identificador = request.form.get("identificador")

    try:

        servico_id = request.form.get("servico_id")
        cliente_nome = request.form.get("cliente_nome", "").strip()
        data = request.form.get("data")
        hora = request.form.get("hora")
        metodo_pagamento = request.form.get(
            "metodo_pagamento",
            "dinheiro"
        )

        # -------------------------------------------------
        # VALIDAÇÕES BÁSICAS
        # -------------------------------------------------

        if not all([
            servico_id,
            cliente_nome,
            data,
            hora
        ]):
            flash(
                "Preencha todos os dados do agendamento.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        if metodo_pagamento not in [
            "pix",
            "cartao",
            "dinheiro"
        ]:
            flash(
                "Método de pagamento inválido.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        # -------------------------------------------------
        # VALIDA DATA E HORA
        # -------------------------------------------------

        data_obj = safe_parse_date(data)

        if not data_obj:
            flash(
                "Data inválida.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        try:
            to_minutes(hora)
        except ValueError:
            flash(
                "Horário inválido.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        # -------------------------------------------------
        # BUSCA O SERVIÇO
        # -------------------------------------------------

        cur.execute(
            """
            SELECT
                id,
                empresa_id,
                nome,
                preco_base,
                preco_promocional,
                promocao_data_limite,
                tipo,
                permitir_agendamento
            FROM produtos
            WHERE id = %s
            """,
            (servico_id,)
        )

        servico = cur.fetchone()

        if not servico:
            flash(
                "Serviço não encontrado.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        # Garante que realmente é um serviço
        if servico["tipo"] != "servico":
            flash(
                "O item selecionado não é um serviço.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        # Garante que o serviço permite agendamento
        if not servico["permitir_agendamento"]:
            flash(
                "Este serviço não permite agendamento.",
                "warning"
            )

            return redirect(
                request.referrer or
                url_for(
                    "loja.loja_publica",
                    identificador=identificador
                )
            )

        # -------------------------------------------------
        # CALCULA O PREÇO
        # -------------------------------------------------

        preco = float(servico["preco_base"])

        promocao_valida = (
            servico["preco_promocional"] is not None
            and servico["promocao_data_limite"] is not None
            and servico["promocao_data_limite"] >= datetime.now().date()
        )

        if promocao_valida:
            preco = float(
                servico["preco_promocional"]
            )

        # -------------------------------------------------
        # CRIA O AGENDAMENTO
        # -------------------------------------------------

        cur.execute(
            """
            INSERT INTO agendamentos (
                cliente_nome,
                servico_id,
                data,
                hora
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                cliente_nome,
                servico_id,
                data,
                hora
            )
        )

        agendamento_id = cur.lastrowid

        # -------------------------------------------------
        # REGISTRA A VENDA
        # -------------------------------------------------

        status = (
            "Aprovado"
            if metodo_pagamento != "dinheiro"
            else "Aguardando"
        )

        cur.execute(
            """
            INSERT INTO vendas (
                item_id,
                agendamento_id,
                quantidade,
                metodo_pagamento,
                valor_total,
                status_pagamento
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                servico_id,
                agendamento_id,
                1,
                metodo_pagamento,
                preco,
                status
            )
        )

        mysql.connection.commit()

        logger.info(
            "Serviço agendado: "
            "servico_id=%s, agendamento_id=%s, cliente=%s",
            servico_id,
            agendamento_id,
            cliente_nome
        )

        flash(
            "Serviço agendado com sucesso!",
            "success"
        )

    except IntegrityError as e:

        mysql.connection.rollback()

        if (
            e.args
            and e.args[0] == 1062
            and "uq_agendamento_horario" in str(e)
        ):

            logger.warning(
                "Conflito de horário: serviço=%s, data=%s, hora=%s",
                servico_id,
                data,
                hora
            )

            flash(
                "Este horário acabou de ser reservado por outra pessoa. "
                "Escolha outro horário.",
                "warning"
            )

        else:

            logger.exception(
                "Erro de integridade ao agendar serviço: servico_id=%s",
                servico_id
            )

            flash(
                "Não foi possível realizar o agendamento.",
                "danger"
            )

    except Exception:
        
        mysql.connection.rollback()

        logger.exception(
            "Erro ao agendar serviço: servico_id=%s",
            servico_id
        )

        flash(
            "Erro ao realizar o agendamento.",
            "danger"
        )

    finally:
        cur.close()

    return redirect(
        url_for(
            "loja.loja_publica",
            identificador=identificador
        )
    )