import locale
import requests
import smtplib, ssl
from re import sub
from bs4 import BeautifulSoup

## -----------------------------------------------------------------------------
## Future Work :
## Read from file with multiple URLs and max prices (compare with current price)
## and inform the user if some of the prices dropped below the max price.
## -----------------------------------------------------------------------------

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53"
}

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# send email to inform user for price drop
def send_email(url, title, price) :
    port = 587 # 465 for SSL, 587 for starttls
    # sender = input("Please enter your email: ")
    sender = "foo123@gmail.com"
    # Application password for Windows machine : fhwxorqlkqnnhvqq
    # password = input("Please enter your application password for Windows machine: ")
    password = "fhwxorqlkqnnhvqq"

    # Create a secure SSL context
    context = ssl.create_default_context()
    try :
        server = smtplib.SMTP('smtp.gmail.com', port)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(sender, password)

        subject = title + " at " + price
        body = "You can find the product here:\n" + url
        msg = ("Subject: " + subject + "\n\n" + body).encode('utf-8')

        receiver = "foo123@gmail.com"
        server.sendmail(sender, receiver, msg)
        print("\033[1mEmail has been sent to:", receiver, ".\033[0m")

    except Exception as err:
        print("\033[1mAn error occurred:\033[0m", str(err).capitalize())

    finally:
        server.quit()

print("\n\033[96mAmazon.de Web Scraper\033[0m\n")
while(1) :
    URL = input("Please type the URL of product page you want to scrap: ")
    URL = URL.strip()

    if not URL :
        print("\n\033[1mWarning:\033[0m The URL should not be empty!")
        continue
        ## Testing URLs
        # URL = "https://www.amazon.de/-/en/Apple-MacBook-16GB-512GB-memory/dp/B081FW6TPQ/ref=sr_1_5?dchild=1&keywords=macbook+pro&qid=1611944506&sr=8-5"
        # URL = "https://www.amazon.de/-/en/HUAWEI-Watch-Pro-Classic-Smartwatch-Night-black/dp/B08GPN5DM6?ref_=Oct_DLandingS_D_9f6a8f5d_60&smid=A3JWKAKR8XB7XF"
        # URL = "https://www.amazon.de/teapot-warmer-strainer-insert-stainless/dp/B07G6V4ZF9/ref=sr_1_2_sspa?dchild=1&keywords=Teekanne&qid=1612007488&sr=8-2-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUExRTBZUzNEOVpJN0NRJmVuY3J5cHRlZElkPUEwNDYyOTkwMUtNRDVYUFBQRzJUNSZlbmNyeXB0ZWRBZElkPUEwMDc3MjI3MkFDWEpKV0VDNVhOQyZ3aWRnZXROYW1lPXNwX2F0ZiZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU="

    try :
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

    except :
        print("\n\033[1mError:\033[0m The URL entered may not be valid!")
        continue

    else :
        break

title_soup = soup.find(id="productTitle")
price_soup = soup.find(id="price_inside_buybox")
# image_soup = soup.find(id="landingImage")

if title_soup and price_soup :
    product_title = title_soup.get_text().strip()
    price_value = price_soup.get_text().strip()
    # image_value = price_soup.get_src().strip()
    print("\n\033[1mPoduct Name:\033[0m", product_title, "\n\033[1mCurrent Price:\033[0m", price_value, "\n")
    # print("Image src:", image_soup['data-old-hires'].strip())

    conv = locale.localeconv()
    raw_numbers = price_value.strip(conv['currency_symbol'])
    raw_numbers = raw_numbers.strip()

    price_split = raw_numbers.split(',')
    cnt = 0
    # print("Array:", price_split, "\n")

    # Convert 39,99 to 39.99 (Warning: Amazon scraping lacks consistency)
    for li in price_split :
        if cnt > 0 and len(li) == 2 :
            price_split[cnt] = "." + price_split[cnt]
        cnt = cnt + 1

    converted_price = ''.join(price_split)
    # print("Converted price:", converted_price)

    while(1) :
        max_price = input("Notify me if price drops under (price): ")

        if not max_price :
            print("\n\033[1mWarning:\033[0m Max price should not be empty!")
            continue

        if max_price.isnumeric() :
            break
        else :
            print("\n\033[1mError:\033[0m Max price may not be valid!")
            continue

    try :
        product_price = locale.atof(converted_price)
        product_max_price = locale.atof(max_price)
        # print("Product price:", product_price)
        # print("Product max price:", product_max_price)

        if product_price < product_max_price :
            print("\n\033[1mInfo:\033[0m Product price dropped under max price.")
            send_email(URL, product_title, price_value)
        else :
            print("\n\033[1mInfo:\033[0m Product price is still higher than max price.")

    except Exception as err :
        print("\n\033[1mUnexpected error occurred:\033[0m", str(err).capitalize())

else :
    print("\n\033[1mError:\033[0m Page may not allow scraping or there was an error with DOM element ids!")