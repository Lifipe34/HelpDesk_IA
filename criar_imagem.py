from PIL import Image, ImageDraw

# 1. Cria uma imagem em branco (fundo branco, tamanho 400x200 pixels)
imagem = Image.new('RGB', (400, 200), color=(255, 255, 255))
desenho = ImageDraw.Draw(imagem)

# 2. Escrevemos os textos simulando um comprovativo de transferência no ecrã
desenho.text((20, 40), "COMPROVATIVO DE PAGAMENTO PIX", fill=(0, 128, 0)) # Texto em verde
desenho.text((20, 80), "Pedido: #1001", fill=(0, 0, 0)) # Texto em preto
desenho.text((20, 110), "Valor: R$ 3.500,00", fill=(0, 0, 0))
desenho.text((20, 150), "STATUS: TRANSFERENCIA CONCLUIDA COM SUCESSO!", fill=(0, 0, 255)) # Texto em azul

# 3. Guarda a imagem na sua pasta
imagem.save('comprovativo_com_erro.png')

print("Imagem 'comprovativo_falso.png' criada com sucesso!")