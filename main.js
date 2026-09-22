let perguntas = [];
let indiceAtual = 0;
let pontuacao = 0;
let vidas = 5;
let modoAtual = 'foto';

function mudarModo(modo) {
    modoAtual = modo;
    if (modo === 'foto') {
        document.getElementById('tab-foto').classList.add('active');
        document.getElementById('tab-disciplina').classList.remove('active');
        document.getElementById('campo-foto').classList.remove('hidden');
        document.getElementById('campo-disciplina').classList.add('hidden');
    } else {
        document.getElementById('tab-disciplina').classList.add('active');
        document.getElementById('tab-foto').classList.remove('active');
        document.getElementById('campo-disciplina').classList.remove('hidden');
        document.getElementById('campo-foto').classList.add('hidden');
    }
}

function alternarTema() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    body.classList.toggle('dark-mode');
    if (body.classList.contains('dark-mode')) {
        if (icon) icon.innerText = '☀️';
        localStorage.setItem('theme', 'dark');
    } else {
        if (icon) icon.innerText = '🌙';
        localStorage.setItem('theme', 'light');
    }
}

(function carregarTemaSalvo() {
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        document.addEventListener('DOMContentLoaded', () => {
            const icon = document.getElementById('theme-icon');
            if (icon) icon.innerText = '☀️';
        });
    }
})();

function tocarSom(tipo) {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (tipo === 'correto') {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(1046.50, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.8);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(audioCtx.currentTime);
            osc.stop(audioCtx.currentTime + 0.8);
        } else if (tipo === 'erro') {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(160, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.25);
            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(audioCtx.currentTime);
            osc.stop(audioCtx.currentTime + 0.3);
        }
    } catch (e) { console.log("Áudio não suportado:", e); }
}

function atualizarNomeFicheiro() {
    const input = document.getElementById('foto');
    const label = document.getElementById('file-label');
    if (input.files.length > 0) label.innerText = `📄 Selecionado: ${input.files[0].name}`;
}

async function enviarSolicitacao(event) {
    if (event) event.preventDefault();
    
    const formData = new FormData();
    formData.append('modo', modoAtual);
    formData.append('dificuldade', document.getElementById('dificuldade').value);

    if (modoAtual === 'foto') {
        const inputFoto = document.getElementById('foto');
        if (!inputFoto.files || inputFoto.files.length === 0) {
            alert("Por favor tira foto ou seleciona uma imagem antes de continuar!");
            return;
        }
        formData.append('foto', inputFoto.files[0]);
    } else {
        formData.append('disciplina', document.getElementById('disciplina').value);
    }

    document.getElementById('upload-section').classList.add('hidden');
    document.getElementById('main-header').classList.add('hidden');
    document.getElementById('loading-section').classList.remove('hidden');

    try {
        const response = await fetch('/gerar-quiz', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.perguntas && data.perguntas.length > 0) {
            perguntas = data.perguntas;
            indiceAtual = 0;
            pontuacao = 0;
            vidas = 5;
            
            document.getElementById('loading-section').classList.add('hidden');
            document.getElementById('top-bar').classList.remove('hidden');
            document.getElementById('quiz-section').classList.remove('hidden');
            mostrarPergunta();
        } else {
            alert('Não foi possível gerar as perguntas. Tenta novamente.');
            location.reload();
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao conectar ao servidor.');
        location.reload();
    }
}

function mostrarPergunta() {
    const q = perguntas[indiceAtual];
    const total = perguntas.length;
    
    document.getElementById('lives-count').innerText = vidas;
    document.getElementById('progress-bar').style.width = `${((indiceAtual + 1) / total) * 100}%`;
    document.getElementById('xp-count').innerText = pontuacao * 10;
    document.getElementById('question-text').innerText = q.pergunta;
    
    const container = document.getElementById('options-container');
    container.innerHTML = '';
    document.getElementById('duo-feedback').classList.add('hidden');

    q.opcoes.forEach((opcao, idx) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn animate__animated animate__fadeInUp';
        btn.innerText = opcao;
        btn.onclick = () => verificarResposta(idx, btn);
        container.appendChild(btn);
    });
}

function verificarResposta(indiceSelecionado, botaoClicado) {
    const q = perguntas[indiceAtual];
    const botoes = document.querySelectorAll('.option-btn');
    const feedbackSheet = document.getElementById('duo-feedback');
    const feedbackTitle = document.getElementById('feedback-title');
    const feedbackIcon = document.getElementById('feedback-icon');
    
    botoes.forEach(b => b.disabled = true);

    if (indiceSelecionado === q.resposta_correta) {
        botaoClicado.classList.add('correct');
        tocarSom('correto');
        pontuacao++;
        feedbackSheet.className = "duo-feedback-sheet correct-sheet";
        feedbackIcon.innerText = "✨";
        feedbackTitle.innerText = "Excelente!";
    } else {
        botaoClicado.classList.add('wrong');
        botoes[q.resposta_correta].classList.add('correct');
        tocarSom('erro');
        vidas--;
        document.getElementById('lives-count').innerText = vidas;
        feedbackSheet.className = "duo-feedback-sheet wrong-sheet";
        feedbackIcon.innerText = "❌";
        feedbackTitle.innerText = "Solução correta:";
    }

    document.getElementById('explanation-text').innerText = q.explicacao;
    feedbackSheet.classList.remove('hidden');
}

function proximaPergunta() {
    document.getElementById('duo-feedback').classList.add('hidden');
    if (vidas <= 0) {
        mostrarGameOver();
        return;
    }
    indiceAtual++;
    if (indiceAtual < perguntas.length) {
        mostrarPergunta();
    } else {
        mostrarResultadoFinal();
    }
}

function mostrarGameOver() {
    document.getElementById('quiz-section').classList.add('hidden');
    document.getElementById('top-bar').classList.add('hidden');
    document.getElementById('gameover-section').classList.remove('hidden');
}

function mostrarResultadoFinal() {
    document.getElementById('quiz-section').classList.add('hidden');
    document.getElementById('top-bar').classList.add('hidden');
    document.getElementById('result-section').classList.remove('hidden');
    
    const total = perguntas.length;
    document.getElementById('final-xp').innerText = `${pontuacao * 10} XP`;
    document.getElementById('final-accuracy').innerText = `${Math.round((pontuacao / total) * 100)}%`;
}

function confirmarSair() {
    if (confirm("Tens a certeza que queres sair? Vais perder o progresso desta lição.")) location.reload();
}

function partilharWhatsapp() {
    const texto = `🏆 Concluí uma lição no PROVA FÁCIL! Fiz ${pontuacao * 10} XP com ${Math.round((pontuacao / perguntas.length) * 100)}% de precisão! 🎓🚀`;
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(texto)}`, '_blank');
}

function partilharGeral() {
    if (navigator.share) {
        navigator.share({ title: 'PROVA FÁCIL 🎓', text: `Consegui ${pontuacao * 10} XP no PROVA FÁCIL!`, url: window.location.href });
    } else { partilharWhatsapp(); }
}