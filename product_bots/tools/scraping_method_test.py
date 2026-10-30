"""
Scraping method test tool.

Standalone script, not part of the core product-db code. It runs a set
of scraping approaches (requests, curl_cffi, httpx, cloudscraper, Selenium,
Playwright, with and without stealth settings) against a single URL and prints
the HTTP status each one gets. Use it when adding a new source, to find the
simplest method that can reliably fetch its pages before writing a bot for it.

"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from playwright.sync_api import sync_playwright

import json

import requests
from curl_cffi import requests as curl_requests
import httpx
import cloudscraper

from selenium_stealth import stealth
from playwright_stealth import stealth_sync

test_url = input('Enter url:')

if not test_url:
    print("Defaulting to example.com...")
    test_url = "https://example.com/"

# service = Service("/opt/homebrew/bin/chromedriver")
# If browser and chromedriver version mismatch happens:
service = Service(ChromeDriverManager(driver_version="149.0.7827.156").install())

def result_handling(result, test_name):
    match result:
        case 200:
            print(f"{test_name}: ✅ 200")
        case _:
            print(f"{test_name}: ❌ {result}")

def short_error(e):
    ''' First line of the exception message, without Selenium's "Message: " prefix '''
    lines = str(e).strip().removeprefix("Message: ").splitlines()
    return lines[0] if lines else type(e).__name__

def request_test(url):
    ''' Testing if website can be scraped using requests '''
    test_name = "request"

    try:
        res = requests.get(url)
        result_handling(res.status_code, test_name)
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)

def curl_requests_test(url):
    ''' Testing if website can be scraped using curl_requests '''
    test_name = "curl_requests"

    try:
        res = curl_requests.get(url, impersonate="chrome")
        result_handling(res.status_code, test_name)
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)

def httpx_test(url):
    ''' Testing if website can be scraped using httpx '''
    test_name = "httpx"

    client = httpx.Client(
        http2=True,
        headers={
            "User-Agent": "PostmanRuntime/7.43.0",
            "Accept": "*/*"
        }
    )

    try:
        res = client.get(url)
        result_handling(res.status_code, test_name)
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)

def request_manual_stealth_test(url):
    ''' Testing if website can be scraped using requests with different settings '''
    test_name = "request-manual-stealth"

    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) "
    #                 "AppleWebKit/537.36 (KHTML, like Gecko) "
    #                 "Chrome/120.0.0.0 Safari/537.36",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    #     "Accept-Language": "en-US,en;q=0.9",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Connection": "keep-alive",
    #     "Upgrade-Insecure-Requests": "1",
    #     "Sec-Fetch-Dest": "document",
    #     "Sec-Fetch-Mode": "navigate",
    #     "Sec-Fetch-Site": "none",
    #     "Sec-Fetch-User": "?1",
    # }

    headers = {
        "Cache-Control": "no-cache",
        "User-Agent": "PostmanRuntime/7.53.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    with requests.Session() as session:
        session.headers.update(headers)
        try:
            res = session.get(url, headers=headers)
            result_handling(res.status_code, test_name)
        except Exception as e:
            result_handling(f"Something went wrong! {short_error(e)}", test_name)

def cloudscraper_test(url):
    ''' Testing if website can be scraped using cloudscraper '''
    test_name = "cloudscraper"

    scraper = cloudscraper.create_scraper(
        interpreter='js2py',
        # Stealth mode non-functional ATM
        # enable_stealth=True,
        # stealth_options={
        #     'min_delay': 2.0,
        #     'max_delay': 6.0,
        #     'human_like_delays': True,
        #     'randomize_headers': True,
        #     'browser_quirks': True
        # },
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        },
        debug=False
    )

    try:
        res = scraper.get(url)
        result_handling(res.status_code, test_name)
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)

def selenium_test(url):
    ''' Testing if website can be scraped using selenium '''
    test_name = "selenium"

    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)

        driver.execute_cdp_cmd("Network.enable", {})

        driver.get(url)

        # Read performance logs
        logs = driver.get_log("performance")
        for entry in logs:
            message = json.loads(entry["message"])
            msg = message["message"]

            if msg["method"] == "Network.responseReceived":
                response = msg["params"]["response"]
                if response["url"] == url:
                    result_handling(response["status"], test_name)
                    break
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)
    finally:
        if driver:
            driver.quit()

def selenium_headless_test(url):
    ''' Testing if website can be scraped using selenium in headless mode '''
    test_name = "selenium-headless"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)

        driver.execute_cdp_cmd("Network.enable", {})

        driver.get(url)

        # Read performance logs
        logs = driver.get_log("performance")
        for entry in logs:
            message = json.loads(entry["message"])
            msg = message["message"]

            if msg["method"] == "Network.responseReceived":
                response = msg["params"]["response"]
                if response["url"] == url:
                    result_handling(response["status"], test_name)
                    break
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)
    finally:
        if driver:
            driver.quit()

def selenium_manual_stealth_test(url):
    ''' Testing if website can be scraped using selenium in headless mode '''
    test_name = "selenium-manual-stealth"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    # options.add_argument("--disable-blink-features=AutomationControlled")  # hide automation
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-infobars")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("window-size=1280,800")  # realistic window size
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)

        driver.execute_cdp_cmd("Network.enable", {})

        driver.get(url)

        # Read performance logs
        logs = driver.get_log("performance")
        for entry in logs:
            message = json.loads(entry["message"])
            msg = message["message"]

            if msg["method"] == "Network.responseReceived":
                response = msg["params"]["response"]
                if response["url"] == url:
                    result_handling(response["status"], test_name)
                    break
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)
    finally:
        if driver:
            driver.quit()

def selenium_stealth_test(url):
    ''' Testing if website can be scraped using selenium in headless mode with stealth plugin '''
    test_name = "selenium-stealth"

    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)

        # --- Stealth patches ---
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        driver.get(url)

        # Read performance logs
        logs = driver.get_log("performance")
        for entry in logs:
            message = json.loads(entry["message"])
            msg = message["message"]

            if msg["method"] == "Network.responseReceived":
                response = msg["params"]["response"]
                if response["url"] == url:
                    result_handling(response["status"], test_name)
                    break
    except Exception as e:
        result_handling(f"Something went wrong! {short_error(e)}", test_name)
    finally:
        if driver:
            driver.quit()

def playwright_test(url):
    test_name = "playwright"

    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            response = page.goto(url)
            result_handling(response.status, test_name)
        except Exception as e:
            result_handling(f"Something went wrong! {short_error(e)}", test_name)
        finally:
            if browser:
                browser.close()

def playwright_headless_test(url):
    test_name = "playwright-headless"

    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            response = page.goto(url)
            result_handling(response.status, test_name)
        except Exception as e:
            result_handling(f"Something went wrong! {short_error(e)}", test_name)
        finally:
            if browser:
                browser.close()

def playwright_manual_stealth_test(url):
    test_name = "playwright-manual-stealth"

    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    # Additional settings
                    # ,viewport={"width": 1280, "height": 800},
                    # locale="en-US"
            )

            page = context.new_page()

            # Some navigator tricks
            # page.evaluate("""
            # () => {
            #     Object.defineProperty(navigator, 'webdriver', {get: () => false});
            #     window.navigator.chrome = {runtime: {}};
            #     Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            #     Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
            # }
            # """)

            response = page.goto(url)
            result_handling(response.status, test_name)
        except Exception as e:
            result_handling(f"Something went wrong! {short_error(e)}", test_name)
        finally:
            if browser:
                browser.close()

def playwright_stealth_test(url):
    test_name = "playwright-stealth"

    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            stealth_sync(page)

            response = page.goto(url)
            result_handling(response.status, test_name)
        except Exception as e:
            result_handling(f"Something went wrong! {short_error(e)}", test_name)
        finally:
            if browser:
                browser.close()

request_test(test_url)
curl_requests_test(test_url)
httpx_test(test_url)
request_manual_stealth_test(test_url)
cloudscraper_test(test_url)
selenium_test(test_url)
selenium_headless_test(test_url)
selenium_manual_stealth_test(test_url)
selenium_stealth_test(test_url)
playwright_test(test_url)
playwright_headless_test(test_url)
playwright_manual_stealth_test(test_url)
playwright_stealth_test(test_url)