from urllib.parse import unquote

url = input("輸入url: ")
print(unquote(url, encoding="utf-8"))