from flask import Flask, request, jsonify, render_template
import joblib
from google import genai 
import json             
import io               
from PIL import Image   

app = Flask(__name__)

# --- ROTA DA INTERFACE Flask ---
@app.route('/')
def home():
    return render_template('index.html')

cliente_gemini = genai.Client(api_key="Chave da api gemini")

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
    mensagem_cliente = request.form.get('mensagem')
    numero_pedido = request.form.get('numero_pedido')

    if not mensagem_cliente or not numero_pedido:
        return jsonify({"erro": "Envie 'mensagem' e 'numero_pedido' no formulário."}), 400

    # 2. Receber a imagem do cliente (AGORA É OPCIONAL)
    imagem = None
    if 'imagem' in request.files and request.files['imagem'].filename != '':
        arquivo_imagem = request.files['imagem']
        imagem = Image.open(io.BytesIO(arquivo_imagem.read()))

    # 3. Classificar o problema usando o modelo da Fase 1
    categoria = modelo_classificador.predict([mensagem_cliente])[0]
    config = categorias_config.get(categoria, {"prioridade": "indefinida", "resposta_base": ""})

    # 4. Consultar os dados do pedido no nosso banco "fake"
    pedido_info = banco_pedidos.get(numero_pedido)
    pedido_encontrado = pedido_info is not None

    # Ajuste: Avisamos a IA se tem imagem ou não
    aviso_imagem = "O cliente enviou uma imagem anexa. Analise-a com cuidado." if imagem else "O cliente NÃO enviou nenhuma imagem."

    # 5. Criar o super prompt com o contexto completo para a IA
    prompt = f"""
    Você é um atendente de suporte avançado de uma loja online.
    
    Mensagem do cliente: "{mensagem_cliente}"
    Número do pedido: {numero_pedido}
    Dados do pedido no sistema: {pedido_info if pedido_encontrado else 'Pedido não encontrado'}
    Categoria do problema: {categoria}
    Solução padrão: {config['resposta_base']}

    {aviso_imagem}
    
    Sua tarefa:
    1. Compare os dados do sistema com a reclamação do cliente (e com a imagem, se houver).
    2. Decida se é necessário abrir um chamado para um humano (ex: divergência de dados).
    3. Crie uma resposta final amigável orientando o cliente.

    Retorne APENAS um JSON válido (sem marcações Markdown) com esta estrutura exata:
    {{
        "abrir_chamado": true (ou false),
        "analise_da_imagem": "sua analise (ou 'Sem imagem anexada')",
        "resposta_cliente": "Sua resposta humanizada aqui"
    }}
    """

    try:
        # Se tem imagem, manda texto + imagem. Se não, manda só texto!
        conteudo_gemini = [prompt, imagem] if imagem else prompt

        resposta_ia = cliente_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=conteudo_gemini
        )
        
        texto_json = resposta_ia.text.replace('```json', '').replace('```', '').strip()
        decisao_ia = json.loads(texto_json)

    except Exception as e:
        print(f"Erro na IA: {e}")
        return jsonify({"erro": f"A IA falhou: {str(e)}"}), 500

    # 6. Montar a resposta
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