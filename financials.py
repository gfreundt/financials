import ezgmail
from datetime import datetime as dt
import csv, os
import subprocess
import platform
import yfinance as yf
from openpyxl import Workbook


def get_system():
	node = platform.node()
	if 'raspberrypi' in node:
		return '/home/pi/pythonCode/financials'
	else:
		return '/home/gabriel/pythonCode/financials'


def httrack(url):
	os.chdir(os.path.join(dir, 'webdata'))
	subprocess.run('httrack --update --skeleton --display ' + url, shell=True)
	with open(os.path.join(dir, 'webdata', 'www.bvl.com.pe', 'mercado', 'agentes', 'listado.html'), mode='r') as file:
		return file.read()


def get_string(raw, idx):
	r = ''
	while True:
		s = raw[idx:idx+1]
		if s=="<":
			return r.strip()
		else:
			r += s
			idx += 1


def codes(raw):
	idx = 0
	extract=[]
	while True:
		nidx = raw.find('<dl><dt>', idx) + 8
		if nidx == 7:
			return sorted(extract)
		e = get_string(raw, nidx)
		if not ([i for i in e if i.islower()]):
			extract.append(e)
		idx = int(nidx)


def prices(raw, codes):
	extract=[]
	for code in codes:
		nidx = raw.find(">"+code+"<") + len(code) + 12
		e = get_string(raw, nidx).replace(',','')
		extract.append(float(e))
	return list(zip(codes, extract, [dt.strftime(dt.now(),'%d-%m-%Y')]*len(codes)))


def combine(prices):
	final = []
	with open(BVL_FILE, mode='r') as file:
		content = [i for i in csv.reader(file, delimiter=",")]
	# update all current codes with new information (if it exists) or copy current one
	for code in content[1:]:
		appending = [i for i in prices if i[0] == code[0]]
		if not appending:
			to_append = code[:]
		else:
			to_append = appending[0]
		final.append(to_append)
	# add new codes from new information not in current codes
	for code in prices:
		if code not in final:
			final.append(code)
	# rewrite file
	with open(BVL_FILE, mode='w', newline="") as file:
		w = csv.writer(file, delimiter=",")
		for line in sorted(final, key=lambda i:i[0]):
			w.writerow(line)


def select_data(data, selected):
    result = []
    for field in selected:
        #print(f'Key: {field} - Value: {data[field]}')
        result.append(data[field])
    return result


def write_file(headers, data):
    workbook = Workbook()
    sheet = workbook.active

    for i, header in enumerate(headers, start=1):
        sheet['A'+str(i)] = header

    for r, row_data in enumerate(data, start=66):
        for c, col_data in enumerate(row_data, start=1):
            coords = chr(r) + str(c)
            sheet[coords] = col_data

    workbook.save(filename=YF_FILE)


def send_gmail(to_list, subject, body, attach):
	for to in to_list:
		ezgmail.send(to, subject, body, [attach])



# Common definitions
os.chdir(get_system())
send_to_list = ['gfreundt@losportales.com.pe'] #, 'jlcastanedaherrera@gmail.com']

# Yahoo Finance
YF_FILE = 'yf_tickers.xlsx'
tickers = ['G', 'AAPL', 'T', 'KO']
fields_to_extract = ['symbol', 'ebitdaMargins', 'profitMargins', 'grossMargins', 'revenueGrowth', 'operatingMargins', 'ebitda', 'targetLowPrice',
                     'returnOnAssets', 'numberOfAnalystOpinions', 'targetMeanPrice', 'returnOnEquity', 'targetHighPrice',
                     'quickRatio', 'recommendationMean', 'trailingAnnualDividendYield', 'payoutRatio', 'trailingAnnualDividendRate',
                     'expireDate', 'yield', 'algorithm', 'dividendRate', 'exDividendDate', 'currency', 'trailingPE',
                     'priceToSalesTrailing12Months', 'forwardPE', 'maxAge', 'fromCurrency', 'fiveYearAvgDividendYield']
compose = []
for ticker in tickers:
    t = yf.Ticker(ticker)
    # get stock info
    compose.append(select_data(t.info, fields_to_extract))
write_file(headers=fields_to_extract, data=compose)

# Bolsa de Valores de Lima
BVL_FILE = 'bvl_data.csv'
url = httrack('https://www.bvl.com.pe/mercado/movimientos-diarios')
codes = codes(url)
prices = prices(url, codes)
final = combine(prices)

# Cerrar mandando mail con attachments
send_gmail(send_to_list, subject='Información Financiera del ' + dt.strftime(dt.now(), '%Y.%m.%d'), body='Contenido:\n1. Cierre BVL del día\n2. Yahoo Finance Ticker Data', attach=[BVL_FILE, YF_FILE])