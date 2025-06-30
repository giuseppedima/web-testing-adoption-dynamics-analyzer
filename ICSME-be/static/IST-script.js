let currentIndex = 0;
let totalRows = 0;

document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_total_rows')
        .then(response => response.json())
        .then(data => {
            totalRows = data.total_rows;
            document.getElementById('total-rows').textContent = totalRows;
            loadRow(currentIndex);
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
            document.getElementById('commit-date').textContent = data['date'];
            const messageElement = document.getElementById('commit-message-text');
            messageElement.value = data['message']; // or .innerText if it's a <div>

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

        });
}


function  setCurrentIndexManually(){
       const index = parseInt(document.getElementById('index-input').value, 10);
    console.log('set current index manually: ' + index);

    if (!isNaN(index) && index <= totalRows && index >= 1) {
        currentIndex = index - 1;
        loadRow(currentIndex);
    } else {
        console.log('Invalid index');
    }

}

function previousRow() {
    if (currentIndex > 0) {
        currentIndex--;
        loadRow(currentIndex);
    }
}

function nextRow() {
    if (currentIndex < totalRows - 1) {
        currentIndex++;
        loadRow(currentIndex);
    }
}

function saveLabel(label) {
    const data ={
        index: currentIndex,
        change_label : label
    }
    perform_save_label_request(data)

    /*
    const label_text = document.getElementById("change-label").value;
    const selectElement = document.getElementById('label-options'); // Ottieni il riferimento alla select
    const selectedValue = selectElement.value; // Ottieni il valore selezionato
    console.log('label_text: '+label_text+' combobox: '+selectedValue)
    if(label_text!='' && selectedValue!=''){
       alert('You can only enter a label manually or choose it from the combo box!')
    }else if (label_text!='' && selectedValue ==''){
         const data = {
            index: currentIndex,
            change_label: label_text
        };
         console.log('saving label '+label_text+' row_index: '+currentIndex)
         perform_save_label_request(data);
    }else if(label_text=='' && selectedValue!=''){
        const data = {
            index: currentIndex,
            change_label: selectedValue
        };
        console.log('saving label '+selectedValue+' row_index: '+currentIndex)
        perform_save_label_request(data);
    }else{ //empty case
        data ={
            index : currentIndex,
            change_label:''
        }
        perform_save_label_request(data)
        console.log('deleting the current label from row_index: '+currentIndex);
    }*/

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
            alert("Label saved successfully!");
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


