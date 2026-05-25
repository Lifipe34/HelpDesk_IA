from flask import Flask, request, jsonify
import joblib
from google import genai 
import json             # <-- NOVO
import io               # <-- NOVO
from PIL import Image   # <-- NOVO

app = Flask(__name__)

cliente_gemini = genai.Client(api_key="AIzaSyAIycZIw5y_LOEt2ep0CqD_9U2SBawmsfo")

modelo_classificador = joblib.load("modelo_classificador.pkl")


categorias_config = {
    "login": {"prioridade": "baixa", "resposta_base": "Para recuperar seu acesso, clique em 'Esqueci minha senha' na tela inicial."},
    "cadastro": {"prioridade": "baixa", "resposta_base": "Para se cadastrar, acesse a área 'Minha Conta' e preencha seus dados."},
    "produto": {"prioridade": "baixa", "resposta_base": "As especificações completas do produto estão na página de detalhes do item."},
    "estoque": {"prioridade": "média", "resposta_base": "Se o item está sem estoque, clique em 'Avise-me' para ser notificado."},
    "carrinho": {"prioridade": "média", "resposta_base": "Tente limpar o cache do seu navegador se o carrinho estiver apresentando erros."},
    "pagamento": {"prioridade": "alta", "resposta_base": "Verifique o status do pagamento na seção 'Meus Pedidos'."},
    "cupom": {"prioridade": "média", "resposta_base": "Verifique se o cupom está na validade e se o produto faz parte da promoção."},
    "pedido": {"prioridade": "média", "resposta_base": "Você pode acompanhar os detalhes na aba 'Meus Pedidos'."},
    "entrega": {"prioridade": "alta", "resposta_base": "O prazo de entrega varia pelos Correios/Transportadora. Acompanhe pelo rastreio."},
    "cancelamento": {"prioridade": "crítica", "resposta_base": "Vamos processar seu cancelamento. O estorno ocorrerá na mesma forma de pagamento."}
}

banco_pedidos = {
    "1001": {
        "cliente": "João Silva",
        "produto": "Notebook Dell",
        "status_pedido": "aguardando pagamento",
        "status_pagamento": "pendente",
        "metodo_pagamento": "Pix",
        "status_entrega": "não enviado"
    },
    "1002": {
        "cliente": "Maria Souza",
        "produto": "Smartphone Samsung",
        "status_pedido": "em trânsito",
        "status_pagamento": "aprovado",
        "metodo_pagamento": "Cartão de Crédito",
        "status_entrega": "caminho da entrega"
    },
    "1003": {
        "cliente": "Carlos Eduardo",
        "produto": "Monitor LG 29 ultrawide",
        "status_pedido": "entregue",
        "status_pagamento": "aprovado",
        "metodo_pagamento": "Pix",
        "status_entrega": "entregue"
    }
}

@app.route('/classificar', methods=['POST'])
def classificar():
    dados = request.get_json()
    mensagem_cliente = dados['mensagem']
    categoria_prevista = modelo_classificador.predict([mensagem_cliente])[0]
    config = categorias_config.get(categoria_prevista, {"prioridade": "indefinida", "resposta_base": ""})
    
    return jsonify({
        "categoria": categoria_prevista,
        "prioridade": config["prioridade"],
        "resposta_base": config["resposta_base"]
    })

@app.route('/atender', methods=['POST'])
def atender():
    dados = request.get_json()
    if not dados or 'mensagem' not in dados:
        return jsonify({"erro": "Envie um JSON com a 'mensagem'."}), 400

    mensagem_cliente = dados['mensagem']


    categoria = modelo_classificador.predict([mensagem_cliente])[0]
    config = categorias_config.get(categoria, {"prioridade": "indefinida", "resposta_base": "Encaminhe para um atendente humano."})

    prompt = f"""
    Você é um atendente de suporte virtual amigável de uma loja online.
    
    Mensagem do cliente: "{mensagem_cliente}"
    Categoria do problema: {categoria}
    Prioridade: {config['prioridade']}
    Solução recomendada pela empresa: {config['resposta_base']}
    
    Sua tarefa: 
    Gere uma resposta humanizada, empática e em formato de passo a passo para o cliente, baseando-se APENAS na 'Solução recomendada pela empresa'. 
    Não prometa prazos ou coisas que não estão na solução recomendada.
    """

    try:
        resposta_ia = cliente_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        texto_final = resposta_ia.text
    except Exception as e:

        print(f"Detalhe do erro do Gemini: {e}")
        return jsonify({"erro": f"A IA falhou: {str(e)}"}), 500

    return jsonify({
        "categoria_identificada": categoria,
        "prioridade": config["prioridade"],
        "resposta_humanizada": texto_final
    })

