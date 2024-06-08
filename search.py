from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
from flask import Flask, request, send_from_directory, jsonify
from threading import Thread

app = Flask(__name__)
results = []
searching = False

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/search')
def search():
    global results, searching
    location = request.args.get('location')
    if location:
        results = []
        searching = True
        thread = Thread(target=search_google_maps, args=(location,))
        thread.start()
        return jsonify({"status": "Searching for: " + location})
    return jsonify({"status": "No location provided."})

@app.route('/results')
def get_results():
    global results, searching
    if searching:
        return jsonify({"status": "Searching"})
    return jsonify({"results": results})

def search_google_maps(location):
    global results, searching
    driver_path = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_path)
    driver.maximize_window()

    try:
        query = urllib.parse.quote(location)
        url = f"https://www.google.com/maps/search/{query}"
        driver.get(url)

        
        restaurant_xpath = '//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[1]/button'
        click_time = 10
        while click_time > 0:
            try:
                driver.find_element(By.XPATH, restaurant_xpath).click()
                break
            except Exception as e:
                print(f"restaurant button not found, retrying... ({click_time} attempts left)")
                click_time -= 1
                time.sleep(1)

        time.sleep(1)

        open_xpath = '//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[3]/button'
        click_time = 10
        while click_time > 0:
            try:
                driver.find_element(By.XPATH, open_xpath).click()
                break
            except Exception as e:
                print(f"open button not found, retrying... ({click_time} attempts left)")
                click_time -= 1
                time.sleep(1)

        time.sleep(1)

        open_select_xpath = '//*[@id="ucc-4"]'
        click_time = 10
        while click_time > 0:
            try:
                driver.find_element(By.XPATH, open_select_xpath).click()
                break
            except Exception as e:
                print(f"open_select button not found, retrying... ({click_time} attempts left)")
                click_time -= 1
                time.sleep(1)

        time.sleep(1)

        ok_xpath = '//*[@id="ucc-8"]'
        click_time = 10
        while click_time > 0:
            try:
                driver.find_element(By.XPATH, ok_xpath).click()
                break
            except Exception as e:
                print(f"ok button not found, retrying... ({click_time} attempts left)")
                click_time -= 1
                time.sleep(1)

        time.sleep(1)

        scrollable_div_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        scrollable_div = driver.find_element(By.XPATH, scrollable_div_xpath)

        for _ in range(5):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)

        info_divs = driver.find_elements(By.XPATH, '//div[contains(@class, "Nv2PK THOPZb CpccDe ")]')
        
        for div in info_divs[:10]:
            try:
                # print(div.get_attribute('outerHTML'))  # Print the HTML code of the div
                name_div = div.find_element(By.XPATH, './/div[contains(@class, "qBF1Pd")]')
                results.append(name_div.text)
                print(name_div.text)
            except Exception as e:
                print(f"Error: {e}")
                continue
        print('info_divs len = ', len(info_divs))
    finally:
        driver.quit()
        searching = False

if __name__ == '__main__':
    app.run(port=8000)
