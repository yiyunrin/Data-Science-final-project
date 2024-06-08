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
        time.sleep(3)

        # Select restaurant button
        restaurant_xpath = '//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[2]/div[2]/div[1]/button'
        driver.find_element(By.XPATH, restaurant_xpath).click()
        time.sleep(5)

        # Grab the restaurant info divs
        info_divs = driver.find_elements(By.XPATH, '//div[contains(@class, "Nv2PK THOPZb CpccDe ")]')
        
        # Extract text from inner divs and print HTML
        for div in info_divs[:10]:  # Process the first 10 results
            try:
                print(div.get_attribute('outerHTML'))  # Print the HTML code of the div
                name_div = div.find_element(By.XPATH, './/div[contains(@class, "qBF1Pd")]')
                results.append(name_div.text)
            except Exception as e:
                # If there is no such element or any other error, print the exception and skip this div
                print(f"Error: {e}")
                continue
    finally:
        driver.quit()
        searching = False

if __name__ == '__main__':
    app.run(port=8000)
