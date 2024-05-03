from pdf2image import convert_from_path
import PyPDF2
import re
import glob
import os
import requests
import datetime
import json
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from market_prefixes import market
import traceback


try:
    posting_numbers_dict=market()



    def pdf_to_jpg(pdf_path, output_folder):
        """
        Конвертит все страницы в pdf документе
        в jpg и сохраняет jpg с именами posting_number
        """
        ozon_pattern = r'\d+-\d+-\d+'
        yandex_pattern = r'\b\d{9}\b'
        with open(pdf_path, "rb") as file:
            images = convert_from_path(pdf_path) #конвертит все страницы в pdf в jpg и собирает их в лист
            reader = PyPDF2.PdfReader(file) #читает pdf
            for page_num in range(len(reader.pages)):
                text=''
                page = reader.pages[page_num]
                text += page.extract_text()
                try:
                    number = re.findall(ozon_pattern, text)[0]
                    image=images[page_num]
                    image.save(f"{output_folder}/{number}.jpg", "JPEG")
                except:
                    number = re.findall(yandex_pattern, text)[0]
                    image = images[page_num]
                    image.save(f"{output_folder}/{number}.jpg", "JPEG")

    path = os.getcwd()
    pdf_pathes = glob.glob(os.path.join(path, '*.pdf')) # находит pdf файл в папке
    output_folder = path  # Папка, куда будут сохранены изображения
    for pdf_path in pdf_pathes:
        pdf_to_jpg(pdf_path, path)


    prefixes = {
        'Вод': 1,
        'Септ': 2,
        'БВод': 3,
        'Раст': 4,
        'Корм': 5
    }

    with open('Я_Импорт ozon API - логин.txt', 'r', encoding='utf-8') as file:
        data = [i for i in file]
    client_id = data[0].replace('\n', '')
    api_key = data[1].replace('\n', '')
    headers = {
        "Client-Id": client_id,
        "Api-Key": api_key
    }
    url = 'https://api-seller.ozon.ru/v3/posting/fbs/list'
    yesterday = datetime.date.today() - datetime.timedelta(days=20)
    after_10_days = yesterday + datetime.timedelta(days=20)
    payload = json.dumps({
        "dir": "ASC",
        "filter": {
            "order_id": 0,
            "since": f"{yesterday}T11:47:39.878Z",
            "to": f"{after_10_days}T11:47:39.878Z",
        },
        "limit": 1000,
    })
    resp_data = requests.post(url, headers=headers, data=payload).json()
    # with open('результат.json', 'w', encoding='utf-8') as file:
    #     json.dump(resp_data, file, indent=4, ensure_ascii=False)


    for i in resp_data['result']['postings']:
        posting_num = i['posting_number']
        sku = i['products'][0]['offer_id']
        posting_numbers_dict[posting_num] = sku


    def draw_image(name, posting_number):
        """
        Добавляет надпись на картинку
        """
        image = Image.open(name)
        resolution=f"{image.width}x{image.height}"
        if resolution!='586x945':
            text = f"Aрт. {posting_number}"
            position = (330, 900)
        else:
            text = f"Aрт. {posting_number}"
            position = (200, 685)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("Я_ArialBlack.ttf", 24)
        draw.text(position, text, font=font, fill="black")
        image.save(name)


    for file in glob.glob(os.path.join(path, '*.jpg')):
        number=file.split('\\')[-1].strip('.jpg')
        if number in posting_numbers_dict:
            prefix = ''
            try:
                for i in prefixes:
                    if i in posting_numbers_dict[number]:
                        prefix = i
                img_name = f"{prefixes[prefix]}_{posting_numbers_dict[number]}.jpg"
                posting_number = posting_numbers_dict[number]
                os.rename(file, img_name)
            except:
                count = 1
                while True:
                    try:
                        for i in prefixes:
                            if i in posting_numbers_dict[number]:
                                prefix = i
                        img_name = f"{prefixes[prefix]}_{posting_numbers_dict[number]}({count}).jpg"
                        posting_number = posting_numbers_dict[number]
                        os.rename(file, img_name)
                        break
                    except:
                        count += 1
                        continue

    # for file in glob.glob(os.path.join(path, '*.jpg')):
    #     flag = False
    #     for prefix in prefixes:
    #         if prefix in file:
    #             flag = True
    #             break
    #     if not flag:
    #         filename=file.split('\\')[-1]
    #         draw_image(filename, '', 200, 600)
    #         if '99_' not in file:
    #             os.rename(file, f"99_{filename}")

    for file in glob.glob(os.path.join(path, '*.jpg')):
        sku = file.split('\\')[-1].strip('.jpg')
        if '(' in sku:
            sku=sku.split('(')[0]
        draw_image(file, sku)


    for file in glob.glob(os.path.join(path, '*.pdf')):
        os.remove(file)
except Exception as e:
    with open('fail.txt','w', encoding='utf-8') as file:
        a=str(e)
        file.write(a)