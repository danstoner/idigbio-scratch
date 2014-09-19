import requests
from requests.auth import HTTPBasicAuth
import os 
import sys

def main():
	s = requests.Session()
	goodurl = "http://httpbin.org/status/200"
	badurl = "http://httpbin.org/status/404"
	r = s.get(goodurl)
	r.raise_for_status()
	print goodurl,r.status_code
	r = s.get(badurl)
	r.raise_for_status()
	print badurl,r.status_code


if __name__ == '__main__':
	main()
