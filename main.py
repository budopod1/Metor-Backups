from flask import Flask, request
import os
import shutil
from requests import get
import json
app = Flask(__name__)

website = ""
my_site = ""
pages = []
censor = {}


def filter(content):
  try:
    content = content.decode("utf-8")
    if content.find("<!DOCTYPE html>") != 0:
      raise ValueError()
    if pages:
      injection = """
  <script>alert("hi");</script>
  """
    else:
      injection = ""
    content = content.replace("<head>", "<head>" + injection)
    for key, value in censor.items():
      content = content.replace(key, value)
    return content
  except (UnicodeDecodeError, ValueError):
    return content


def from_site():
  path = request.full_path.split("?")[0]
  response = get(f"https://{website}/{path}")
  path = path + "" if os.path.split(path)[1] else "/index"
  content = filter(response.content)
  so_far = "backup"
  for folder in os.path.split(path)[0].split("/")[1:]:
    so_far += f"/{folder}"
    if not os.path.exists(so_far):
      print(so_far)
      os.mkdir(so_far)
  with open(f"backup{path}", "wb" if isinstance(content, bytes) else "w") as file:
    file.write(content)
  return content


@app.route('/<path:path>')
def url(path):
  return from_site()


@app.route('/')
def home():
  return from_site()


def main():
  global censor, my_site, website, pages
  # Load config file
  with open("config.json") as file:
    data = json.loads(file.read())
  
  # Setup backup folder
  # shutil.rmtree("backup")
  # os.mkdir("backup")

  # Use config options
  my_site = data["this"]
  website = data["site"]
  pages = data["pages"]
  censor[website] = my_site

  # Start the webserver
  app.run(host='0.0.0.0', port=443)


if __name__ == "__main__":
  main()
