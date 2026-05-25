import requests

cliente_json = {
    "mensagem": "Coloquei o código de desconto de 20% mas deu erro no valor final. Me ajude!"
}

print("Enviando mensagem para a API...")
resposta = requests.post("http://127.0.0.1:5000/atender", json=cliente_json)

# Verificamos se a requisição deu 100% certo (Código HTTP 200)
if resposta.status_code == 200:
    dados_retorno = resposta.json()
    print("\n✅ SUCESSO!")
    print(f"Categoria: {dados_retorno['categoria_identificada']}")
    print(f"Prioridade: {dados_retorno['prioridade']}\n")
    print(f"Resposta da IA:\n{dados_retorno['resposta_humanizada']}")
else:
    print(f"\n❌ ERRO NO SERVIDOR! Código: {resposta.status_code}")
    print(f"Detalhes do erro que o Flask devolveu:\n{resposta.text}")