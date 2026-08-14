CREATE DATABASE catalogo_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE catalogo_db;

-- =====================================================
-- USUÁRIOS
-- =====================================================

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);

-- =====================================================
-- EMPRESAS
-- =====================================================

CREATE TABLE empresas (
    id INT AUTO_INCREMENT PRIMARY KEY,

    usuario_id INT NOT NULL,

    nome VARCHAR(255) NOT NULL,

    identificador_url VARCHAR(100) NOT NULL UNIQUE,

    FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);

-- =====================================================
-- PRODUTOS / SERVIÇOS
-- =====================================================

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,

    empresa_id INT NOT NULL,

    nome VARCHAR(255) NOT NULL,

    categoria VARCHAR(100) NOT NULL,

    descricao TEXT,

    preco_base DECIMAL(10,2) NOT NULL,

    preco_promocional DECIMAL(10,2) DEFAULT NULL,

    estoque INT NOT NULL DEFAULT 0,

    imagem VARCHAR(255),

    tipo ENUM('produto','servico')
        NOT NULL DEFAULT 'produto',

    promocao_percentual INT DEFAULT NULL,

    promocao_data_limite DATE DEFAULT NULL,

    permitir_agendamento BOOLEAN DEFAULT FALSE,

    duracao_minutos INT DEFAULT 60,

    dias_disponiveis JSON DEFAULT NULL,

    horarios_disponiveis JSON DEFAULT NULL,

    FOREIGN KEY (empresa_id)
        REFERENCES empresas(id)
        ON DELETE CASCADE
);

-- =====================================================
-- PROMOÇÕES
-- =====================================================

CREATE TABLE promocoes (

    id INT AUTO_INCREMENT PRIMARY KEY,

    produto_id INT NOT NULL,

    desconto DECIMAL(5,2) NOT NULL,

    data_inicio DATE NOT NULL,

    data_fim DATE NOT NULL,

    FOREIGN KEY (produto_id)
        REFERENCES produtos(id)
        ON DELETE CASCADE
);

-- =====================================================
-- AGENDAMENTOS
-- =====================================================

CREATE TABLE agendamentos (

    id INT AUTO_INCREMENT PRIMARY KEY,

    cliente_nome VARCHAR(255) NOT NULL,

    servico_id INT NOT NULL,

    data DATE NOT NULL,

    hora TIME NOT NULL,

    FOREIGN KEY (servico_id)
        REFERENCES produtos(id)
        ON DELETE CASCADE
);

-- =====================================================
-- VENDAS
-- =====================================================

CREATE TABLE vendas (

    id INT AUTO_INCREMENT PRIMARY KEY,

    item_id INT NOT NULL,

    agendamento_id INT DEFAULT NULL,

    quantidade INT NOT NULL,

    metodo_pagamento ENUM(
        'pix',
        'cartao',
        'dinheiro'
    ) NOT NULL,

    valor_total DECIMAL(10,2) NOT NULL,

    data DATETIME DEFAULT CURRENT_TIMESTAMP,

    status_pagamento ENUM(
        'Aguardando',
        'Aprovado',
        'Recusado'
    ) DEFAULT 'Aguardando',

    FOREIGN KEY (item_id)
        REFERENCES produtos(id)
        ON DELETE CASCADE,

    FOREIGN KEY (agendamento_id)
        REFERENCES agendamentos(id)
        ON DELETE SET NULL
);

-- =====================================================
-- HORÁRIOS BLOQUEADOS
-- =====================================================

CREATE TABLE horarios_bloqueados (

    id INT AUTO_INCREMENT PRIMARY KEY,

    data DATE NOT NULL,

    hora TIME NOT NULL,

    UNIQUE(data, hora)
);

drop database catalogo_db;