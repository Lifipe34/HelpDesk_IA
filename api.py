from flask import Flask, request, jsonify
import joblib
from google import genai 

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

if __name__ == '__main__':
    print("API do HelpDesk + Gemini Rodando! Aguardando chamados...")
    app.run(debug=True)