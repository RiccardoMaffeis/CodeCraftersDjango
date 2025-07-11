document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.db-tab');
    const overlay = document.getElementById('loading-overlay');

    let currentPage = 1;
    let currentTable = 'Biglietto';

    function showTab(tableName) {
        tabs.forEach(t => t.classList.toggle('active', t.dataset.table === tableName));
        document.querySelectorAll('.db-table-container')
            .forEach(c => c.style.display = c.id === 'tab-' + tableName ? 'block' : 'none');
    }

    function loadTable(tableName, page = 1) {
        currentTable = tableName;
        currentPage = page;

        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/database/get_table/?table=${encodeURIComponent(tableName)}&page=${page}`, true);

        xhr.onload = () => {
            const container = document.getElementById('tab-' + tableName);
            if (xhr.status === 200) {
                container.innerHTML = xhr.responseText;
            } else {
                container.innerHTML = `<h2 class="db-title">Tabella ${tableName}</h2>
                               <p class="db-nodata">Errore ${xhr.status}</p>`;
            }
            showTab(tableName);

            container.querySelectorAll('.page-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    loadTable(currentTable, parseInt(btn.dataset.page, 10));
                });
            });

            const pagination = container.querySelector('.pagination');
            const totalPages = parseInt(pagination.dataset.total, 10);
            const pageInput = pagination.querySelector('.page-input');
            const pageGo = pagination.querySelector('.page-go');

            pageGo.addEventListener('click', () => {
                let target = parseInt(pageInput.value, 10);
                if (isNaN(target) || target < 1) target = 1;
                else if (target > totalPages) target = totalPages;
                loadTable(currentTable, target);
            });

            container.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', () => {
                    const table = encodeURIComponent(btn.dataset.table);
                    const id = encodeURIComponent(btn.dataset.id);
                    Swal.fire({
                        title: 'Sei sicuro?',
                        text: "Questa azione non può essere annullata!",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#d33',
                        cancelButtonColor: '#3085d6',
                        confirmButtonText: 'Sì, elimina!',
                        cancelButtonText: 'Annulla'
                    }).then(result => {
                        if (result.isConfirmed) {
                            fetch(`/database/delete_row/`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                body: `table=${table}&id=${id}`
                            })
                                .then(res => res.json())
                                .then(data => {
                                    if (data.success) {
                                        Swal.fire('Eliminato!', data.message, 'success')
                                            .then(() => loadTable(currentTable, currentPage));
                                    } else {
                                        Swal.fire('Errore', data.message, 'error');
                                    }
                                });
                        }
                    });
                });
            });

            container.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', () => {
                    const table = encodeURIComponent(btn.dataset.table);
                    const id = encodeURIComponent(btn.dataset.id);
                    window.location.href = `/database/edit_row/?table=${table}&id=${id}`;
                });
            });
        };

        xhr.onerror = () => {
            const container = document.getElementById('tab-' + tableName);
            container.innerHTML = `<h2 class="db-title">Tabella ${tableName}</h2>
                             <p class="db-nodata">Errore di rete.</p>`;
            showTab(tableName);
            overlay.style.display = 'none';
        };

        xhr.send();
    }

    loadTable('Biglietto', 1);

    tabs.forEach(tab =>
        tab.addEventListener('click', () => loadTable(tab.dataset.table, 1))
    );
});
