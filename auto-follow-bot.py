from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import httpx
import datetime

# ====== LOGIN INFO ======
USERNAME = "testautomate2025"
PASSWORD = "test_cosc"
USERNAME_TO_SEARCH = "cbitosc"  # 🔁 Change this to scrape another profile

# ====== SETUP SELENIUM DRIVER ======
options = Options()
options.add_argument("--start-maximized")
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# ====== LOGIN TO INSTAGRAM ======
driver.get("https://www.instagram.com/accounts/login/")
WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username")))
driver.find_element(By.NAME, "username").send_keys(USERNAME)
driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)

# ====== SEARCH FOR PROFILE ======
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Search']")))
time.sleep(3)
driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Search']").click()
time.sleep(2)

search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search input']"))
)
search_input.clear()
search_input.send_keys(USERNAME_TO_SEARCH)
time.sleep(3)

driver.execute_script(f"""
    const suggestion = document.querySelector("a[href^='/{USERNAME_TO_SEARCH}']");
    if (suggestion) suggestion.click();
""")
time.sleep(5)

WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//header")))
time.sleep(2)

# ====== FOLLOW LOGIC ======
try:
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//header//button")))
    buttons = driver.find_elements(By.XPATH, "//header//button")

    followed = False
    for btn in buttons:
        text = btn.text.strip().lower()
        if text in ["follow", "follow back", "requested"]:
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            btn.click()
            print(f"✅ Clicked: {text.title()} button")
            followed = True
            time.sleep(2)
            break

    if not followed:
        driver.execute_script("""
            let btns = [...document.querySelectorAll('header button')];
            for (let b of btns) {
                let txt = b.innerText.toLowerCase();
                if (txt.includes('follow') || txt.includes('follow back') || txt.includes('requested')) {
                    b.scrollIntoView();
                    b.click();
                    break;
                }
            }
        """)
        print("✅ JS fallback used to click Follow button")

except Exception as e:
    print("❌ Failed to click Follow button:", e)

# ====== FETCH PROFILE INFO VIA API ======
def fetch_profile(username):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-ig-app-id": "936619743392459"
    }
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        user = response.json()["data"]["user"]
        return {
            "Name": user.get("full_name") or username,
            "Username": user["username"],
            "Posts": user["edge_owner_to_timeline_media"]["count"],
            "Followers": user["edge_followed_by"]["count"],
            "Following": user["edge_follow"]["count"],
            "Bio": user.get("biography", ""),
            "External URL": user.get("external_url", "None")
        }
    except Exception as e:
        print("❌ Failed to fetch profile info:", e)
        return {
            "Name": "N/A",
            "Username": username,
            "Posts": "N/A",
            "Followers": "N/A",
            "Following": "N/A",
            "Bio": "N/A",
            "External URL": "N/A"
        }

# ====== SAVE TO FILE ======
def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Fetched: {datetime.datetime.now()}\n")
        for key, value in data.items():
            f.write(f"{key}: {value}\n")

# ====== MAIN ======
if __name__ == "__main__":
    info = fetch_profile(USERNAME_TO_SEARCH)
    save_to_file(info, f"{USERNAME_TO_SEARCH}_info.txt")
    print(f"✅ Data saved to {USERNAME_TO_SEARCH}_info.txt")

# ====== CLOSE BROWSER ======
driver.quit()
print(f"✅ Done. Profile visited and data extracted.")
