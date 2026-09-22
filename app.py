import os
import json
import random
from flask import Flask, render_template, request, jsonify
from PIL import Image
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBEFe95-TZKIvHvKQ355glAgxAh5E5TBKY")
genai.configure(api_key=GEMINI_API_KEY)

# Banco de questões extenso
BANCO_DE_PERGUNTAS = {
    "Informática": [
        ("Qual componente do computador é responsável por executar instruções e processar dados?", ["Processador (CPU)", "Memória RAM", "Disco Rígido (HD)", "Placa Mãe"], 0, "A CPU é o cérebro do computador, responsável pelo processamento principal."),
        ("O que significa a sigla HTTP nos endereços da web?", ["HyperText Transfer Protocol", "High Tech Transfer Program", "Home Text Process Protocol", "Hyperlink Total Task"], 0, "HTTP é o protocolo de transferência de hipertexto na web."),
        ("Qual destes é um sistema operativo de código aberto (Open Source)?", ["Linux", "Windows 11", "macOS", "iOS"], 0, "O Linux possui código-fonte aberto e livre acesso."),
        ("Para que serve a memória RAM?", ["Armazenar dados temporariamente em execução", "Guardar fotos permanentemente", "Imprimir ficheiros", "Aumentar a velocidade da internet"], 0, "A RAM armazena informações temporárias de programas abertos."),
        ("O que é Phishing no contexto de cibersegurança?", ["Engano para roubar dados confidenciais", "Um antivírus de computador", "Uma linguagem de programação", "Aceleração do sinal Wi-Fi"], 0, "Phishing utiliza mensagens falsas para induzir o utilizador a fornecer senhas."),
        ("Qual porta lógica inverte o valor de entrada (0 vira 1 e 1 vira 0)?", ["Porta NOT", "Porta AND", "Porta OR", "Porta XOR"], 0, "A porta NOT (inversora) altera o bit de entrada para o seu oposto."),
        ("O que é um endereço IP?", ["Identificador único de um dispositivo na rede", "Uma chave de segurança do Wi-Fi", "O nome do fabricante do computador", "A velocidade da conexão"], 0, "O IP identifica e localiza um dispositivo na rede."),
        ("Qual destas opções é uma linguagem de programação?", ["Python", "HTML", "CSS", "JSON"], 0, "Python é uma linguagem de programação de alto nível."),
        ("O que significa SSD em armazenamento de dados?", ["Solid State Drive", "Super Speed Disk", "System Storage Data", "Secure Source Device"], 0, "O SSD é um dispositivo de armazenamento ultrarrápido sem partes móveis."),
        ("O que faz um Firewall num sistema informático?", ["Filtra o tráfego de rede e bloqueia conexões não autorizadas", "Aumenta o espaço de armazenamento", "Limpa a poeira física da máquina", "Traduz textos automaticamente"], 0, "O Firewall monitoriza e controla o tráfego de rede com base em regras de segurança."),
        ("Qual é a função do sistema de ficheiros num sistema operativo?", ["Organizar e controlar como os dados são guardados e lidos", "Aumentar a resolução da tela", "Proteger contra quedas de energia", "Compactar ficheiros de áudio"], 0, "O sistema de ficheiros organiza a estrutura de dados no disco."),
        ("O que é a Nuvem (Cloud Computing)?", ["Serviços de computação prestados através da Internet", "Rede sem fios local da residência", "Transferência via Bluetooth entre telemóveis", "Backup feito numa pen drive"], 0, "A computação em nuvem fornece recursos computacionais via internet."),
        ("O que significa URL?", ["Uniform Resource Locator", "Universal Remote Link", "Unified Read Language", "User Recovery License"], 0, "URL é o endereço de rede de um recurso web."),
        ("Qual destas opções é um banco de dados relacional?", ["PostgreSQL", "MongoDB", "Redis", "Neo4j"], 0, "PostgreSQL é um sistema de gestão de bancos de dados relacional."),
        ("O que é um 'Bug' no desenvolvimento de software?", ["Um erro ou falha no código que causa comportamento inesperado", "Um vírus de computador perigoso", "Um tipo de cabo de rede", "Um programa de aceleração de downloads"], 0, "Bug é a designação dada a uma falha no código de um programa.")
    ],
    "Matemática": [
        ("Qual é o resultado da equação 3x + 9 = 24?", ["x = 5", "x = 3", "x = 8", "x = 15"], 0, "3x = 24 - 9 => 3x = 15 => x = 5."),
        ("Qual é a área de um triângulo com base de 10 cm e altura de 6 cm?", ["30 cm²", "60 cm²", "16 cm²", "20 cm²"], 0, "A área do triângulo é (Base x Altura) / 2 = 30 cm²."),
        ("Quanto é 15% de 200?", ["30", "20", "15", "40"], 0, "15% de 200 = (15/100) * 200 = 30."),
        ("Como se chama um ângulo de exatamente 90 graus?", ["Ângulo Reto", "Ângulo Agudo", "Ângulo Obtuso", "Ângulo Raso"], 0, "O ângulo reto possui amplitude exata de 90°."),
        ("Qual é a raiz quadrada de 81?", ["9", "8", "7", "81"], 0, "9 x 9 = 81, portanto a raiz é 9."),
        ("Qual é o valor de Pi (aproximadamente)?", ["3.14159", "2.71828", "1.61803", "3.00000"], 0, "Pi é a constante matemática aproximada para 3.14159."),
        ("Qual é a moda no conjunto numérico [2, 3, 5, 5, 7, 8, 5, 9]?", ["5", "2", "6", "9"], 0, "A moda é o elemento mais frequente do conjunto (número 5)."),
        ("Quanto é 2 elevado à quinta potência (2⁵)?", ["32", "10", "16", "64"], 0, "2 * 2 * 2 * 2 * 2 = 32."),
        ("Qual é o perímetro de um quadrado com lado de 8 cm?", ["32 cm", "64 cm", "16 cm", "24 cm"], 0, "Soma de todos os 4 lados: 8 * 4 = 32 cm."),
        ("Se um número é multiplicado por 0, qual é o resultado?", ["0", "1", "O próprio número", "Infinito"], 0, "Qualquer valor multiplicado por zero resulta em zero."),
        ("Em estatística, o que é a mediana?", ["O valor central que divide o conjunto ordenado ao meio", "A soma de todos os valores", "O número mais alto", "A diferença entre os extremos"], 0, "A mediana representa o centro de uma amostragem ordenada."),
        ("Qual é o teorema de Pitágoras?", ["a² + b² = c²", "a + b = c", "a * b = c²", "a² - b² = c²"], 0, "A soma dos quadrados dos catetos é igual ao quadrado da hipotenusa."),
        ("O número 17 é um número primo?", ["Sim, pois só é divisível por 1 e por ele mesmo", "Não, é um número composto", "Apenas quando multiplicado por 2", "Nenhuma das opções"], 0, "Números primos só possuem dois divisores: 1 e eles próprios."),
        ("Quanto dá a expressão: 5 + 3 * 2?", ["11", "16", "13", "10"], 0, "Multiplicação primeiro: 3 * 2 = 6, depois 5 + 6 = 11."),
        ("Qual é o fatorial de 4 (4!)?", ["24", "12", "16", "8"], 0, "4! = 4 * 3 * 2 * 1 = 24.")
    ],
    "Língua Portuguesa": [
        ("Qual das opções apresenta uma palavra proparoxítona?", ["Lâmpada", "Café", "Mesa", "Jardim"], 0, "Todas as palavras proparoxítonas têm a antepenúltima sílaba tónica e são acentuadas."),
        ("Qual é o sujeito da frase: 'Os alunos estudaram para o exame'?", ["Os alunos", "estudaram", "para o exame", "exame"], 0, "O sujeito é quem pratica a ação expressa pelo verbo."),
        ("Qual é o antónimo da palavra 'efémero'?", ["Duradouro", "Passageiro", "Rápido", "Curto"], 0, "Efémero significa algo passageiro; o seu oposto é duradouro."),
        ("Assinale a frase com a regência correta:", ["Assistimos ao filme ontem", "Assistimos o filme ontem", "Assistimos no filme ontem", "Assistimos do filme ontem"], 0, "O verbo assistir no sentido de ver exige a preposição 'a'."),
        ("Qual figura de linguagem é usada em: 'O vento uivava na noite'?", ["Personificação", "Metáfora", "Hipérbole", "Apostrofe"], 0, "Personificação atribui características humanas a seres inanimados."),
        ("Qual destas palavras é um substantivo abstrato?", ["Saudade", "Cadeira", "Livro", "Pedra"], 0, "Saudade depende de um ser vivo para existir."),
        ("Como se classifica a palavra 'rapidamente' quanto à sua formação?", ["Advérbio", "Substantivo", "Adjetivo", "Verbo"], 0, "É um advérbio de modo derivado do adjetivo rápido."),
        ("Qual é a forma correta do verbo na frase: 'Se nós _____ mais, passaríamos'?", ["estudássemos", "estudar", "estudávamos", "estudaremos"], 0, "Subjuntivo correto para exprimir uma hipótese no passado."),
        ("Qual é o plural da palavra 'Cidadão'?", ["Cidadãos", "Cidadões", "Cidadães", "Cidadases"], 0, "O plural correto de cidadão é cidadãos."),
        ("Identifique o verbo na frase: 'A menina correu no parque.'", ["correu", "menina", "parque", "no"], 0, "Correu indica a ação realizada pela menina."),
        ("O que é uma Oração Coordenada Assindética?", ["Oração ligada sem conectivos/conjunções", "Oração subordinada com 'que'", "Oração com verbo no infinitivo", "Oração sem sujeito"], 0, "Orações assindéticas são separadas apenas por vírgulas."),
        ("Qual opção contém um hiato?", ["Saúde", "Peixe", "Caixa", "Noite"], 0, "Em Sa-ú-de, as vogais ficam em sílabas separadas."),
        ("O que indica o uso das aspas numa frase?", ["Citação direta ou destaque de palavra", "Fim de uma frase declarativa", "Pergunta direta", "Pausa longa na leitura"], 0, "Aspas são usadas para destacar citações, termos estrangeiros ou ironia."),
        ("Qual é a função do pronome na língua portuguesa?", ["Substituir ou acompanhar um substantivo", "Indicar a ação principal", "Modificar a intensidade do adjetivo", "Conectar duas orações"], 0, "O pronome ocupa o lugar do nome ou acompanha-o."),
        ("Qual é o sinónimo de 'benevolente'?", ["Bondoso", "Maldoso", "Orgulhoso", "Apressado"], 0, "Benevolente é quem tem boa intenção ou bondade.")
    ],
    "Física": [
        ("Qual é a unidade de medida de força no Sistema Internacional (SI)?", ["Newton (N)", "Joule (J)", "Watt (W)", "Pascal (Pa)"], 0, "O Newton é a unidade padronizada de força no SI."),
        ("Qual é o valor aproximado da aceleração da gravidade na Terra?", ["9.8 m/s²", "5.0 m/s²", "15.2 m/s²", "1.6 m/s²"], 0, "A aceleração gravítica média na Terra é ~9.8 m/s²."),
        ("O que diz a 1ª Lei de Newton (Lei da Inércia)?", ["Um corpo mantém o seu estado de repouso ou movimento a menos que atuem forças sobre ele", "A toda a ação corresponde uma reação igual e oposta", "A força é igual à massa vezes a aceleração", "A energia não se cria nem se destrói"], 0, "A inércia é a tendência dos corpos de resistir a mudanças no seu estado de movimento."),
        ("Qual é a fórmula para calcular a Velocidade Média?", ["v = Δs / Δt", "v = m * a", "v = F * d", "v = m / V"], 0, "Velocidade média é a variação da posição dividida pelo tempo decorrido."),
        ("Qual é a unidade de medida da potência elétrica?", ["Watt (W)", "Volt (V)", "Ampere (A)", "Ohm (Ω)"], 0, "O Watt mede a taxa de conversão ou consumo de energia por segundo."),
        ("A energia associada ao movimento de um corpo é chamada de:", ["Energia Cinética", "Energia Potencial Gravítica", "Energia Térmica", "Energia Nuclear"], 0, "Energia cinética depende da massa e da velocidade do objeto."),
        ("Qual é o fenómeno de curvatura da luz ao mudar de meio de propagação?", ["Refração", "Reflexão", "Difração", "Polarização"], 0, "A refração ocorre devido à alteração da velocidade da luz ao mudar de meio."),
        ("O que mede um manómetro?", ["Pressão de fluidos", "Temperatura corporal", "Corrente elétrica", "Massa de um sólido"], 0, "Manómetros medem a pressão exercida por líquidos ou gases."),
        ("O que diz a 3ª Lei de Newton?", ["A toda a ação corresponde uma reação de igual intensidade e sentido oposto", "Os planetas orbitam em elipses", "A energia total é constante", "A força depende da massa"], 0, "Princípio da Ação e Reação."),
        ("Qual é o instrumento usado para medir a corrente elétrica?", ["Amperímetro", "Voltímetro", "Termómetro", "Barómetro"], 0, "O amperímetro mede a intensidade de corrente em amperes."),
        ("O som propaga-se no vácuo?", ["Não, porque precisa de um meio material", "Sim, na velocidade da luz", "Sim, mas muito devagar", "Apenas em altas temperaturas"], 0, "O som é uma onda mecânica e necessita de matéria para se propagar."),
        ("Qual é a Lei de Ohm referente à resistência elétrica?", ["V = R * I", "F = m * a", "E = m * c²", "P = V * I * t"], 0, "A tensão (V) é o produto da resistência (R) pela corrente (I)."),
        ("A passagem direta do estado sólido para o estado gasoso chama-se:", ["Sublimação", "Fusão", "Vaporização", "Condensação"], 0, "Sublimação é a transição direta do sólido ao gás."),
        ("Qual é a velocidade aproximada da luz no vácuo?", ["300.000 km/s", "1.500 km/s", "340 m/s", "100.000 km/h"], 0, "A luz viaja a cerca de 3 x 10⁸ metros por segundo no vácuo."),
        ("O que mede a escala Kelvin?", ["Temperatura absoluta", "Pressão atmosférica", "Luminosidade", "Radioatividade"], 0, "Kelvin é a unidade de temperatura no SI onde 0 K é o zero absoluto.")
    ],
    "Química": [
        ("Qual é o símbolo químico da água?", ["H₂O", "CO₂", "NaCl", "O₂"], 0, "A água é composta por dois átomos de hidrogénio e um de oxigénio."),
        ("Qual é o elemento químico mais abundante no universo?", ["Hidrogénio", "Oxigénio", "Carbono", "Hélio"], 0, "O hidrogénio representa cerca de 75% de toda a matéria elementar do universo."),
        ("Qual é o valor do pH neutro a 25°C?", ["7", "0", "14", "5"], 0, "pH 7 representa neutralidade (nem ácido nem básico)."),
        ("Qual destas opções é um gás nobre?", ["Hélio", "Nitrogénio", "Cloro", "Sódio"], 0, "O Hélio pertence ao Grupo 18 (gases nobres), sendo quimicamente inerte."),
        ("O que acontece numa reação de oxidação?", ["Perda de eletrões", "Ganho de eletrões", "Ganho de protões", "Perda de neutrões"], 0, "Oxidação é o processo químico no qual uma espécie perde eletrões."),
        ("Qual é o número atómico do Carbono?", ["6", "12", "1", "8"], 0, "O Carbono possui 6 protões no seu núcleo atómico."),
        ("Qual é a tabela que organiza os elementos químicos conhecidos?", ["Tabela Periódica", "Tabela de Mendeleev Clássica", "Diagrama de Linus Pauling", "Gráfico de Solubilidade"], 0, "A Tabela Periódica organiza os elementos em função das suas propriedades."),
        ("Como é chamada a ligação onde ocorre a partilha de eletrões?", ["Ligação Covalente", "Ligação Iónica", "Ligação Metálica", "Pontes de Hidrogénio"], 0, "Na ligação covalente, os átomos partilham pares de eletrões."),
        ("Qual é o nome da mudança do estado líquido para o gasoso?", ["Vaporização", "Solidificação", "Fusão", "Sublimação"], 0, "Vaporização é a passagem da fase líquida para a fase gasosa."),
        ("Qual é o elemento cujo símbolo químico é Fe?", ["Ferro", "Flúor", "Fósforo", "Francio"], 0, "Fe vem do latim 'Ferrum'."),
        ("Misturas homogéneas também são chamadas de:", ["Soluções", "Colóides", "Suspensões", "Emulsões"], 0, "Uma solução é uma mistura homogénea com uma única fase visível."),
        ("Qual é a carga elétrica de um neutrão?", ["Neutra (zero)", "Positiva (+1)", "Negativa (-1)", "Variável"], 0, "Os neutrões no núcleo atómico não possuem carga elétrica."),
        ("O que é um catião?", ["Um ião de carga positiva", "Um ião de carga negativa", "Um átomo neutro", "Uma partícula do núcleo"], 0, "Catiões são formados quando um átomo perde um ou mais eletrões."),
        ("Qual ácido está presente no suco gástrico do estômago humano?", ["Ácido Clorídrico (HCl)", "Ácido Sulfúrico", "Ácido Acético", "Ácido Nítrico"], 0, "O HCl ajuda na digestão dos alimentos no estômago."),
        ("Qual é a massa molar aproximada do Oxigénio (O₂)?", ["32 g/mol", "16 g/mol", "8 g/mol", "64 g/mol"], 0, "Cada átomo de oxigénio tem massa ~16 g/mol; a molécula O₂ tem 32 g/mol.")
    ],
    "História": [
        ("Em que ano teve início a Segunda Guerra Mundial?", ["1939", "1914", "1945", "1918"], 0, "A Segunda Guerra Mundial começou em setembro de 1939 com a invasão da Polónia."),
        ("Quem foi o primeiro imperador de Roma?", ["Augusto", "Júlio César", "Nero", "Calígula"], 0, "Octávio Augusto tornou-se o primeiro imperador romano em 27 a.C."),
        ("Qual civilização antiga construiu as Pirâmides de Gizé?", ["Egípcia", "Mesopotâmica", "Grega", "Romana"], 0, "Os antigos egípcios ergueram as pirâmides na região de Gizé."),
        ("Em que século ocorreu a Revolução Francesa?", ["Século XVIII (1789)", "Século XIX", "Século XVI", "Século XVII"], 0, "A Revolução Francesa iniciou-se em 1789."),
        ("Qual evento marcou o fim da Idade Média em 1453?", ["A Queda de Constantinopla", "A Descoberta da América", "A Invenção da Imprensa", "A Peste Negra"], 0, "A tomada de Constantinopla pelos otomanos marcou o fim do Império Bizantino."),
        ("Quem pintou o teto da Capela Sistina?", ["Miguel Ângelo", "Leonardo da Vinci", "Rafael", "Donatello"], 0, "Miguel Ângelo pintou os afrescos do teto da Capela Sistina em Roma."),
        ("O que foi a Guerra Fria?", ["Conflito ideológico e político entre EUA e União Soviética", "Guerra travada no inverno europeu", "Invasão do Polo Norte", "Conflito direto entre China e Japão"], 0, "Guerra Fria foi o período de tensão geopolítica sem combate direto entre as duas superpotências."),
        ("Qual navio afundou em 1912 após colidir com um iceberg?", ["Titanic", "Lusitania", "Britannic", "Bismarck"], 0, "O RMS Titanic afundou na sua viagem inaugural no Atlântico Norte."),
        ("Quem escreveu as '95 Teses' iniciando a Reforma Protestante?", ["Martinho Lutero", "João Calvino", "Henrique VIII", "Inácio de Loyola"], 0, "Martinho Lutero afixou as 95 Teses na igreja de Wittenberg em 1517."),
        ("Qual civilização pré-colombiana habitava a região do Peru e dos Andes?", ["Incas", "Astecas", "Maias", "Olmecas"], 0, "O Império Inca dominava a cordilheira dos Andes na América do Sul."),
        ("Qual era a capital do Império Bizantino?", ["Constantinopla", "Atenas", "Roma", "Alexandria"], 0, "Constantinopla (atual Istambul) era o centro bizantino."),
        ("Quem proclamou a independência dos Estados Unidos em 1776?", ["As 13 Colónias americanas", "A Coroa Britânica", "A França de Luís XVI", "O Império Espanhol"], 0, "A Declaração de Independência foi assinada pelos representantes das 13 Colónias."),
        ("Em que ano caiu o Muro de Berlim?", ["1989", "1991", "1975", "1961"], 0, "A queda do Muro em novembro de 1989 simbolizou o fim do bloco soviético europeu."),
        ("Qual tratado pôs fim oficialmente à Primeira Guerra Mundial?", ["Tratado de Versalhes", "Tratado de Tordesilhas", "Pacto de Varsóvia", "Tratado de Utrecht"], 0, "Assinado em 1919 pelas potências europeias."),
        ("Como se chamava o sistema socioeconómico predominante na Europa Medieval?", ["Feudalismo", "Capitalismo", "Mercantilismo", "Socialismo"], 0, "O Feudalismo baseava-se em relações de suserania, vassalagem e trabalho servil.")
    ],
    "Biologia": [
        ("Qual é a unidade fundamental da vida em todos os seres vivos?", ["Célula", "Átomo", "Tecido", "Órgão"], 0, "A célula é a menor unidade estrutural e funcional dos organismos."),
        ("Onde ocorre a fotossíntese nas plantas?", ["Nos Cloroplastos", "Nas Mitocôndrias", "No Núcleo", "Nos Ribossomas"], 0, "Os cloroplastos contêm clorofila, o pigmento responsável pela fotossíntese."),
        ("Qual organelo celular é responsável pela respiração celular e produção de ATP?", ["Mitocôndria", "Complexo de Golgi", "Lisossoma", "Retículo Endoplasmático"], 0, "As mitocôndrias produzem a energia química necessária para a célula."),
        ("O que significa a sigla ADN (DNA)?", ["Ácido Desoxirribonucleico", "Ácido Ribonucleico", "Ácido Acelular Primário", "Molécula de Adenina Dupla"], 0, "O ADN carrega as instruções genéticas dos organismos."),
        ("Qual é o processo de divisão celular que produz gâmetas?", ["Meiose", "Mitose", "Bipartição", "Gemação"], 0, "A meiose reduz o número de cromossomas para metade na formação dos gâmetas."),
        ("Como se chamam os organismos capazes de produzir o seu próprio alimento?", ["Autótrofos", "Heterótrofos", "Decompositores", "Consumidores"], 0, "Autótrofos (como as plantas) sintetizam compostos orgânicos a partir de luz ou compostos inorgânicos."),
        ("Qual destas opções é um vaso sanguíneo que transporta sangue do coração para o corpo?", ["Artéria", "Veia", "Capilar", "Válvula"], 0, "As artérias conduzem sangue rico em oxigénio que sai do coração."),
        ("Qual sistema do corpo humano é responsável pela defesa contra infeções?", ["Sistema Imunitário", "Sistema Nervoso", "Sistema Endócrino", "Sistema Digestivo"], 0, "O sistema imunitário combate patógenos como vírus e bactérias."),
        ("Que nome se dá ao conjunto de indivíduos da mesma espécie que habitam a mesma área?", ["População", "Comunidade", "Ecossistema", "Biosfera"], 0, "Uma população agrupa organismos da mesma espécie no mesmo local."),
        ("Qual o maior órgão do corpo humano?", ["Pele", "Fígado", "Pulmão", "Intestino"], 0, "A pele reveste todo o corpo e é o maior órgão em extensão e massa."),
        ("O que é o fenómeno da Seleção Natural?", ["Mecanismo evolutivo proposto por Charles Darwin", "Mutação artificial em laboratório", "Extinção imediata de espécies velhas", "Clone de plantas"], 0, "Indivíduos com traços mais favoráveis têm maior probabilidade de sobreviver e reproduzir-se."),
        ("Qual das opções é um exemplo de fungo?", ["Cogumelo", "Alga verde", "Bactéria E. coli", "Acaro"], 0, "Os cogumelos pertencem ao Reino Fungi."),
        ("Que organelo realiza a síntese de proteínas na célula?", ["Ribossoma", "Vacúolo", "Centríolo", "Peroxissoma"], 0, "Os ribossomas traduzem o ARN para montar cadeias de aminoácidos/proteínas."),
        ("Qual hormona regula os níveis de glicose no sangue?", ["Insulina", "Adrenalina", "Tiroxina", "Melatonina"], 0, "A insulina facilita a entrada de glicose nas células."),
        ("Organismos que se alimentam de matéria orgânica morta são chamados de:", ["Decompositores", "Produtores", "Predadores Topo", "Herbívoros"], 0, "Fungos e bactérias decompositoras reciclam nutrientes na natureza.")
    ],
    "Inglês": [
        ("Qual é o passado simples do verbo 'To Go'?", ["Went", "Gone", "Goes", "Going"], 0, "'Went' é a forma irregular do passado de 'Go'."),
        ("Escolha a opção com o artigo correto: 'I saw _____ elephant at the zoo.'", ["an", "a", "the", "some"], 0, "Usa-se 'an' antes de palavras que iniciam com som de vogal."),
        ("Qual é o oposto do adjetivo 'Expensive'?", ["Cheap", "Costly", "High", "Rich"], 0, "'Cheap' significa barato, o oposto de caros/expensive."),
        ("O que significa a expressão 'How old are you?' em português?", ["Quantos anos tens?", "Como estás?", "De onde és?", "Qual é o teu nome?"], 0, "É a pergunta padrão para questionar a idade de alguém."),
        ("Qual destas palavras é um pronome possessivo em inglês?", ["Mine", "Me", "I", "Myself"], 0, "'Mine' indica posse (meu/minha)."),
        ("Como se diz 'Quarta-feira' em inglês?", ["Wednesday", "Tuesday", "Thursday", "Friday"], 0, "Wednesday é a quarta-feira."),
        ("Qual é o plural correto da palavra 'Child'?", ["Children", "Childs", "Childes", "Childrens"], 0, "Child tem um plural irregular: children."),
        ("Escolha a forma correta: 'She _____ to school every day.'", ["walks", "walk", "walking", "walked"], 0, "Na 3ª pessoa do singular no Present Simple, adiciona-se 's' ao verbo."),
        ("O que significa o verbo phrasal 'Give up'?", ["Desistir", "Continuar", "Entregar", "Subir"], 0, "'Give up' significa abandonar ou desistir de algo."),
        ("Qual é o comparativo de superioridade do adjetivo 'Good'?", ["Better", "Gooder", "Best", "More good"], 0, "'Good' possui o comparativo irregular 'better'."),
        ("O que significa 'To make a decision'?", ["Tomar uma decisão", "Fazer um trabalho", "Decidir nada", "Escrever uma ideia"], 0, "Tradução da locução verbal idiomática."),
        ("Qual das opções é um advérbio de frequência?", ["Always", "Quick", "Soft", "Red"], 0, "'Always' (sempre) indica a frequência de uma ação."),
        ("Como se escreve o número 12 em inglês?", ["Twelve", "Twelfth", "Twenty", "Ten-two"], 0, "Twelve é a grafia de 12."),
        ("Qual é a tradução de 'Library'?", ["Biblioteca", "Livraria", "Laboratório", "Liberdade"], 0, "'Library' é um falso amigo (falso cognato) que significa Biblioteca."),
        ("Complete a frase: 'If it rains, we _____ stay at home.'", ["will", "would", "are", "did"], 0, "Primeira condicional em inglês usa Present Simple + Will.")
    ]
}

