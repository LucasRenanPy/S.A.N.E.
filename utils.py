import json
import unicodedata
import hashlib
import requests
import secrets
from datetime import datetime
from email_validator import validate_email, EmailNotValidError


def normalizar(txt):

    if not txt:
        return ""

    s = unicodedata.normalize('NFD', str(txt))
    s = ''.join(
        ch for ch in s
        if unicodedata.category(ch) != 'Mn'
    )

    s = s.split('-')[0].split()[0]

    return s.lower().strip()


def parse_list_field(val):

    if not val:
        return []

    if isinstance(val, list):
        return val

    if isinstance(val, str):
        try:
            parsed = json.loads(val)

            if isinstance(parsed, list):
                return parsed

        except json.JSONDecodeError:
            return [
                p.strip()
                for p in val.split(',')
                if p.strip()
            ]

    return []


def to_minutes(hhmm):

    try:
        parts = hhmm.split(':')

        if len(parts) != 2:
            raise ValueError("Invalid time format")

        h, m = map(int, parts)

        return h * 60 + m

    except Exception as e:
        raise ValueError(f"Invalid time format: {e}")


def safe_parse_date(v, format="%Y-%m-%d"):

    if not v:
        return None

    try:
        return datetime.strptime(v, format).date()

    except ValueError:
        return None
    
def validar_senha(senha):
    if not 8 <= len(senha) <= 64:
        return False, "A senha deve ter entre 8 e 64 caracteres."
    
    if any(c.isspace() for c in senha):
        return False, "A senha não pode conter espaços."
    
    try:
        if senha_comprometida(senha):
            return False, "Essa senha já apareceu em vazamentos de dados e não pode ser utilizada."

    except RuntimeError:
        return False, "Não foi possível verificar a segurança da senha. Tente novamente."

    return True, None

def senha_comprometida(senha):
    hash_senha = hashlib.sha1(
        senha.encode('utf-8')
    ).hexdigest().upper()

    prefixo = hash_senha[:5]
    sufixo = hash_senha[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefixo}"

    try:
        resposta = requests.get(
            url,
            headers={
                "User-Agent": "SANE-Password-Checker"
            },
            timeout=5
        )

        resposta.raise_for_status()

    except requests.RequestException as e:
        raise RuntimeError(
            "Não foi possível verificar a senha."
        ) from e

    for linha in resposta.text.splitlines():
        hash_retorno, quantidade = linha.split(":")

        if hash_retorno == sufixo:
            return True

    return False

def validar_email(email):
    if not email:
        return False, "O e-mail é obrigatório."

    if any(c.isspace() for c in email):
        return False, "O e-mail não pode conter espaços."

    try:
        validate_email(
            email,
            check_deliverability=False
        )

    except EmailNotValidError:
        return False, "Informe um endereço de e-mail válido."

    return True, None

def hash_token_verificacao(token):
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def gerar_token_verificacao():
    token = secrets.token_urlsafe(32)

    token_hash = hash_token_verificacao(token)

    return token, token_hash
