import os
import requests
import sys 
from time import sleep 
import base64 
from datetime import datetime
import json

from scraper import scrape_page, scrape_all_links, image_downloader
from foxit import create_report, downloadResult, uploadDoc, imageToPDF, checkTask, combinePDF


base_url = "https://na1.fusion.foxit.com"
HOST = base_url
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
CLIENT_ID = client_id
CLIENT_SECRET = client_secret



sample_links = [
    "https://www.redfin.com/CA/Livermore/La-Vina-Apartments/apartment/177431043",
    "https://www.redfin.com/CA/Livermore/702-Hayes-Ave-94550/home/192999784",
    "https://www.redfin.com/CA/Livermore/3550-Pacific-Ave-94550/home/2003204",
    "https://www.redfin.com/CA/Livermore/Ironwood/apartment/177387889",
    "https://www.redfin.com/CA/Livermore/211-Maple-St-94550/home/1552965"
]

properties, images = scrape_all_links(sample_links)
create_report(properties, images, client_id, client_secret)