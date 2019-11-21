from selenium import webdriver
import traceback
import time

def main():
    try:
        chrome_option = webdriver.ChromeOptions()
        chrome_option.add_argument('--headless')
        chrome_option.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=chrome_option)
        
        driver.get("https://www.google.com/flights#flt=/m/022pfm.AJU.2018-12-26;c:BRL;e:1;sd:1;t:f;tt:o")
        time.sleep(5)
        
        date = driver.find_element_by_class_name("gws-flights-form__departure-input").text;
        rows = driver.find_elements_by_class_name("gws-flights-results__collapsed-itinerary");

        print 'Data: {0}'.format(date)

        for row in rows:
            price = int(filter(str.isdigit, row.find_element_by_class_name("gws-flights-results__price").text.encode('utf8')));
            hour = row.find_element_by_class_name("gws-flights-results__times").text.encode('utf8');
            carrier = row.find_element_by_class_name("gws-flights-results__carriers").text.encode('utf8').split('\n')[0];
            duration = row.find_element_by_class_name("gws-flights-results__duration").text.encode('utf8');
            airports = row.find_element_by_class_name("gws-flights-results__airports").text.encode('utf8');
            stops = row.find_element_by_class_name("gws-flights-results__stops").text.encode('utf8');

            print '----'
            print price
            print hour
            print carrier
            print duration
            print airports
            print stops

        # driver.save_screenshot('screenshot.png')
    except:
        print traceback.format_exc()
    finally:
        driver.quit()

if __name__ == '__main__':
    main()