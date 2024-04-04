import openpyxl

import requests
import json
import datetime


with open('Импорт ozon API - логин.txt', 'r', encoding='utf-8') as file:
    data = [i for i in file]
client_id = data[0].replace('\n', '')
api_key = data[1].replace('\n', '')
headers = {
    "Client-Id": client_id,
    "Api-Key": api_key
}

url = 'https://api-seller.ozon.ru/v3/posting/fbs/list'
yesterday = datetime.date.today()- datetime.timedelta(days=1)
after_10_days = yesterday + datetime.timedelta(days=10)
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

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

filename=f'market - заказы {str(tomorrow)}.xlsx'

def ozon():
    book = openpyxl.load_workbook(filename)
    sheet=book.active
    for i in range(6, 10):
        sheet.cell(column=i, row=1).value = 'Ozon'
    sheet.merge_cells('F1:J1')
    row=2

    for i in resp_data['result']['postings']:
        date_time_str=i['shipment_date'][:10]
        date= datetime.datetime.strptime(date_time_str, '%Y-%m-%d')
        date=date.date()
        if date==tomorrow:
            sku=i['products'][0]['offer_id']
            quantity=i['products'][0]['quantity']

            sheet.cell(column=6, row=row).value = sku
            sheet.cell(column=7, row=row).value = quantity
            sheet.cell(column=8, row=row).value = date
            sheet.cell(column=9, row=row).value = 'FBS'
            sheet.cell(column=10, row=row).value = i['delivery_method']['warehouse']
            row+=1
            book.save(filename)
    book.close()


