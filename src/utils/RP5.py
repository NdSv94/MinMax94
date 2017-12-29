from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
import time

driver = webdriver.Chrome()
driver.get("https://rp5.ru/%D0%90%D1%80%D1%85%D0%B8%D0%B2_%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B_%D0%B2_%D0%9C%D0%B0%D0%BB%D0%BE%D1%8F%D1%80%D0%BE%D1%81%D0%BB%D0%B0%D0%B2%D1%86%D0%B5")

action = action_chains.ActionChains(driver)

def load_data_from_wmo(wmo_id, start = '01.01.2012' ,end = '01.01.2017'):
    wmo_id_field = driver.find_element_by_id('wmo_id')
    wmo_id_field.clear()
    wmo_id_field.send_keys(str(wmo_id))
    time.sleep(1)

    action.send_keys(keys.Keys.ENTER)
    action.perform()

    download_archive_button = driver.find_element_by_id('tabSynopDLoad')
    download_archive_button.click()

    start_date_field = driver.find_element_by_id('calender_dload')
    start_date_field.clear()
    start_date_field.send_keys(start)

    action.send_keys(keys.Keys.ENTER)
    action.perform()

    end_date_field = driver.find_element_by_id('calender_dload2')
    end_date_field.clear()
    end_date_field.send_keys(end)

    driver.execute_script("document.getElementById('format2').click();")
    driver.execute_script("document.getElementById('coding2').click();")

    create_gz_button = driver.find_element_by_xpath("//div[@style=\"margin: 0 0 5px 19px;\"]")
    create_gz_button.click()

    time.sleep(2)
    download_archive_button = driver.find_element_by_id("f_result")
    download_archive_button.click()

