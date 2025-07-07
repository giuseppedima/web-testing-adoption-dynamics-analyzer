let currentIndex = 0;
let totalRows = 0;
let filteredIndices = null; // Nuova variabile globale

document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_total_rows')
        .then(response => response.json())
        .then(data => {
            totalRows = data.total_rows;
            document.getElementById('total-rows').textContent = totalRows;
            loadRow(currentIndex);
            updateFilterResultsInfo();
        });

    $('#keyword-filter').select2({
        placeholder: "Select the keywords",
        width: '100%'
    });

    document.getElementById('clear-keyword-filter').addEventListener('click', function() {
        $('#keyword-filter').val(null).trigger('change');
        document.getElementById('apply-keyword-filter').click(); // Simula il click per applicare il filtro
    });

    document.getElementById('apply-keyword-filter').addEventListener('click', function() {
        const selectedKeywords = $('#keyword-filter').val();
        console.log('Selected keywords:', selectedKeywords);

        // Se nessuna keyword selezionata, resetta la visualizzazione
        if (!selectedKeywords || selectedKeywords.length === 0) {
            filteredIndices = null; // Reset filtri
            loadRowByIndex(0);
            return;
        }

        // Invia le keyword selezionate al backend per filtrare
        fetch('/filter_by_keywords', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keywords: selectedKeywords })
        })
        .then(response => response.json())
        .then(data => {
            const indices = data.indices;
            if (indices.length === 0) {
                alert('Nessun risultato trovato per le keyword selezionate.');
                filteredIndices = null;
                return;
            }
            filteredIndices = indices;
            loadRowByIndex(0);
        })
        .catch(error => {
            alert('Errore durante il filtraggio: ' + error);
        });
    });

    // Popola le opzioni dal backend
    fetch('/keywords')
        .then(response => response.json())
        .then(keywords => {
            const select = document.getElementById('keyword-filter');
            select.innerHTML = ''; // Pulisci le opzioni esistenti
            keywords.forEach(keyword => {
                const option = document.createElement('option');
                option.value = keyword;
                option.textContent = keyword;
                select.appendChild(option);
            });
            // Aggiorna Select2 dopo aver aggiunto le opzioni
            $('#keyword-filter').trigger('change');
        });
});

document.getElementById('prev-button').addEventListener('click',previousRow);
document.getElementById('next-button').addEventListener('click',nextRow);
document.getElementById('not-useful-button').addEventListener('click', function() {
    saveLabel('not-useful');
});

document.getElementById('useful-button').addEventListener('click', function() {
    saveLabel('useful');
});
document.getElementById('set-index-button').addEventListener('click',setCurrentIndexManually)



function loadRow(index) {
    fetch(`/get_csv_data/${index}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            document.getElementById('repo').textContent = data.repo;
            document.getElementById('keywords').textContent = data['matches'];
            document.getElementById('created-at').textContent = data['created_at'];
            document.getElementById('updated-at').textContent = data['updated_at'];
            document.getElementById('closed-at').textContent = data['is_closed'] ? data['closed_at'] : 'Open';
            const messageElement = document.getElementById('issue-message-text');
            messageElement.value = "Title:\n" + data['title'] + '\n\nBody:\n' + data['body'];

            if (data['label'] === 'useful') {
                messageElement.style.color = 'green';
            } else if (data['label'] === 'not-useful') {
                messageElement.style.color = 'red';
            } else {
                messageElement.style.color = 'black';
            }

            //document.getElementById('diff-text').value = data.diff;
            document.getElementById('current-index').textContent = index + 1; // For 1-based display
            console.log('label: '+data.label)

            /*
            if (data.label !=''){
                document.getElementById('change-label').value = data.label;
            }else{
                console.log('label empty!')
                document.getElementById('change-label').value='';
            }*/

            document.getElementById('view-issue').onclick = function() {
                window.open(`https://github.com/${data.repo}/issues/${data.number}`, '_blank');
            };

        });
}


