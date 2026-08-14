function toggleServiceFields() {
    const tipo = document.getElementById('tipo-select').value;

    document.getElementById('service-fields').style.display =
        tipo === 'servico' ? 'block' : 'none';

    document.getElementById('estoque-field').style.display =
        tipo === 'produto' ? 'block' : 'none';
}


function openEditForm(id, nome, categoria, preco, tipo, estoque, agendar, duracao) {

    document.getElementById('produto_id').value = id;
    document.getElementById('nome').value = nome;
    document.getElementById('categoria').value = categoria;
    document.getElementById('preco_base').value = preco;

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