# --- NOVO ENDPOINT DA FASE 3 (VISÃO COMPUTACIONAL E DECISÃO) ---
@app.route('/atendimento_avancado', methods=['POST'])
def atendimento_avancado():
    # 1. Agora recebemos dados via Formulário (multipart/form-data) porque tem arquivo
    mensagem_cliente = request.form.get('mensagem')
    numero_pedido = request.form.get('numero_pedido')

    if not mensagem_cliente or not numero_pedido:
        return jsonify({"erro": "Envie 'mensagem' e 'numero_pedido' no formulário."}), 400

    # 2. Receber a imagem do cliente
    if 'imagem' not in request.files:
        return jsonify({"erro": "Envie o arquivo de 'imagem'."}), 400

    arquivo_imagem = request.files['imagem']
    
    # "Abrimos" a imagem na memória para o Gemini conseguir olhar
    imagem = Image.open(io.BytesIO(arquivo_imagem.read()))

    # 3. Classificar o problema usando o modelo da Fase 1
    categoria = modelo_classificador.predict([mensagem_cliente])[0]
    config = categorias_config.get(categoria, {"prioridade": "indefinida", "resposta_base": ""})

    # 4. Consultar os dados do pedido no nosso banco "fake"
    pedido_info = banco_pedidos.get(numero_pedido)
    pedido_encontrado = pedido_info is not None

    # 5. Criar o super prompt com o contexto completo para a IA
    prompt = f"""
    Você é um atendente de suporte avançado de uma loja online.
    
    Mensagem do cliente: "{mensagem_cliente}"
    Número do pedido: {numero_pedido}
    Dados do pedido no sistema: {pedido_info if pedido_encontrado else 'Pedido não encontrado'}
    Categoria do problema: {categoria}
    Solução padrão: {config['resposta_base']}

    O cliente enviou uma imagem anexa.
    
    Sua tarefa:
    1. Analise a imagem com cuidado.
    2. Compare o que está na imagem com os 'Dados do pedido no sistema' e a reclamação do cliente.
    3. Decida se é necessário abrir um chamado para um humano (ex: se o sistema diz aguardando pagamento, mas o print mostra que o cliente pagou, ou se for um erro sistêmico na imagem).
    4. Crie uma resposta final amigável orientando o cliente.

    Retorne APENAS um JSON válido (sem marcações Markdown) com esta estrutura exata:
    {{
        "abrir_chamado": true (ou false),
        "analise_da_imagem": "sua analise breve",
        "resposta_cliente": "Sua resposta humanizada aqui"
    }}
    """

    try:
        # A IA processa o texto E a imagem ao mesmo tempo!
        resposta_ia = cliente_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, imagem]
        )
        
        # Limpar a resposta da IA para garantir que seja um JSON perfeito
        texto_json = resposta_ia.text.replace('```json', '').replace('```', '').strip()
        decisao_ia = json.loads(texto_json)

    except Exception as e:
        print(f"Erro na IA: {e}")
        return jsonify({"erro": f"A IA falhou ao analisar a imagem: {str(e)}"}), 500

    # 6. Montar a resposta estruturada exatamente como o Prof. Jaime pediu no PDF!
    resposta_final = {
        "categoria": categoria,
        "prioridade": config["prioridade"],
        "dados_pedido": {
            "encontrado": pedido_encontrado,
            "numero_pedido": numero_pedido,
            "dados": pedido_info if pedido_encontrado else {}
        },
        "decisao_ia": decisao_ia
    }

    return jsonify(resposta_final)

if __name__ == '__main__':
    print("API do HelpDesk + Gemini Rodando! Aguardando chamados...")
    app.run(debug=True)