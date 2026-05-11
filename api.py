from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# 1. Carregamos o modelo treinado que você acabou de criar
modelo = joblib.load("modelo_classificador.pkl")

# 2. Tabela de regras de negócio (Prioridades e Respostas Base)
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

# 3. Criamos o "Endpoint" (a porta de entrada da API)
@app.route('/classificar', methods=['POST'])
def classificar():
    # Recebe os dados em formato JSON
    dados = request.get_json()

    # Validação simples
    if not dados or 'mensagem' not in dados:
        return jsonify({"erro": "Formato inválido. Envie um JSON com o campo 'mensagem'."}), 400

    mensagem_cliente = dados['mensagem']

    # 4. A IA lê a frase e prevê a categoria
    categoria_prevista = modelo.predict([mensagem_cliente])[0]

    # 5. Puxamos a prioridade e a resposta_base usando a categoria que a IA encontrou
    config = categorias_config.get(categoria_prevista, {"prioridade": "indefinida", "resposta_base": "Aguarde o atendimento humano."})

    # 6. Montamos o pacote de resposta para devolver ao usuário
    resposta = {
        "categoria": categoria_prevista,
        "prioridade": config["prioridade"],
        "resposta_base": config["resposta_base"]
    }

    return jsonify(resposta)

# Inicia o servidor web
if __name__ == '__main__':
    print("API do HelpDesk Rodando! Aguardando chamados...")
    app.run(debug=True)