from bs4 import BeautifulSoup as bs
import os
import re
import yaml

SETTTINGS_FILE='settings.yml'
HTML_FILE = 'templates/_navigation.html'

with open(SETTTINGS_FILE, 'r') as cfg:
		log_cfg = yaml.safe_load(cfg)
		RACKLOG_SITES = log_cfg.get('RACKLOG_SITES')


def add_stations():
	base = os.path.dirname(os.path.abspath(__file__))
	html = open(os.path.join(base, HTML_FILE ))
	soup = bs(html, 'html.parser')

	nav_bar_stations = soup.find_all("a", {"id": 'station'})
	if nav_bar_stations:
		for i in nav_bar_stations:
			i.decompose()
	if RACKLOG_SITES:
		nav_bar_stations = soup.find("nav", {"id": "nav_bar"})
		
		for station in RACKLOG_SITES:
			new_link = soup.new_tag('a')
			new_link['href'] = f"http://{RACKLOG_SITES[station][0]['IP']}/QMFRacklog/query"
			new_link['id'] = 'station'
			new_link.string = station + ' |'
			if (RACKLOG_SITES[station][1]['HOME']):
				new_link['style'] = "font-weight:bold"
			nav_bar_stations.append(new_link)


	with open(HTML_FILE, "wb") as f_output:
		f_output.write(soup.prettify("utf-8"))



if __name__ == '__main__':
	add_stations()
