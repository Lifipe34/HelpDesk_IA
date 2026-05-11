import requests

# Simular mensagem 
cliente_json = {
    "mensagem": "Coloquei o código de desconto de 20% mas deu erro no valor final."
}

# Enviar para API
resposta = requests.post("http://127.0.0.1:5000/classificar", json=cliente_json)

print(resposta.json())