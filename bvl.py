import ezgmail
from datetime import datetime as dt
import csv, os
import subprocess
import platform


def get_system():
	node = platform.node()
	if 'raspberrypi' in node:
		return '/home/pi/pythonCode/bvl'
	else:
		return '/home/gabriel/pythonCode/bvl'


def httrack(url, dir):
	subprocess.run('httrack --update --skeleton --display -O' + os.path.join(dir, 'webdata') + ' ' + url, shell=True)
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


def send_gmail(to_list, subject, body, attach):
	for to in to_list:
		ezgmail.send(to, subject, body, [attach])



# Main
base_dir = get_system()
print(base_dir)
os.chdir(base_dir)
BVL_FILE = os.path.join(base_dir, 'bvl_data.csv')
raw = httrack('https://www.bvl.com.pe/mercado/movimientos-diarios', base_dir)

codes = codes(raw)
prices = prices(raw, codes)
final = combine(prices)

to_list = ['gfreundt@losportales.com.pe']  #, 'jlcastanedaherrera@gmail.com']
send_gmail(to_list, 'Cierre BVL del ' + dt.strftime(dt.now(), '%Y.%m.%d'), 'Abrirlo como CSV. No tiene fila de titulos.', BVL_FILE)