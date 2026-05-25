import requests
import json

url = "http://127.0.0.1:5000/atendimento_avancado"

# 1. Os dados de texto (a dor do cliente e o número do pedido)
dados_cliente = {
    "mensagem": "Paguei via Pix mas meu pedido continua aguardando pagamento!",
    "numero_pedido": "1001"
}

# 2. O ficheiro de imagem que acabámos de criar
ficheiros = {
    "imagem": open("comprovativo_com_erro.png", "rb") # "rb" significa ler em formato binário
}

print("A enviar mensagem, número do pedido e imagem para a IA analisar...")
resposta = requests.post(url, data=dados_cliente, files=ficheiros)

# 3. Verificar o resultado
if resposta.status_code == 200:
    print("\n✅ SUCESSO! Veja a decisão da IA:\n")
    # Imprime o JSON de resposta de forma bem formatada
    print(json.dumps(resposta.json(), indent=4, ensure_ascii=False))
else:
    print(f"\n❌ ERRO! Código: {resposta.status_code}")
    print(resposta.text)