def obter_15_perguntas_unicas(disciplina):
    questoes = BANCO_DE_PERGUNTAS.get(disciplina, BANCO_DE_PERGUNTAS["Informática"])
    amostra = random.sample(questoes, min(15, len(questoes)))
    
    lista_final = []
    for q_texto, opcoes_orig, resp_idx, exp in amostra:
        opcoes = list(opcoes_orig)
        correta_texto = opcoes[resp_idx]
        random.shuffle(opcoes)
        novo_idx = opcoes.index(correta_texto)

        lista_final.append({
            "pergunta": q_texto,
            "opcoes": opcoes,
            "resposta_correta": novo_idx,
            "explicacao": exp
        })
    return lista_final

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gerar-quiz', methods=['POST'])
def gerar_quiz():
    modo = request.form.get('modo', 'disciplina')
    disciplina = request.form.get('disciplina', 'Informática')

    prompt_instrucoes = f"""
    Cria EXATAMENTE 15 PERGUNTAS ÚNICAS de escolha múltipla sobre {disciplina}.

    [REGRAS]
    - QUANTIDADE OBRIGATÓRIA: EXATAMENTE 15 PERGUNTAS.
    - DISCIPLINA: {disciplina}
    - NENHUMA PERGUNTA PODE SER REPETIDA.
    - Respostas teóricas e académicas rigorosas.

    [FORMATO JSON APENAS]
    [
      {{
        "pergunta": "Enunciado...",
        "opcoes": ["Certa", "Errada 1", "Errada 2", "Errada 3"],
        "resposta_correta": 0,
        "explicacao": "Explicação..."
      }}
    ]
    """

    try:
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,
            top_p=0.9,
            max_output_tokens=8192,
            response_mime_type="application/json"
        )
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)

        if modo == 'foto' and 'foto' in request.files and request.files['foto'].filename != '':
            ficheiro = request.files['foto']
            imagem = Image.open(ficheiro.stream)
            imagem.thumbnail((800, 800))
            prompt_final = f"{prompt_instrucoes}\n\nAnalisa a foto/documento anexado e gera 15 perguntas únicas do conteúdo."
            resposta = model.generate_content([prompt_final, imagem])
        else:
            prompt_final = f"{prompt_instrucoes}\n\nGera 15 perguntas inéditas para {disciplina}."
            resposta = model.generate_content(prompt_final)

        texto = resposta.text.strip()
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

        if len(quiz_limpo) >= 15:
            return jsonify({"perguntas": quiz_limpo[:15]})
        else:
            return jsonify({"perguntas": obter_15_perguntas_unicas(disciplina)})

    except Exception as e:
        print(f"⚠️ A usar banco estático de reserva: {e}")
        return jsonify({"perguntas": obter_15_perguntas_unicas(disciplina)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)