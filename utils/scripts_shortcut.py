import subprocess
import sys

# 注意: 此程式用途為簡化需在terminal重複輸入的指令

def get_device() -> str:
    while True:
        device = input("請輸入裝置型別:\n(1 win\n(2 linux\n: ")
        if device in ["1", "2"]:
            return device
        else:
            print("錯誤指令，請輸入1或2")
            


def load_fixtures_script(device: str):
    if device == "1":
        py_script = "python"
    else:
        py_script = "python3"
        
    fixtures_root = "./base/fixtures/"
    fixtures_dict = {
        "activities_tags": fixtures_root+"activities_tags_fixture.json",
        "activities": fixtures_root+"activities_fixture.json",
        
        "competition_tags": fixtures_root+"competition_tags_fixture.json",
        "competitions": fixtures_root+"competitions_fixture.json",
        
        "ourtag": fixtures_root+"ourtag_fixture.json",
    }
    for script_name, fixture_path in fixtures_dict.items():
        print(f"正在將{script_name}加載進資料庫...")
        # print([py_script, "manage.py", "loaddata", fixture_path])
        subprocess.run([py_script, "manage.py", "loaddata", fixture_path])


def web_scraping_script(device):
    if device == "1":
        py_script = "python"
    else:
        py_script = "python3"
    
    fixtures_root = "./base/fixtures/"
    web_scraping_dict = {
        "competitions": fixtures_root+"competitions_fixture_generator.py",
        "activities": fixtures_root+"activities_fixture_generator.py",
    }
    while True:
        scrape_data = input("要爬取的資料是:\n(1 competitions\n(2 activities\n(3 all\n: ")
        if scrape_data in ["1", "competitions"]:
            del web_scraping_dict["activities"]
            break
            
        elif scrape_data in ["2", "activities"]:
            del web_scraping_dict["competitions"]
            break
            
        elif scrape_data in ["3", "all"]:
            break
        
        else:
            print("指令錯誤")
        
    for script_name, scraping_path in web_scraping_dict.items():
        print(f"正在爬取{script_name}的資料...")
        subprocess.run([py_script, scraping_path])


def quick_deployment():    
    subprocess.run("sudo pkill -f runserver")
    print("已執行 sudo pkill -f runserver")
    
    subprocess.run("git pull --force --rebase")
    print("已執行 git pull --force --rebase")
    
    subprocess.run("python3 .\manage.py migrate")
    print("已執行 python3 .\manage.py migrate")
    
    subprocess.run("sudo nohup python3 manage.py runserver 0.0.0.0:80 --insecure")
    print("已執行 sudo nohup python3 manage.py runserver 0.0.0.0:80 --insecure")


def main(input_args):
    if len(input_args) > 1:
        if "scrape" in input_args:
            web_scraping_script(get_device())
        if "loaddata" in input_args:
            load_fixtures_script(get_device())
        if "asap" in input_args:
            quick_deployment()
    else:
        print("未指定指令")

        
if __name__ == "__main__":
    main(sys.argv)