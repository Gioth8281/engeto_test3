"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: gioth8281
email: rathpavel@icloud.com
"""
from bs4 import BeautifulSoup
import requests
import sys
import csv

def webscrap(arg_url: str) -> str:
	"""
	
	This function takes the data from the url that we entered in the command line.

	"""
	response = requests.get(arg_url)
	if response.status_code == 200:
		print(f"Downloading content from {arg_url}")
		soup = BeautifulSoup(response.content, "html.parser")
		return soup
	else:
		print(f"Failed... Response Status Code: {response.status_code}")
		sys.exit()


def get_url_zipcode(soup: str) -> dict:
	"""

	This function collects zip codes and url endings which I will then use in the get_data() function.

	"""
	content = {}
	tables = soup.select("table.table")
	for table in tables:
		raw_urls = table.find_all("td", {"class": "cislo"})
		for raw_url in raw_urls:
			zip_code = raw_url.find("a")
			url = zip_code["href"]
			content[url] = zip_code.text
	return content


def get_data(content: dict) -> list:
	"""

	This feature collects data from websites.
	Data: (Location, Registered, Envelopes, Valid, Name of Political Party, Votes of Political Parties)

	"""
	data = []
	for k in content.keys():
		temp_data = {}
		politics_name_list = []
		response = requests.get(f"https://volby.cz/pls/ps2017nss/{k}")
		soup = BeautifulSoup(response.content, "html.parser")
		h3 = soup.find_all("h3")
		for content in h3: 
			if "Obec: " in content.text:
				raw_content = content.text.replace("Obec: ", "")
				content = raw_content.replace("\n", "")
				temp_data[content] = None
				break
		table = soup.select("#ps311_t1")
		registered = table[0].find("td", {"headers": "sa2"})
		envelopes = table[0].find("td", {"headers": "sa5"})
		valid = table[0].find("td", {"headers": "sa6"})

		t2_470 = soup.select(".t2_470")
		valid_votes_list = []
		for content in t2_470:
			for tr in content.find_all("tr"):
				politics_name = tr.find("td", {"class": "overflow_name"})
				if politics_name == None:
					continue
				politics_name_list.append(politics_name.text)
				valid_votes = tr.find_all("td", {"class": "cislo"})
				valid_votes_list.append(valid_votes[1].text)
		for k in temp_data.keys():
			temp_data[k] = [registered.text, envelopes.text, valid.text, valid_votes_list]
		data.append(temp_data)
	data.append(politics_name_list)
	return data


def get_value(content):
	"""

	This function is part of the data_to_csv() function.

	"""
	v_list = []
	for v in content.values():
		v_list.append(v)
	return v_list


def data_to_csv(data: list, output_file: str, content: dict) -> None:
	"""

	This function writes all collected data to a csv file/output.
	
	"""
	politics_name = data.pop(-1)
	with open(output_file, "w", newline='', encoding="utf-8") as f:
		writer = csv.writer(f)
		header = ["code", "location", "registered", "envelopes", "valid"]
		writer.writerow(header + politics_name)
		system = 0
		for line in data:
			values = []
			code_list = get_value(content)
			values.append(code_list[system])
			city = str(line.keys()).replace("dict_keys(['", "")
			values.append(city.replace("'])", ""))
			for v in line.values():
				pol_votes = v.pop(-1)
				for vv in v: values.append(vv)
				for v in pol_votes: values.append(v)
			writer.writerow(values)
			system += 1


def main() -> None:
	"""

	This function combines all other functions into one.

	"""
	if len(sys.argv) != 3:
		print("Use: python main.py \"link\" output_file.csv")
		sys.exit()
	arg_url = sys.argv[1]
	output_file = sys.argv[2]
	if "https://volby.cz/pls/ps2017nss/ps3" in arg_url and ".csv" in output_file[-4:]:
		soup = webscrap(arg_url)
		content = get_url_zipcode(soup)
		data = get_data(content)
		data_to_csv(data, output_file, content)
		print(f"The data has been successfully saved to a csv file: {output_file}")
	else:
		print("Use: python main.py \"link\" output_file.csv")

if __name__ == "__main__":
	main()