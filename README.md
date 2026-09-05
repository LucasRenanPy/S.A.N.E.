# S.A.N.E.

## Sistema de Apoio a Negócios e Empresas

O **S.A.N.E. (Sistema de Apoio a Negócios e Empresas)** é um projeto voltado ao apoio à gestão de **microempresas**, utilizando tecnologia e dados para auxiliar empreendedores na análise e tomada de decisões.

O projeto foi desenvolvido e apresentado em **feiras de iniciação científica**, tendo como proposta transformar dados de diferentes fontes em **informação e inteligência de negócio**, facilitando a compreensão do mercado e o planejamento empresarial dentro da problemática da **gestão de microempresas**.

Entre os módulos e funcionalidades desenvolvidos estão:

* **Pesquisa de mercado** — análise de estabelecimentos, concorrentes, serviços complementares e características da região;
* **Cálculo de tributos** — ferramenta para simulação de cálculos tributários;
* **Catálogo digital** — gerenciamento e divulgação de produtos e serviços;

> **Status:** Atualmente, o S.A.N.E. encontra-se em processo de formulação e evolução. Os módulos estão sendo reformulados gradualmente, com foco em uma arquitetura que permita futuras integrações e expansão do sistema.

---

## Feiras de Iniciação Científica

O S.A.N.E. foi apresentado em eventos de iniciação científica como parte de sua proposta de aplicação de tecnologia na gestão de pequenos negócios.

### Eventos

* **1ª Virada Tecnológica de Paulínia** — Prefeitura de Paulínia, 2025
* **BentoTec** — ETEC Bento Quirino, 2025
* **IFCIÊNCIA** — Instituto Federal de Salto, 2025
* **COTUCA/Unicamp** — Colégio Técnico de Campinas, 2025

---

## Tecnologias

* **Python**
* **Flask**
* **MySQL**
* **HTML**
* **CSS**
* **JavaScript**

### Estrutura do projeto

```text
routes/       → rotas e lógica da aplicação
templates/    → páginas HTML e templates Jinja2
static/       → arquivos CSS, JavaScript e imagens
database/     → estrutura e scripts do banco de dados
```

---

## Instalação

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd S.A.N.E.
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

Ative o ambiente virtual:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto e configure as variáveis necessárias.

Utilize o `.env.example` como referência:

```text
.env.example
```

> **Nunca envie o arquivo `.env` para o repositório**, pois ele pode conter credenciais e outras informações privadas.

### 5. Configure o banco de dados

O script de criação do banco encontra-se em:

```text
database/schema.sql
```

Execute o script no **MySQL** para criar o banco de dados e suas tabelas.

### 6. Execute a aplicação

Com o ambiente virtual ativado:

```bash
python app.py
```

A aplicação estará disponível localmente no endereço indicado pelo Flask no terminal.
