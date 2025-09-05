import os
import requests
import sys 
from time import sleep 
import base64 
from datetime import datetime
import json
from scraper import image_downloader
import http.client

base_url = "https://na1.fusion.foxit.com"
HOST = base_url

def uploadDoc(path, id, secret):
	
	headers = {
		"client_id":id,
		"client_secret":secret
	}

	with open(path, 'rb') as f:
		files = {'file': f}

		request = requests.post(f"{HOST}/pdf-services/api/documents/upload", files=files, headers=headers)
		return request.json()

def imageToPDF(doc, id, secret):
	
	headers = {
		"client_id":id,
		"client_secret":secret,
		"Content-Type":"application/json"
	}

	body = {
		"documentId":doc	
	}

	request = requests.post(f"{HOST}/pdf-services/api/documents/create/pdf-from-image", json=body, headers=headers)
	return request.json()

def checkTask(task, id, secret):

	headers = {
		"client_id":id,
		"client_secret":secret,
		"Content-Type":"application/json"
	}

	done = False
	while done is False:

		request = requests.get(f"{HOST}/pdf-services/api/tasks/{task}", headers=headers)
		status = request.json()
		if status["status"] == "COMPLETED":
			done = True
			# really only need resultDocumentId, will address later
			return status
		elif status["status"] == "FAILED":
			print("Failure. Here is the last status:")
			print(status)
			sys.exit()
		else:
			print(f"Current status, {status['status']}, percentage: {status['progress']}")
			sleep(5)

def combinePDF(docs, id, secret, level="MEDIUM"):
	
	headers = {
		"client_id":id,
		"client_secret":secret,
		"Content-Type":"application/json"
	}

	body = {
		"documentInfos": docs
	}

	request = requests.post(f"{HOST}/pdf-services/api/documents/enhance/pdf-combine", json=body, headers=headers)
	return request.json()

def downloadResult(doc, path, id, secret):
	
	headers = {
		"client_id":id,
		"client_secret":secret
	}

	with open(path, "wb") as output:
		
		bits = requests.get(f"{HOST}/pdf-services/api/documents/{doc}/download", stream=True, headers=headers).content 
		output.write(bits)


def download_and_append_image(url, client_id, client_secret):
	base_report = uploadDoc("./temp_report.pdf", client_id, client_secret)
	image_downloader(url)
	doc = uploadDoc("./temp.jpg", client_id, client_secret)
	task = imageToPDF(doc["documentId"], client_id, client_secret)
	print(f"Uploading Image, id is {task['taskId']}")
	result = checkTask(task["taskId"], client_id, client_secret)
	print(f"Image Uploaded: {result}")
	downloadResult(result["resultDocumentId"], "./tempimage.pdf", client_id, client_secret)
	imgdoc = uploadDoc("./tempimage.pdf", client_id, client_secret)
	task = combinePDF([base_report, imgdoc], client_id, client_secret)
	print(f"Adding Image to PDF, id is {task['taskId']}")
	result = checkTask(task["taskId"], client_id, client_secret)
	print(f"Image Added to PDF: {result}")
	downloadResult(result["resultDocumentId"], "./temp_report.pdf", client_id, client_secret)

def create_report(properties, images, client_id, client_secret):
	template_filepath = "./template.docx"
	with open(template_filepath, 'rb') as file:
		bd = file.read()
		b64 = base64.b64encode(bd).decode('utf-8')   

	data = {"properties":properties}	
 
	payload = {
	    "outputFormat":"pdf",
		"documentValues":data,
		"base64FileString":b64
    }

	body = json.dumps(payload)

	headers = {
		"client_id":client_id,
		"client_secret":client_secret
	}

	conn = http.client.HTTPSConnection("na1.fusion.foxit.com")
	conn.request("POST", "/document-generation/api/GenerateDocumentBase64", body, headers)

	resp = conn.getresponse()
	reader = resp.read()

	parsed = json.loads(reader)
	b64_str = parsed["base64FileString"]

	binary_data = base64.b64decode(b64_str)

	with open("temp_report.pdf", "wb") as f:
		f.write(binary_data)

	for image in images:
		try:
			download_and_append_image(image, client_id, client_secret)
		except Exception as e:
			print(f"Error occurred while adding images to the PDF: {e}")

	os.rename("./temp_report.pdf", "./final_report.pdf")