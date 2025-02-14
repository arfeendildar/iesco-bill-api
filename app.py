from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

def fetch_bill_details(reference_number):
    options = Options()
    options.add_argument('--headless')  # Run in headless mode (no UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get("https://bill.pitc.com.pk/iescobill")
    time.sleep(2)  # Wait for the page to load

    search_box = driver.find_element(By.ID, "searchTextBox")
    search_box.send_keys(reference_number)
    search_button = driver.find_element(By.ID, "btnSearch")
    search_button.click()
    time.sleep(5)  # Wait for the results to load

    units_consumed = driver.find_element(By.XPATH, "//td[b[text()='UNITS CONSUMED']]/following-sibling::td").text.strip()
    payable_amount = driver.find_element(By.XPATH, "//td[b[text()='PAYABLE WITHIN DUE DATE']]/following-sibling::td").text.strip()

    driver.quit()
    
    return {
        "units_consumed": units_consumed,
        "payable_amount": payable_amount
    }

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        reference_number = request.form.get('reference_number')
        if not reference_number:
            return render_template('index.html', error="Reference number is required")
        
        result = fetch_bill_details(reference_number)
        return render_template('index.html', result=result)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