function loadRowByIndex(index) {
    if (filteredIndices && filteredIndices.length > 0) {
        if (index >= 0 && index < filteredIndices.length) {
            currentIndex = index;
            loadRow(filteredIndices[currentIndex]);
        }
    } else {
        if (index >= 0 && index < totalRows) {
            currentIndex = index;
            loadRow(currentIndex);
        }
    }
    updateFilterResultsInfo();
}

function setCurrentIndexManually() {
    const index = parseInt(document.getElementById('index-input').value, 10);
    console.log('set current index manually: ' + index);

    if (!isNaN(index)) {
        loadRowByIndex(index - 1);
    } else {
        alert('Invalid index');
    }
}

function previousRow() {
    loadRowByIndex(currentIndex - 1);
}

function nextRow() {
    loadRowByIndex(currentIndex + 1);
}

function saveLabel(label) {
    let realIndex;
    if (filteredIndices && filteredIndices.length > 0) {
        realIndex = filteredIndices[currentIndex];
    } else {
        realIndex = currentIndex;
    }
    const data = {
        index: realIndex,
        change_label: label
    };
    perform_save_label_request(data);
}


function perform_save_label_request(data){
      // Invio della richiesta POST al server
    fetch('/save_label', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadRowByIndex(currentIndex); // Ricarica la riga corrente per aggiornare l'etichetta
            // alert("Label saved successfully!");
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => {
        alert("An error occurred: " + error);
    });
}

function fillLabelOptions() {
    fetch(`/labels`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Ottieni il riferimento al select
            const selectElement = document.getElementById('label-options');

            // Pulisci le opzioni esistenti
            selectElement.innerHTML = '';

            // Aggiungi un'opzione vuota (opzionale)
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select Label';
            selectElement.appendChild(defaultOption);

            // Aggiungi le etichette dinamicamente
            data.forEach(label => {
                const option = document.createElement('option');
                option.value = label; // Valore dell'opzione
                option.textContent = label; // Testo visibile dell'opzione
                selectElement.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching labels:', error);
            alert('Failed to load labels.');
        });
}


function displayDiff(diffText) {
    const diffContent = document.getElementById('diff-text');
    diffContent.innerHTML = ''; // Pulisce il contenuto esistente
    const lines = diffText.split('\n');
    console.log('lines size: '+lines.length);
    lines.forEach(line => {
        const lineElement = document.createElement('div');
        lineElement.textContent = line;

        if (line.startsWith('+')) {
            lineElement.classList.add('line-addition');
        } else if (line.startsWith('-')) {
            lineElement.classList.add('line-deletion');
        }

        diffContent.appendChild(lineElement);
    });
}

function updateFilterResultsInfo() {
    const infoSpan = document.getElementById('filter-results-info');
    if (!infoSpan) return;
    if (filteredIndices && filteredIndices.length > 0) {
        infoSpan.textContent = `Result ${currentIndex + 1} of ${filteredIndices.length}`;
    } else {
        infoSpan.textContent = `Result ${currentIndex + 1} of ${totalRows}`;
    }
}

document.addEventListener('keydown', function(event) {
    const active = document.activeElement;

    // Se focus su input indice e Invio, imposta indice manualmente
    if (event.key === 'Enter' && active && active.id === 'index-input') {
        setCurrentIndexManually();
        event.preventDefault();
        return;
    }

    // Evita conflitti se si sta scrivendo in un input
    if (active && (active.tagName === 'INPUT')) return;

    switch(event.key) {
        case 'ArrowLeft':
        case 'ArrowUp':
            previousRow();
            event.preventDefault();
            break;
        case 'ArrowRight':
        case 'ArrowDown':
            nextRow();
            event.preventDefault();
            break;
        case 'Enter':
            saveLabel('useful');
            event.preventDefault();
            break;
        case 'Backspace':
            saveLabel('not-useful');
            event.preventDefault();
            break;
    }
});


