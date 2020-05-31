import pyqrcode
import xlrd

def create_qr(excelname, sheetname):
    '''create qr code from excel'''

    wb = xlrd.open_workbook(excelname)
    sheet = wb.sheet_by_name(sheetname)
    sheet.cell_value(0,0)

    for i in range(2, sheet.nrows):
        row = sheet.row_values(i)
        data = ''
        order = [0,2,1,4,5,6,7,8]
        for j in order:
                data += str(row[j]) + ' '
        print(data)
        qr = pyqrcode.create(data)
        qrname = 'pill{}.png'.format(row[0])
        qr.png(qrname, scale=4)


excelname = 'medicinefrequency.xlsx'
sheetname = 'med'
create_qr(excelname, sheetname)
print('create qr done')