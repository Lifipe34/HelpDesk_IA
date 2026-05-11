import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

print("Iniciando o treinamento da IA...")

df = pd.DataFrame(pd.read_csv("chamados.csv"))

X = df["mensagem"]
y = df["categoria"]

modelo = make_pipeline(TfidfVectorizer(), MultinomialNB())

modelo.fit(X, y)

joblib.dump(modelo, "modelo_classificador.pkl")

print("Treinamento concluído com sucesso!")
print("O cérebro da IA foi salvo no arquivo 'modelo_classificador.pkl'.")

teste = ["Meu pix não caiu ainda"]
previsao = modelo.predict(teste)
print(f"\nTeste Rápido: A frase '{teste[0]}' foi classificada como: '{previsao[0]}'")