from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import subprocess

app = Flask(__name__)

# Install Google Chrome manually
CHROME_PATH = "/usr/bin/google-chrome"

if not os.path.exists(CHROME_PATH):
    subprocess.run([
        "apt-get", "update"
    ], check=True)

    subprocess.run([
        "apt-get", "install", "-y", "google-chrome-stable"
    ], check=True)

def fetch_bill_details(reference_number):
    try:
        options = Options()
        options.add_argument("--headless")  # Run in headless mode (no GUI)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.binary_location = CHROME_PATH  # Set Chrome binary location

        # Use WebDriver Manager to install ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get("https://bill.pitc.com.pk/iescobill")
        time.sleep(3)  # Wait for the page to load

        search_box = driver.find_element(By.ID, "searchTextBox")
        search_box.send_keys(reference_number)
        search_button = driver.find_element(By.ID, "btnSearch")
        search_button.click()
        time.sleep(5)  # Wait for the results to load

        # Fetch required details
        try:
            units_consumed = driver.find_element(By.XPATH, "//td[b[text()='UNITS CONSUMED']]/following-sibling::td").text.strip()
        except Exception:
            units_consumed = "Not Found"

        try:
            payable_amount = driver.find_element(By.XPATH, "//td[b[text()='PAYABLE WITHIN DUE DATE']]/following-sibling::td").text.strip()
        except Exception:
            payable_amount = "Not Found"

        driver.quit()

        return {
            "units_consumed": units_consumed,
            "payable_amount": payable_amount
        }

    except Exception as e:
        return {"error": str(e)}

@app.route('/get_bill', methods=['GET'])
def get_bill():
    reference_number = request.args.get('reference_number')
    if not reference_number:
        return jsonify({"error": "Reference number is required"}), 400

    result = fetch_bill_details(reference_number)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
