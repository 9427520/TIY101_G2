import google.generativeai as genai
import os
import json
from io import BytesIO

current_script_path = os.path.abspath(__file__)
# 獲取當前腳本所在的目錄
current_script_dir = os.path.dirname(current_script_path)
json_file_path = os.path.join(current_script_dir, 'env.json')
# ENV Config file
with open(json_file_path, 'r') as f:
    env = json.load(f)
genai.configure(api_key=env["GOOGLE_API_KEY"])
# 列出可用模型
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)