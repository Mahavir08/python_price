import os
import ssl
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

options = Options()
options.add_argument("--headless=new") 
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

what_we_have = float(os.environ["COIN"] or 0.00691840)

sites = [
    {
        "name":"Zebpay",
        "URL":"https://zebpay.com/exchange/BTC-INR",
        "selector":".css-qkkbbk",
        "multiply":what_we_have,
        "timeout":15,
        "array":0
    },
    {
        "name":"Macbook M4 Air Vijay Sales",
        "URL":"https://www.vijaysales.com/p/P238593/238593/apple-macbook-air-m4-chip-13-inch-34-46-cm-13-6-16gb-256gb-midnight-mw123hn-a?gad_campaignid=17952322759",
        "selector":".product__price--price",
        "multiply":1,
        "timeout":15,
        "array":1
    },
    {
        "name":"ASUS Prime RTX 5060 OC 8GB",
        "URL":"https://mdcomputers.in/product/asus-prime-graphics-card-rtx5060-o8g/graphics-card/nvidia/rtx-50-graphics-card",
        "selector":".special-price",
        "multiply":1,
        "timeout":15,
        "array":0
    },
    {
        "name":"Macbook M4 Air Reliance",
        "URL":"https://www.reliancedigital.in/product/apple-mc6t4hna-macbook-air-apple-m4-chip16-gb256-gb-ssdmacos-sequoialiquid-retina-3446-cm-136-inch-sky-blue-m7x7uv-8968953",
        "selector":".product-price",
        "multiply":1,
        "timeout":15,
        "array":0
    }
]


def send_email(html_body):
    try:
        SMTP_HOST = os.environ["SMTP_HOST"]
        SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
        SMTP_USER = os.environ["SMTP_USER"]
        SMTP_PASS = os.environ["SMTP_PASS"]
        EMAIL_TO = os.environ["EMAIL_TO"]

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = EMAIL_TO
        msg["Subject"] = f"Price: {current_time}"
        msg.set_content("Your email client does not support HTML.")
        msg.add_alternative(html_body, subtype="html")

        context = ssl.create_default_context()

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls(context=context)
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)        
        print("Mail Send Successfully!")
    except:
        print("Error while mailing")


def check_price():
    # email_body = ""
    html_body = """
            <html>
            <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f7fa;
                    color: #333;
                    padding: 20px;
                    text-align: left;  
                }
                .container {
                    max-width: 650px;
                    margin: auto;
                    background: #fff;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 18px rgba(0,0,0,0.1);
                    text-align: left;
                    margin: 0 !important;                 /* <-- KEY FIX */
                    text-align: left !important;          /* ensure Gmail respects it */
                }
                .title {
                    text-align: left;
                    font-size: 26px;
                    font-weight: bold;
                    color: #1a73e8;
                    margin-bottom: 20px;
                }
                .site-card {
                    background: #fafafa;
                    border-left: 5px solid #1a73e8;
                    padding: 15px 20px;
                    margin-bottom: 18px;
                    border-radius: 8px;
                    text-align: left;
                }
                .site-name {
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 8px;
                    text-align: left;
                }
                .price {
                    font-size: 16px;
                    margin-bottom: 3px;
                    color: #222;
                    text-align: left;
                }
                .final-price {
                    font-size: 17px;
                    font-weight: bold;
                    color: #0a7b34;
                    text-align: left;
                }
                .not-found {
                    font-size: 16px;
                    color: #c62828;
                    font-weight: bold;
                    text-align: left;
                }
            </style>
            </head>
            <body>
            <div class="container">
                <div class="title">Price Update</div>
            """

    for each_site in sites :
        try:
            driver.get(each_site["URL"])
            wait = WebDriverWait(driver, 15)
            el = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, each_site["selector"])))
            el = el[each_site["array"]]
            number_str = "".join(ch for ch in el.text if ch.isdigit())
            number = int(number_str)
            print("--------------------",each_site["name"],"-----------------------")
            print("Price:", el.text)
            final_price = (number * each_site["multiply"]/100) if "zebpay" in each_site["name"].lower() else (number * each_site["multiply"])
            print("Final Price", final_price)
            html_body += f"""
                <div class="site-card">
                <div class="site-name">{each_site['name']}</div>
                <div class="price">Price: {el.text}</div>
                <div class="final-price">Final Price: {final_price}</div>
                </div>
            """
            # email_body += f"-------------------- {each_site['name']} --------------------\n"
            # email_body += f"Price: {el.text}\n"
            # email_body += f"Final Price: {final_price}\n\n"
        except:
            html_body += f"""
                <div class="site-card">
                    <div class="site-name">{each_site['name']}</div>
                    <div class="not-found">Element not found</div>
                </div>
            """
            # email_body += f"-------------------- {each_site['name']} --------------------\n"
            # email_body += "Element not found\n\n"
            print("Element not found")
    send_email(html_body)
    driver.quit()
    return ("OK", 200)

def main():
    result = check_price()
    if not result:
        print("No results to send")
        return


if __name__ == "__main__":
    main()