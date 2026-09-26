import os
import json
import random
import base64
import requests
from flask import Flask, render_template, request, jsonify
from PIL import Image
import io

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gerar-quiz', methods=['POST'])
def gerar_quiz():
    modo = request.form.get('modo', 'disciplina')
    disciplina = request.form.get('disciplina', 'Informática')

    prompt_instrucoes = f"""
    Cria EXATAMENTE 15 PERGUNTAS ÚNICAS de escolha múltipla sobre {disciplina}.

    [REGRAS OBRIGATÓRIAS]
    - QUANTIDADE: EXATAMENTE 15 PERGUNTAS.
    - DISCIPLINA: {disciplina}
    - NENHUMA PERGUNTA REPETIDA.
    - Respostas teóricas e académicas rigorosas.

    [FORMATO EXCLUSIVO DE RESPOSTA]
    Responde APENAS com um array JSON válido sem markdown e sem texto adicional:
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

            prompt_final = f"{prompt_instrucoes}\n\nAnalisa a imagem anexada e gera 15 perguntas baseadas no seu conteúdo."
            messages_content = [
                {"type": "text", "text": prompt_final},
                {"type": "image_url", "image_url": {"url": image_data_url}}
            ]
        else:
            prompt_final = f"{prompt_instrucoes}\n\nGera 15 perguntas inéditas para {disciplina}."
            messages_content = prompt_final

        # Modelos válidos do OpenRouter
        modelos_para_tentar = [
            "google/gemini-2.0-flash-lite-001",
            "google/gemini-flash-1.5",
            "meta-llama/llama-3.3-70b-instruct"
        ]

        resposta_sucesso = None

        for model_name in modelos_para_tentar:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "És um gerador de testes escolares. Responde EXCLUSIVAMENTE num array JSON válido."},
                    {"role": "user", "content": messages_content}
                ],
                "temperature": 0.3,
                "max_tokens": 4096
            }

            try:
                res = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    resposta_sucesso = res.json()
                    break
                else:
                    print(f"⚠️ Modelo {model_name} respondeu com código {res.status_code}: {res.text}")
            except Exception as err:
                print(f"⚠️ Falha no modelo {model_name}: {err}")

        if not resposta_sucesso:
            raise Exception("Nenhum dos modelos disponíveis respondeu com sucesso.")

        texto = resposta_sucesso['choices'][0]['message']['content'].strip()

        # Limpeza do formato JSON
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0].strip()

        quiz_data = json.loads(texto)
        if isinstance(quiz_data, dict) and "perguntas" in quiz_data:
            quiz_data = quiz_data["perguntas"]

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
        print(f"❌ Erro final ao gerar o quiz: {e}")
        return jsonify({
            "error": True,
            "message": f"Erro na API do OpenRouter: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
