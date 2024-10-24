from flask import Flask, render_template, request
from PIL import Image
import time
import io
import base64

app = Flask(__name__)

def hide_message(message, image):
    encoded = image.copy()
    width, height = image.size
    pixels = encoded.load()

    # Converter a mensagem para binário
    binary_message = ''.join(format(ord(i), '08b') for i in message) + '1111111111111110'

    data_index = 0
    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])
            for i in range(3): #Alterar os 3 primeiros valores RGB do pixel
                if data_index < len(binary_message):
                    pixel[i] = pixel[i] & ~1 | int(binary_message[data_index])
                    data_index += 1
                
            pixels[x, y] = tuple(pixel)
            if data_index >= len(binary_message):
                break
        if data_index >=len(binary_message):
            break
    return encoded

def reveal_message(image):
    binary_message = ''
    pixels = image.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])
            for i in range(3): # Extrair os 3 primeiros valores RGB do pixel
                binary_message += str(pixel[i] & 1)

    # Verificar o fim da mensagem com o terminador (1111111111111110)
    terminator = '1111111111111110'
    index_of_terminator = binary_message.find(terminator)

    # Se o terminador for encontrado, cortar a mensagem
    if index_of_terminator != -1:
        binary_message = binary_message[:index_of_terminator]

    # Converter de binário para texto
    decoded_message = ''
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        decoded_message += chr(int(byte, 2))

    return decoded_message

@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota codificar
@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        file = request.files['image']
        message = request.form['message']

        #Abrir a imagem e ocultar a mensagem
        img = Image.open(file)
        encoded_img = hide_message(message, img)

        # Nome da imagem com timestamp
        timestamp = str(int(time.time()))
        img_filename = f'encoded_{timestamp}.png'

        # Salvar a imagem codificada em um objeto de bytes
        img_io = io.BytesIO()
        encoded_img.save(img_io, 'PNG')
        img_io.seek(0)

        return render_template(
            'encode.html',
            image_data=img_io.getvalue(),
            img_filename=img_filename
        )

    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        file = request.files['image']

        # Abrir a imagem e revelar a mensagem
        image = Image.open(file)
        hidden_message = reveal_message(image)

        return render_template(
            'decode.html',
            message=hidden_message
        )
    return render_template('decode.html')