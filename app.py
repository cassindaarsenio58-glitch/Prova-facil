import os
import json
import random
import base64
import requests
from flask import Flask, render_template, request, jsonify
from PIL import Image
import io

app = Flask(__name__)

# Chave do OpenRouter obtida das variáveis de ambiente
OPENROUTER_API_KEY = os.environ.get("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")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gerar-quiz', methods=['POST'])
def gerar_quiz():
    modo = request.form.get('modo', 'disciplina')
    disciplina = request.form.get('disciplina', 'Informática')

    # Instrução direta reforçando a saída apenas em JSON
    prompt_instrucoes = f"""
    Cria EXATAMENTE 15 PERGUNTAS ÚNICAS de escolha múltipla sobre {disciplina}.

    [REGRAS]
    - QUANTIDADE OBRIGATÓRIA: EXATAMENTE 15 PERGUNTAS.
    - DISCIPLINA: {disciplina}
    - NENHUMA PERGUNTA PODE SER REPETIDA.
    - Respostas teóricas e académicas rigorosas.

    [FORMATO OBRIGATÓRIO DE RESPOSTA]
    Responde APENAS com um array JSON válido sem texto antes ou depois, seguindo este formato:
    [
      {{
        "pergunta": "Enunciado da pergunta...",
        "opcoes": ["Opção Correta", "Opção Errada 1", "Opção Errada 2", "Opção Errada 3"],
        "resposta_correta": 0,
        "explicacao": "Explicação detalhada..."
      }}
    ]
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://provafacil.onrender.com",
        "X-Title": "Prova Fácil"
    }

    try:
        if modo == 'foto' and 'foto' in request.files and request.files['foto'].filename != '':
            ficheiro = request.files['foto']
            imagem = Image.open(ficheiro.stream)
            imagem.thumbnail((800, 800))
            
            buffered = io.BytesIO()
            imagem.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{img_str}"

            prompt_final = f"{prompt_instrucoes}\n\nAnalisa a foto anexada e gera 15 perguntas baseadas no seu conteúdo."
            
            messages_content = [
                {"type": "text", "text": prompt_final},
                {"type": "image_url", "image_url": {"url": image_data_url}}
            ]
        else:
            prompt_final = f"{prompt_instrucoes}\n\nGera 15 perguntas inéditas sobre {disciplina}."
            messages_content = prompt_final

        # Usa modelo gratuito por padrão ou a rota gratuita universal do OpenRouter
        model_name = "google/gemini-flash-1.5-exp:free"

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "És um gerador automático de testes. Responde APENAS no formato JSON solicitado."},
                {"role": "user", "content": messages_content}
            ],
            "temperature": 0.3,
            "max_tokens": 4096
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=35)
        
        # Tenta rota de modelos grátis alternativa caso o modelo principal falhe
        if response.status_code != 200:
            print(f"⚠️ Erro {response.status_code} no modelo principal. A tentar rota gratuita 'openrouter/free'...")
            payload["model"] = "openrouter/free"
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=35)

        response.raise_for_status()
        
        data = response.json()
        texto = data['choices'][0]['message']['content'].strip()

        # Extração limpa do bloco JSON
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0].strip()

        quiz_data = json.loads(texto)
        if isinstance(quiz_data, dict) and "perguntas" in quiz_data:
            quiz_data = quiz_data["perguntas"]

        # Embaralhar as opções e ajustar o índice correto
        perguntas_vistas = set()
        quiz_limpo = []
        for q in quiz_data:
            if q["pergunta"] not in perguntas_vistas:
                perguntas_vistas.add(q["pergunta"])
                correta_texto = q["opcoes"][q["resposta_correta"]]
                random.shuffle(q["opcoes"])
                q["resposta_correta"] = q["opcoes"].index(correta_texto)
                quiz_limpo.append(q)

        return jsonify({"perguntas": quiz_limpo[:15]})

    except Exception as e:
        print(f"❌ Erro na requisição OpenRouter: {e}")
        return jsonify({
            "error": True,
            "message": "Ocorreu um erro ao gerar o quiz na API. Verifica se a chave OPENROUTER_API_KEY está configurada no Render."
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
