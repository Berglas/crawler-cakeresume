# 載入需要的套件
from selenium import webdriver
from selenium.webdriver.common.by import By
import json, threading, queue

class WebDriver():

    def setUp(self, amount):
        print('[INFO] Set up web driver.')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=1920,1080")
        driver_list = []
        for i in range(amount):
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            driver_list.append(driver)
        return driver_list

class ResumeDownloadProcess():
    url_queue = queue.Queue()
    result_data = []

    def get_resume_url_put_queue(self, driver):
        print('[INFO] Call function get_all_resume_url.')
        current_page = 1
        last_page = current_page + 1

        while (current_page <= 2):
            url = f'https://www.cakeresume.com/工程-resume-samples/?page={current_page}'
            driver.get(url)

            if current_page == 1:
                ### 抓取最後頁數
                pagination =driver.find_element(by=By.CLASS_NAME, value='pagination')
                pages = pagination.find_elements(by=By.TAG_NAME, value='a')
                last_page = int(pages[len(pages) - 2].text)
            print(f'[INFO] Process Page{current_page}')

            elements = driver.find_elements(by=By.CLASS_NAME, value='item-user')
            for e in elements:
                a = e.find_element(by=By.TAG_NAME, value='a')
                self.url_queue.put(a.get_attribute('href'))
            current_page += 1

    def get_resume_data_handler(self, thread_no, driver):
        while True:
            try:
                url = self.url_queue.get()
                print(f'[INFO] Thread[{thread_no}] accept one task, Remain task {self.url_queue.qsize()}.')

                driver.get(url)
                tag_name_list = ['b', 'i', 'p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5']
                content = ''
                for tag in tag_name_list:
                    items = driver.find_elements(by=By.TAG_NAME, value=tag)
                    for i in items:
                        content += '_' + i.text
                obj = {
                    'url': url,
                    'content': content
                }
                self.result_data.append(obj)
            except:
                print('[WARING] get_resume_data_handler happened error.')
            finally:
                self.url_queue.task_done()

print('=== START ===')
try:
    web_driver = WebDriver()
    driver_list = web_driver.setUp(10) # 設置 WebDriver 初始化，數量為十個

    process = ResumeDownloadProcess()
    process.get_resume_url_put_queue(driver_list[0]) # 獲取履歷網址且放置 queue 中
    print(f'[INFO] Get {process.url_queue.qsize()} task.')
    # threading.Thread(target=process.get_resume_data_handler, args=(0, driver_list[0]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(1, driver_list[1]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(2, driver_list[2]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(3, driver_list[3]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(4, driver_list[4]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(5, driver_list[5]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(6, driver_list[6]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(7, driver_list[7]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(8, driver_list[8]), daemon=True).start()
    # threading.Thread(target=process.get_resume_data_handler, args=(9, driver_list[9]), daemon=True).start()

    for index, driver in enumerate(driver_list):
        print(index, driver)
        threading.Thread(target=process.get_resume_data_handler, args=(index, driver), daemon=True).start()
    process.url_queue.join() # 等待 queue 消耗完畢

    print('[INFO] Writing file.')
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(process.result_data, f, ensure_ascii=False, indent=4)

except Exception as err:
    print(f'[ERROR] {err}')

print('=== END ===')
