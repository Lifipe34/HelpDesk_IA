import pandas as pd
import random

# 1. Definimos as categorias, prioridades e respostas base solicitadas no projeto
categorias_config = {
    "login": {"prioridade": "baixa", "resposta": "Para recuperar seu acesso, clique em 'Esqueci minha senha' na tela inicial."},
    "cadastro": {"prioridade": "baixa", "resposta": "Para se cadastrar, acesse a área 'Minha Conta' e preencha seus dados."},
    "produto": {"prioridade": "baixa", "resposta": "As especificações completas do produto estão na página de detalhes do item."},
    "estoque": {"prioridade": "média", "resposta": "Se o item está sem estoque, clique em 'Avise-me' para ser notificado."},
    "carrinho": {"prioridade": "média", "resposta": "Tente limpar o cache do seu navegador se o carrinho estiver apresentando erros."},
    "pagamento": {"prioridade": "alta", "resposta": "Verifique o status do pagamento na seção 'Meus Pedidos'."},
    "cupom": {"prioridade": "média", "resposta": "Verifique se o cupom está na validade e se o produto faz parte da promoção."},
    "pedido": {"prioridade": "média", "resposta": "Você pode acompanhar os detalhes na aba 'Meus Pedidos'."},
    "entrega": {"prioridade": "alta", "resposta": "O prazo de entrega varia pelos Correios/Transportadora. Acompanhe pelo rastreio."},
    "cancelamento": {"prioridade": "crítica", "resposta": "Vamos processar seu cancelamento. O estorno ocorrerá na mesma forma de pagamento."}
}

# 2. Criamos frases de exemplo (o "X" da questão para a IA aprender)
frases_exemplo = [
    ("Não lembro minha senha de acesso", "login"),
    ("Onde faço minha conta?", "cadastro"),
    ("Qual o tamanho dessa TV?", "produto"),
    ("Vai voltar o tênis tamanho 40?", "estoque"),
    ("Meu carrinho esvaziou sozinho!", "carrinho"),
    ("Paguei via Pix, mas meu pedido continua aguardando pagamento", "pagamento"),
    ("Meu boleto venceu, e agora?", "pagamento"),
    ("O cartão foi recusado no checkout.", "pagamento"),
    ("Meu cupom não funciona na hora de pagar", "cupom"),
    ("Quero saber o status do meu pedido", "pedido"),
    ("O código de rastreio não atualiza, está atrasado!", "entrega"),
    ("Minha entrega não chegou no prazo.", "entrega"),
    ("Quero cancelar minha compra agora mesmo!", "cancelamento"),
    ("Preciso estornar esse valor, cancelem o pedido.", "cancelamento")
]

# 3. Geramos uma base de dados maior duplicando e embaralhando levemente para termos volume (ex: 50 linhas)
dados = []
for _ in range(50):
    frase, categoria = random.choice(frases_exemplo)
    config = categorias_config[categoria]
    
    dados.append({
        "mensagem": frase,
        "categoria": categoria,
        "prioridade": config["prioridade"],
        "resposta_base": config["resposta"]
    })

# 4. Transformamos em um DataFrame do Pandas e salvamos em CSV
df = pd.DataFrame(dados)
df.to_csv("chamados.csv", index=False, encoding="utf-8")

print("Base de dados 'chamados.csv' gerada com sucesso! Temos", len(df), "registros.")