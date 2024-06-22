# 關於SightPath

<<<<<<<<< Temporary merge branch 1

# 環境
```
django == 4.2.1
python == 3.9.12
```  
快速建置環境
```
pip install -r requirements.txt
```

### 環境變數設定

建立 `.env` 檔案並加入下列變數
```bash
line_token=""
line_secret=""
DEV=""
```

### 運行專案

```bash
# Run DB migration
python3 manage.py makemigrations
python3 manage.py migrate

# Run server
python3 manage.py runserver
```
