from selenium import webdriver
import traceback
import time
import re

def main():
    try:
        chrome_option = webdriver.ChromeOptions()
        chrome_option.add_argument('--headless')
        chrome_option.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_option)
        
        driver.get("https://www.google.com/flights?hl=en#flt=/m/06gmr.CAI.2020-02-21*CAI./m/06gmr.2020-02-25;c:BRL;e:1;sd:1;t:f")
        time.sleep(3)
        
        date = driver.find_element_by_class_name("gws-flights-form__departure-input").text
        rows = driver.find_elements_by_class_name("gws-flights-results__collapsed-itinerary")

        print('Data: {0}'.format(date))

        for row in rows:
            price = int(re.sub(r'[^0-9]', r'', row.find_element_by_class_name("gws-flights-results__price").text))
            hour = row.find_element_by_class_name("gws-flights-results__times").text
            carrier = row.find_element_by_class_name("gws-flights-results__carriers").text.split('\n')[0]
            duration = row.find_element_by_class_name("gws-flights-results__duration").text
            airports = row.find_element_by_class_name("gws-flights-results__airports").text
            stops = row.find_element_by_class_name("gws-flights-results__stops").text

            print('----')
            print(price)
            print(hour)
            print(carrier)
            print(duration)
            print(airports)
            print(stops)

        # driver.save_screenshot('screenshot.png')
    except:
        print(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == '__main__':
    main()