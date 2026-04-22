const dropZone = document.getElementById('drop-zone');
const previewContainer = document.getElementById('preview-container');
const btnGerar = document.getElementById('btn-gerar');
const btnCopiar = document.getElementById('btn-copiar');
const resultado = document.getElementById('resultado');

let imagensParaEnviar = []; 

window.addEventListener('paste', (event) => {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;
    
    for (let item of items) {
        if (item.kind === 'file' && item.type.startsWith('image/')) {
            const blob = item.getAsFile();
            
            imagensParaEnviar.push(blob);

            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.createElement('img');
                img.src = e.target.result;
                
                img.style.width = "100px";
                img.style.height = "75px";
                img.style.objectFit = "cover";
                img.style.borderRadius = "8px";
                img.style.border = "2px solid #3b82f6";
                
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(blob);
        }
    }
});

btnGerar.onclick = async () => {
    if (imagensParaEnviar.length === 0) {
        alert("Nenhuma imagem detectada. Tire um print e dê Ctrl+V aqui!");
        return;
    }

    resultado.value = "IA analisando os prints... aguarde.";

    const formData = new FormData();
    imagensParaEnviar.forEach((file, index) => {
        formData.append('files', file, `print_${index}.png`);
    });

    try {
        const response = await fetch('http://localhost:8001/gerar-guia', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.guia) {
            resultado.value = data.guia;
        } else {
            resultado.value = "Erro: " + data.error;
        }
    } catch (error) {
        resultado.value = "Servidor offline. Ligue o main.py no VS Code!";
    }
};

btnCopiar.onclick = () => {
    resultado.select();
    document.execCommand('copy');
    alert("Texto copiado!");
};