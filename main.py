from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument("--window-size=1920x1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

main_url = "https://open.smk.dk/en/art?q=*&page=15&filters=has_3d_file%3Atrue"
driver.get(main_url)
time.sleep(3)

try:
    wait = WebDriverWait(driver, 10)
    allow_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Tillad alle']"))
    )
    ActionChains(driver).move_to_element(allow_button).perform()
    allow_button.click()
    print("Cookie popup dismissed successfully.")
except Exception as e:
    print("No cookie popup found or already dismissed.", e)

def scroll_to_bottom(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

scroll_to_bottom(driver)

artwork_links = [
    a.get_attribute("href")
    for a in driver.find_elements(By.TAG_NAME, "a")
    if a.get_attribute("href") and a.get_attribute("href").startswith("https://open.smk.dk/en/artwork/image/")
]

print(f"Found {len(artwork_links)} artwork image links.")

small_file = open("small.txt", "a", encoding="utf-8")
large_file = open("large.txt", "a", encoding="utf-8")

for art_link in artwork_links:
    driver.get(art_link)
    time.sleep(3)  
    download_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'https://api.smk.dk/api/v1/download-3d/')]")
    download_links = [elem.get_attribute("href") for elem in download_elements if elem.get_attribute("href")]

    for dl in download_links:
        if "small.stl" in dl:
            small_file.write(dl + "\n")
        else:
            large_file.write(dl + "\n")

    print(f"Processed artwork page: {art_link} ({len(download_links)} download link(s) found)")

small_file.close()
large_file.close()
driver.quit()

print("Finished processing all artwork pages.")
