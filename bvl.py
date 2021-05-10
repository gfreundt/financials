import yagmail
from datetime import datetime as dt
import csv
import os
import subprocess


class Basics:
	def __init__(self):
		base_path = self.find_path()
		if not base_path:
			print("PATH NOT FOUND")
			quit()
		data_path = os.path.join(base_path[:3],'Coding','bvl')
		self.SCRAPER_PATH = os.path.join(data_path,'bvl_scrape.bat')
		self.CHROMEDRIVER = os.path.join(base_path, 'chromedriver.exe')
		self.BVL_FILE = os.path.join(data_path, 'bvl.csv')
		self.HTML_PATH = os.path.join(data_path, 'html')
		self.EXTRACT_FILE = os.path.join(self.HTML_PATH, r'www.bvl.com.pe\mercado\movimientos-diarios.html')

	def find_path(self):
	    paths = (r'C:\Users\Gabriel Freundt\Google Drive\Multi-Sync',r'D:\Google Drive Backup\Multi-Sync', r'C:\users\gfreu\Google Drive\Multi-Sync')
	    for path in paths:
	        if os.path.exists(path):
	            return path


def get_source(url):
	#Get Full HTML
	#cmd = '''d:\"program files\winhttrack\httrack.exe" https://www.bvl.com.pe/mercado/movimientos-diarios -O "D:\Google Drive Backup\Multi-Sync\sharedData\data\html" --quiet'''
	#subprocess.call(cmd)
	subprocess.call(active.SCRAPER_PATH)
	with open(active.EXTRACT_FILE, 'r') as file:
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
		nidx = raw.find('</dt></dl><dl><dt>', idx) + 18
		if nidx == 17:
			return sorted(extract)
		e = get_string(raw, nidx)
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
	with open(active.BVL_FILE, mode='r') as file:
		content = [i for i in csv.reader(file, delimiter=",")]
	# upodate all current codes with new information (if it exists) or copy current one
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
	with open(active.BVL_FILE, mode='w', newline="") as file:
		w = csv.writer(file, delimiter=",")
		w.writerow(['Nemónico', 'Última', 'Fecha'])
		for line in sorted(final, key=lambda i:i[0]):
			w.writerow(line)


def send_gmail(to, subject, text_content, attach):
	user = 'gfreundt@gmail.com'
	app_password = 'brwd tjfk tpuo gimo'
	content = [text_content, attach]

	with yagmail.SMTP(user, app_password) as yag:
	    yag.send(to, subject, content)



# Main
active = Basics()
raw = get_source('https://www.bvl.com.pe/mercado/movimientos-diarios')
codes = codes(raw)
prices = prices(raw, codes)
final = combine(prices)

send_gmail('jcastaneda@gmail.com', 'Cierre BVL del ' + dt.strftime(dt.now(), '%Y.%m.%d'), 'Abrirlo como CSV.', active.BVL_FILE)
send_gmail('gfreundt@losportales.com.pe', 'Cierre BVL del ' + dt.strftime(dt.now(), '%Y.%m.%d'), 'Abrirlo como CSV.', active.BVL_FILE)