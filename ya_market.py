import datetime
import openpyxl

import requests
from ozon import ozon, filename


with open('Импорт YaMarket API - логин.txt', 'r', encoding='utf-8') as file:
    data = [i for i in file]
campaign_id = data[0].replace('\n', '')
token = data[1].replace('\n', '')

date=str(datetime.datetime.today().date()+datetime.timedelta(1)).split('-')
date=f"{date[2]}-{date[1]}-{date[0]}"


url=f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/orders?status=&substatus=&fromDate=&toDate=&supplierShipmentDateFrom={date}&supplierShipmentDateTo={date}&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&page=&pageSize='

headers={
        "Authorization":f"{token}"
}


response=requests.get(url, headers=headers).json()
pages=int(response['pager']['pagesCount'])

wb = openpyxl.Workbook(filename)
wb.save(filename)
book = openpyxl.load_workbook(filename)
sheet=book.active
row=2
for i in range(1,5):
    sheet.cell(column=i, row=1).value = 'Яндекс Маркет'

sheet.merge_cells('A1:D1')
for i in range(pages):
    if i==0:
        response=response
    else:
        url = f'https://api.partner.market.yandex.ru/campaigns/{campaign_id}/orders?status=&substatus=&fromDate=&toDate=&supplierShipmentDateFrom={date}&supplierShipmentDateTo={date}&updatedAtFrom=&updatedAtTo=&dispatchType=&fake=&hasCis=&onlyWaitingForCancellationApprove=&onlyEstimatedDelivery=&page={i+1}&pageSize='
        response = requests.get(url, headers=headers).json()
    for i in response['orders']:
        if i['status']=='CANCELLED':
            continue
        item=i['items'][0]
        sku=item['offerId']
        quantity=item['count']
        sheet.cell(column=1, row=row).value = sku
        sheet.cell(column=2, row=row).value = quantity
        sheet.cell(column=3, row=row).value = date
        sheet.cell(column=4, row=row).value = 'FBS'
        row += 1
        book.save(filename)
ozon()
