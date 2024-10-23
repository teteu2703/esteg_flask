from flask import Flask, render_template, request
from PIL import Image
import time
import io

app = Flask(__name__)

def hide_message(message, image):
    encoded = image.copy()
    width, height = image.size
    pixels = encoded.load()

    # Converter a mensagem para binário
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    binary_message += '1111111111111110' #terminador

    data_index = 0
    for y in range(height):
        for x in range(width):
            pixel= list(pixels[x, y])
            for i in range(3): #Alterar os 3 priemeiros valores RGB do pixel
                if data_index < len(binary_message):
                    pixel[i] = pixel[i] & -1 | int(binary_message[data_index])
                    data_index += 1
                
            pixels[x, y] = tuple(pixel)
            if data_index >=len(binary_message):
                break
        if data_index >=(binary_message):
            break
    return encoded

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota codificar
@app.route('/codificar', methods=['GET', 'POST'])
def codificar():
    if request.method == 'POST':
        file = request.files['image']
        message = request.form['message']

        #Abrir a imagem e ocultar a mensagem
        img = Image.open(file)
        encoded_image = hide_message(message, img)

        # Nome da imagem com timestamp
        timestamp = str(int(time.time()))
        img_filename = f'encoded_{timestamp}.png'

        #Salvar a imagem codificada em um objeto de 
        img_io = io.BytesIO()
        encoded_img.save(img_io, 'PNG')
        img_io.seek(0)

        return render_template('decodificar.html', image_data=img_io.getvalue(), img_filename=img_filename)



    return render_template('codificar.html')