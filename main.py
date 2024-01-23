from flask import Flask, request, send_file, jsonify
import requests
import re
from flask_cors import CORS
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup


def get_response(url):
  headers = {
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
  }
  try:
    r = requests.get(url, headers=headers, allow_redirects=True, verify=False)
    r.encoding = 'utf-8'
    return r
  except requests.exceptions.RequestException as e:
    print(f"{url} 请求发生异常: {e}", )
    return None


class LinkContainer:

  def __init__(self, url):
    self.url = url
    self.info = None
    self.response = get_response(url)
    self.get_info_from_html()

  def get_info_from_html(self):
    if self.response.history:
      # 发生了重定向
      print(f"Redirected to {self.response.url}")
      redirect_location = self.response.url
    else:
      redirect_location = ''
    soup = BeautifulSoup(self.response.content.decode("utf-8"), "html.parser")

    # 页面描述
    description = soup.find(attrs={"name": "description"})
    # 关键词
    keywords = soup.find(attrs={"name": "keywords"})
    # 版权声明
    copyright_text = soup.find(text=re.compile('©'))

    self.info = {
        "webTitle": soup.title.string if soup.title else '',
        "webStatus": f'{self.response.status_code}' if self.response else '',
        "webRedirectLocation": redirect_location,
        "webContent": description['content'] if description else '',
        "webKeywords": keywords['content'] if keywords else '',
        "webCopyright": copyright_text.strip() if copyright_text else ''
    }

    #print(self.info)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_ALLOW_ORIGINS'] = '*'
app.config['CORS_ALLOW_METHODS'] = ['GET', 'POST']
app.config['CORS_ALLOW_HEADERS'] = ['Content-Type', 'Authorization']


@app.route('/get_link_data', methods=['POST'])
def get_link_data():
  link_info = {}
  web_url = request.form.get('web_url')
  if not web_url:
    return jsonify({"error": "No URL provided"}), 400

  link_container = LinkContainer(web_url)
  link_info = link_container.info
  return jsonify({"status": 200, "info": link_info})


app.run(host='0.0.0.0', port=10081)