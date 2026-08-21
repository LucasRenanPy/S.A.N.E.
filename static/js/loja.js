function loadHorarios(servicoId, data) {

    console.log(
        "Carregando horários:",
        servicoId,
        data
    );
}

console.log("LOJA.JS FOI CARREGADO!");

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

    select.innerHTML = `
        <option value="">
            Carregando horários...
        </option>
    `;

    try {

        const resposta = await fetch(
            `/horarios_disponiveis/${servicoId}/${data}`
        );

        const horarios = await resposta.json();

        console.log(
            "Horários recebidos do servidor:",
            horarios
        );

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