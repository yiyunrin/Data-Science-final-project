from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time
import urllib.parse
from flask import Flask, request, send_from_directory, jsonify
from threading import Thread

app = Flask(__name__)
results = []
searching = False

# set the home route
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# set the search route
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

# set the route for getting results
@app.route('/results')
def get_results():
    global results, searching
    if searching:
        return jsonify({"status": "Searching"})
    return jsonify({"results": results})

# crawl data from google maps
def search_google_maps(location):
    global results, searching
    driver_path = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_path)
    driver.maximize_window()

    try:
        # open google maps and search for the input location
        query = urllib.parse.quote(location)
        url = f"https://www.google.com/maps/search/{query}"
        driver.get(url)

        # confirm if the button has appeared
        buttons_exist = False
        check_time = 10 # confirm 10 times
        while check_time > 0:
            try:
                check_time -= 1
                first_button_xpath = '//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[1]/button'
                driver.find_element(By.XPATH, first_button_xpath)
                buttons_exist = True
                break
            except NoSuchElementException:
                print("No buttons found.")
                time.sleep(1)
        if not buttons_exist:
            print("No buttons found.")
            return
        
        # find "餐廳" botton
        restaurant_button = -1
        for i in range(1, 6):
            try:
                button_xpath = f'//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[{i}]/button'
                button = driver.find_element(By.XPATH, button_xpath)
                if "餐廳" in button.text:
                    button.click()
                    restaurant_button = i
                    break
            except NoSuchElementException:
                print(f"Button at index {i} not found.")
                break
            except Exception as e:
                print(f"Error finding button at index {i}: {e}")
                return
            
        # if "餐廳" button is found, click it
        if restaurant_button != -1:
            restaurant_xpath = f'//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[{restaurant_button}]/button'
            click_time = 10
            # try to click "餐廳" button
            while click_time > 0:
                try:
                    driver.find_element(By.XPATH, restaurant_xpath).click()
                    break
                except Exception as e:
                    print(f"restaurant button not found, retrying... ({click_time} attempts left)")
                    click_time -= 1
                    time.sleep(1)
        # else if "restaurant" button is not found
        else:
            # select the first location from the left-hand recommendations
            try:
                place_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[3]'
                driver.find_element(By.XPATH, place_xpath).click()
            except:
                print('place_xpath not found')
            # click the "附近" button
            click_time = 10
            near_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[4]/div[3]/button'
            while click_time > 0:
                try:
                    driver.find_element(By.XPATH, near_xpath).click()
                    break
                except Exception as e:
                    print(f"nearby button not found, retrying... ({click_time} attempts left)")
                    click_time -= 1
                    time.sleep(1)
            # click the "附近 restaurants" option
            click_time = 10
            restaurant_xpath = '//*[@id="ydp1wd-haAclf"]/div[1]'
            while click_time > 0:
                try:
                    driver.find_element(By.XPATH, restaurant_xpath).click()
                    break
                except Exception as e:
                    print(f"restaurant button not found, retrying... ({click_time} attempts left)")
                    click_time -= 1
                    time.sleep(1)
        time.sleep(1)

        # confirm if the button has appeared
        buttons_exist = False
        check_time = 10
        while check_time > 0:
            try:
                check_time -= 1
                first_button_xpath = '//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[1]/button'
                driver.find_element(By.XPATH, first_button_xpath)
                buttons_exist = True
                break
            except NoSuchElementException:
                print("No buttons found.")
                time.sleep(1)
        if not buttons_exist:
            print("No buttons found.")
            return

        # find the "營業時間" button
        open_button = -1
        for i in range(1, 6):
            try:
                button_xpath = f'//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[{i}]/button'
                button = driver.find_element(By.XPATH, button_xpath)
                if "營業時間" in button.text:
                    button.click()
                    restaurant_button = i
                    break
            except NoSuchElementException:
                print(f"Button at index {i} not found.")
                break
            except Exception as e:
                print(f"Error finding button at index {i}: {e}")
                return
        
        # if "營業時間" button is found, click it
        if open_button != -1:
            open_xpath = f'//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[{open_button}]/button'
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

        # click the "營業中" option
        open_select_xpath = '//*[@id="popup"]/div/div/div/div[1]/div/div/div[1]/div[1]/div[3]'
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

        # click the "套用" button
        ok_xpath = '//*[@id="popup"]/div/div/div/div[1]/div/div/div[2]/button[2]'
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

        # scroll the left panel 5 times
        scrollable_div_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        scrollable_div = driver.find_element(By.XPATH, scrollable_div_xpath)
        for _ in range(5):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)

        # crawl restaurant information
        info_divs = driver.find_elements(By.XPATH, '//div[contains(@class, "Nv2PK THOPZb CpccDe ")]')
        for div in info_divs[:20]:
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
