function toggleServiceFields() {
    const tipo = document.getElementById('tipo-select').value;

    document.getElementById('service-fields').style.display =
        tipo === 'servico' ? 'block' : 'none';

    document.getElementById('estoque-field').style.display =
        tipo === 'produto' ? 'block' : 'none';
}


function openEditFormFromCard(card) {

    const id = card.dataset.id;
    const nome = card.dataset.nome;
    const categoria = card.dataset.categoria;
    const preco = card.dataset.preco;
    const agendar = card.dataset.agendar;
    const duracao = card.dataset.duracao;
    const diasDisponiveis = card.dataset.dias;
    const horariosDisponiveis = card.dataset.horarios;

    openEditForm(
        id,
        nome,
        categoria,
        preco,
        'servico',
        0,
        agendar,
        duracao,
        diasDisponiveis,
        horariosDisponiveis
    );
}


function openEditForm(
    id,
    nome,
    categoria,
    preco,
    tipo,
    estoque,
    agendar,
    duracao,
    diasDisponiveis,
    horariosDisponiveis
) {

    console.log("Dias:", diasDisponiveis);
    console.log("Horários:", horariosDisponiveis);

    document.getElementById('produto_id').value = id;
    document.getElementById('nome').value = nome;
    document.getElementById('categoria').value = categoria;
    document.getElementById('preco_base').value = preco;

    let horarios = [];

    try {
        horarios = JSON.parse(horariosDisponiveis || "[]");
    } catch (e) {
        console.error("Erro ao interpretar horários:", e);
        horarios = [];
    }

    let dias = [];

    try {
        dias = JSON.parse(diasDisponiveis || "[]");
    } catch (e) {
        console.error("Erro ao interpretar dias:", e);
        dias = [];
    }

    console.log("Dias recebidos:", dias);
    console.log(
        "Checkboxes:",
        [...document.querySelectorAll('input[name="dias_disponiveis"]')]
            .map(c => c.value)
    );

    document
    .querySelectorAll('input[name="dias_disponiveis"]')
    .forEach(checkbox => {

        checkbox.checked = dias.some(
            dia =>
                String(dia).trim().toLowerCase() ===
                checkbox.value.trim().toLowerCase()
        );

    });

    const horariosContainer =
        document.getElementById("horarios-container");

    horariosContainer.innerHTML = "";

    if (horarios.length === 0) {

        horariosContainer.innerHTML = `
            <input
                type="time"
                name="horarios_disponiveis"
            >
        `;

    } else {

        horarios.forEach(horario => {

            const input = document.createElement("input");

            input.type = "time";
            input.name = "horarios_disponiveis";
            input.value = horario;

            horariosContainer.appendChild(input);

        });

    }

    if (tipo === 'produto') {

        document.getElementById('edit-estoque').style.display = 'block';
        document.getElementById('edit-servico').style.display = 'none';

        document.getElementById('estoque').value = estoque;

    } else {

        document.getElementById('edit-estoque').style.display = 'none';
        document.getElementById('edit-servico').style.display = 'block';

        document.getElementById('permitir_agendamento').checked =
            agendar == 1;

        document.getElementById('duracao_minutos').value =
            duracao;
    }

    document.getElementById('editOverlay').style.display = 'flex';

    const editForm = document.getElementById('editForm');

    editForm.action = `/produto/editar/${id}`;
}


function excluirItem() {

    const id = document.getElementById('produto_id').value;

    if (!id) {
        return;
    }

    if (confirm('Excluir este item permanentemente?')) {

        const form = document.createElement('form');

        form.method = 'POST';

        form.action = `/produto/excluir/${id}`;

        document.body.appendChild(form);

        form.submit();
    }
}

function closeEditForm() {
    document.getElementById('editOverlay').style.display = 'none';
}

function adicionarHorario() {

    const container = document.getElementById("horarios-container");

    const input = document.createElement("input");

    input.type = "time";
    input.name = "horarios_disponiveis";

    container.appendChild(input);
}

(function () {

    let scale = 1.0;

    const STEP = 0.1;
    const MIN = 0.6;
    const MAX = 2.0;

    const inc = document.getElementById('fontInc');
    const dec = document.getElementById('fontDec');

    function applyScale() {
        document.documentElement.style.setProperty(
            '--ui-scale',
            scale
        );
    }

    if (inc) {
        inc.onclick = () => {
            scale = Math.min(MAX, scale + STEP);
            applyScale();
        };
    }

    if (dec) {
        dec.onclick = () => {
            scale = Math.max(MIN, scale - STEP);
            applyScale();
        };
    }

    
})();

async function loadHorarios(servicoId, data) {

    const select =
        document.getElementById(`horarios-${servicoId}`);

    if (!select) {
        console.error(
            "Select de horários não encontrado:",
            servicoId
        );
        return;
    }

    // Limpa os horários anteriores
    select.innerHTML = `
        <option value="">
            Carregando horários...
        </option>
    `;

    if (!data) {

        select.innerHTML = `
            <option value="">
                Selecione uma data
            </option>
        `;

        return;
    }

    try {

        const resposta = await fetch(
            `/horarios_disponiveis/${servicoId}/${data}`
        );

        const horarios = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                horarios.error ||
                "Erro ao consultar horários."
            );
        }

        select.innerHTML = "";

        if (horarios.length === 0) {

            select.innerHTML = `
                <option value="">
                    Nenhum horário disponível
                </option>
            `;

            return;
        }

        const opcaoInicial =
            document.createElement("option");

        opcaoInicial.value = "";
        opcaoInicial.textContent =
            "Selecione um horário";

        select.appendChild(opcaoInicial);

        horarios.forEach(horario => {

            const option =
                document.createElement("option");

            option.value = horario;
            option.textContent = horario;

            select.appendChild(option);

        });

    } catch (erro) {

        console.error(
            "Erro ao carregar horários:",
            erro
        );

        select.innerHTML = `
            <option value="">
                Erro ao carregar horários
            </option>
        `;
    }
}