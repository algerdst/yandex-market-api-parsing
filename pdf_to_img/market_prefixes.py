import os
import glob
import datetime
import json
import requests
import re
from PIL import Image
from pytesseract import pytesseract
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def market():
    pattern = r'\b\d{9}\b'
    prefixes = {
        'Вод': 1,
        'Септ': 2,
        'БВод': 3,
        'Раст': 4,
        'Корм': 5
    }

    with open('Я_Импорт YaMarket API - логин.txt', 'r', encoding='utf-8') as file:
        data = [i for i in file]
    campaign_id = data[0].replace('\n', '')
    token = data[1].replace('\n', '')
    date_from=str(datetime.datetime.today().date()-datetime.timedelta(5)).split('-')
    date_to=str(datetime.datetime.today().date()+datetime.timedelta(15)).split('-')
    date_from=f"{date_from[2]}-{date_from[1]}-{date_from[0]}"
    date_to=f"{date_to[2]}-{date_to[1]}-{date_to[0]}"

    url=f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/orders?status=&substatus=&fromDate=&toDate=&supplierShipmentDateFrom={date_from}&supplierShipmentDateTo={date_to}&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&page=&pageSize='
    headers={
            "Authorization":f"{token}"
    }

    response=requests.get(url, headers=headers).json()

    # with open('результат.json', 'w', encoding='utf-8') as file:
    #     json.dump(response, file, indent=4, ensure_ascii=False)

    posting_numbers_dict={}

    pages=int(response['pager']['pagesCount'])
    for i in range(pages):
        if i == 0:
            response = response
        else:
            page = i + 1
            url = f"https://api.partner.market.yandex.ru/campaigns/{campaign_id}/orders?status=&substatus=&fromDate=&toDate=&supplierShipmentDateFrom={date_from}&supplierShipmentDateTo={date_to}&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&page={page}&pageSize="
            response = requests.get(url, headers=headers).json()
        for i in response['orders']:
            if i['status'] == 'CANCELLED':
                continue
            posting_number=str(i['id'])
            sku=i['items'][0]['offerId']
            posting_numbers_dict[posting_number]=sku
    return posting_numbers_dict