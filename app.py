import os
import time
import subprocess
from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def install_chrome():
    """ Install Chrome & Chromedriver for cloud environments like Render """
    os.system("apt update")
    os.system("apt install -y wget unzip")
    os.system("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
    os.system("apt install -y ./google-chrome-stable_current_amd64.deb")
    os.system("rm google-chrome-stable_current_amd64.deb")

def fetch_bill_details(reference_number):
    options = Options()
    options.add_argument('--headless')  # Run in headless mode (no UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/google-chrome"  # Explicitly set Chrome path
    
    try:
        service = Service(ChromeDriverManager().install())  # Auto-install Chromedriver
        driver = webdriver.Chrome(service=service, options=options)

        driver.get("https://bill.pitc.com.pk/iescobill")
        time.sleep(2)  # Wait for the page to load

        search_box = driver.find_element(By.ID, "searchTextBox")
        search_box.send_keys(reference_number)
        search_button = driver.find_element(By.ID, "btnSearch")
        search_button.click()
        time.sleep(5)  # Wait for results to load

        units_consumed = driver.find_element(By.XPATH, "//td[b[text()='UNITS CONSUMED']]/following-sibling::td").text.strip()
        payable_amount = driver.find_element(By.XPATH, "//td[b[text()='PAYABLE WITHIN DUE DATE']]/following-sibling::td").text.strip()

        driver.quit()

        return {"units_consumed": units_consumed, "payable_amount": payable_amount}

    except Exception as e:
        return {"error": str(e)}

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
    install_chrome()  # Install Chrome at startup
    app.run(debug=True)
