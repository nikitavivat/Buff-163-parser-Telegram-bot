import os
import re
from math import ceil

import requests
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from solver import PuzzleSolver

from aiogram.types import BufferedInputFile


# Функция входа в аккаунт Buff
# Buff account login function
def buff_login(driver, phone_number):
    # Загрузка страницы buff.163.com
    # Loading page buff.163.com
    driver.get("https://buff.163.com/")
    time.sleep(5)

    # Поиск кнопки Входа в аккаунт
    # Search for the Login button
    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Войти/Зарегистрироваться')]"))
    )

    # Проверка доступности кнопки для нажатия
    # Checking whether a button is clickable
    if login_button.is_displayed():
        login_button.click()
        # Пауза для загрузки окна входа
        # Pause to load the login window
        time.sleep(15)

        # Переключение Driver на Frame входа
        # Switch driver to Login Frame
        iframe = driver.find_elements(By.TAG_NAME, 'iframe')[0]
        driver.switch_to.frame(iframe)

        # Поиск окна ввода номера телефона и ввод
        # Search for the phone number entry window and enter
        label_text = "Введите номер телефона"
        input_field = driver.find_element(By.XPATH, f'//label[text()="{label_text}"]/following-sibling::input')
        input_field.send_keys(phone_number)

        # Выбор кода страны Ru / +7
        # Select country code Ru / +7
        trigger_element = driver.find_element(By.ID, "mobile-itl-div")
        trigger_element.click()
        element = driver.find_element(By.XPATH, "//a[@data-code='+7-']")
        element.click()

        # Нажатие на кнопку пользовательского соглашения
        # Clicking on the user agreement button
        checkbox = driver.find_element(By.CLASS_NAME, "zc-un-login")
        checkbox.click()

        try:
            # Нажатие на кнопку отправки SMS
            # Click on the send SMS button
            send_sms = driver.find_element(By.XPATH, '//a[@class="j-power-btn tabfocus getsmscode "]')
            send_sms.click()

            # Ожидание загрузки Captcha
            # Waiting for Captcha to load
            time.sleep(10)

            # Поиск фонового изображение у Captcha и пазла
            # Search for background image in Captcha and puzzle
            img_element_background = driver.find_element(By.CLASS_NAME, 'yidun_bg-img')
            img_url_background = img_element_background.get_attribute('src')
            img_element_puzzle = driver.find_element(By.CLASS_NAME, 'yidun_jigsaw')
            img_url_puzzle = img_element_puzzle.get_attribute('src')

            # Генерация папки, если ее не существует, для элементов Captcha
            # Generate a folder if it does not exist for Captcha elements
            folder_name = 'capcha_data'
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            # Отправка запроса на получение изображения
            # Sending a request for an image
            response = requests.get(img_url_background)

            # Сохранение изображения в папку
            # Save image to folder
            with open(os.path.join(folder_name, 'photo.jpg'), 'wb') as f:
                f.write(response.content)

            # Отправка запроса на получение пазла
            # Sending a request to receive a puzzle
            response = requests.get(img_url_puzzle)

            # Сохранение изображения в папку
            # Saving the puzzle image to a folder
            with open(os.path.join(folder_name, 'puzzle.jpg'), 'wb') as f:
                f.write(response.content)

            # Пауза для загрузки фото
            # Pause to download photos
            time.sleep(3)

            # Решение Captcha
            # Solving Captcha
            solver = PuzzleSolver("capcha_data/puzzle.jpg", "capcha_data/photo.jpg")
            solution = solver.get_position()
            solution = int(ceil(solution / 2.06))

            # Поиск ползунка и перемещением его на необходимое значение
            # Find the slider and move it to the required value
            slider = driver.find_element(By.CLASS_NAME, "yidun_slider")
            action_chains = ActionChains(driver)
            action_chains.click_and_hold(slider).move_by_offset(solution, 0).release().perform()
            action_chains.click()

            # Ожидание проверки Captcha
            # Waiting for Captcha verification
            time.sleep(5)

            # Удаление папки с элементами Captcha
            # Deleting a folder with Captcha elements
            try:
                os.rmdir(folder_name)
            except:
                pass

        except Exception as e:
            print(f'error: {e}')


# Функция ввода SMS для входа
# SMS input function for login
def buff_sms(driver, sms):
    # Поиск элемента для ввода SMS
    # Search for an element to enter SMS
    input_field = driver.find_element(By.NAME, 'phonecode')
    input_field.send_keys(sms)

    # Поиск кнопки входа и нажатие
    # Search for the login button and press
    login_button = driver.find_element(By.XPATH, '//a[@class="u-loginbtn btncolor tabfocus"]')
    login_button.click()

    # Пауза для завершения входа
    # Pause to complete login
    time.sleep(5)


# Функция запуска парсинга элементов, выгодных к перепродаже
# Function to start parsing elements that are profitable for resale
async def start_search(driver, bot, user_id, min_price):
    while True:
        # Указание количества страниц, которые будем обрабатывать
        # Indicating the number of pages that will be processed
        for i in range(1, 1200):
            # Получение страницы с элементами CS:GO
            # Getting a page with CS:GO items
            link = f'https://buff.163.com/market/csgo#game=csgo&page_num={i}&min_price={min_price}&tab=selling'
            driver.get(link)
            link = f'https://buff.163.com/market/csgo#game=csgo&page_num={i}&tab=selling'
            # Установка ожидания для загрузки страницы
            # Setting the time to wait for a page to load
            time.sleep(1.5)

            # Создание списка ссылок элементов на странице
            # Creating a list of element links on a page
            links_on_page = []
            names_on_page = []

            # Получение HTML кода страницы для дальнейшего поиска элементов в нем
            # Obtaining the HTML code of a page for further searching for elements in it
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Поиск окна с предметами cs:go
            # Finding a window with cs:go items
            ul_elements = soup.find_all('ul', class_='card_csgo')
            print(len(ul_elements))

            # Выделение ссылки и названия из каждого предмета и добавление в список
            # Extract the link and name from each item and add to the list
            for ul in ul_elements:
                a_elements = ul.find_all('a')

                links = [a.get('href') for a in a_elements]

                for link in links:
                    full_link = f"https://buff.163.com/{link}"
                    links_on_page.append(full_link)

                names = [a.get('title') for a in a_elements]
                for name in names:
                    names_on_page.append(name)

                # Оставляем только уникальные элементы в списках, сохраняя порядок
                # Keep only unique elements in lists, maintaining order
                links_on_page[:] = [x for i, x in enumerate(links_on_page) if i == links_on_page.index(x)]
                names_on_page[:] = [x for i, x in enumerate(names_on_page) if i == names_on_page.index(x)]

                i = -1

                # Обработка страниц предметов
                # Processing item pages
                for link in links_on_page:
                    try:
                        i += 1
                        # Устанавливаем значение float в соответствии с износом оружия
                        # Set the float value according to weapon wear
                        if str(names_on_page[i]).split('(')[1].split(')')[0] == "Field-Tested":
                            item = str(link) + "&min_paintwear=0.15&max_paintwear=0.17" + f"&page_num=1"
                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Factory New":
                            item = str(link) + "&min_paintwear=0.0001&max_paintwear=0.001" + f"&page_num=1"
                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Minimal Wear":
                            item = str(link) + "&min_paintwear=0.07&max_paintwear=0.08" + f"&page_num=1"

                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Well-Worn":
                            item = str(link) + "&min_paintwear=0.38&max_paintwear=0.39" + f"&page_num=1"
                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Battle-Scarred":
                            item = str(link) + "&min_paintwear=0.999&max_paintwear=0.9999" + f"&page_num=1"
                        else:
                            continue

                        driver.get(item)
                        time.sleep(4)

                        driver.save_screenshot('msg.png')

                        elements = driver.find_elements(By.CLASS_NAME, 'f_Strong')
                        competitor = elements[2].text

                        try:
                            pattern = r'\d+\.\d+'
                            matches = re.findall(pattern, competitor)
                            number1 = round(float(matches[0]), 2) * 13.07
                        except:
                            pattern = r'\d+'
                            matches = re.findall(pattern, competitor)
                            number1 = round(float(matches[0]), 2) * 13.07
                        if number1 < 100:
                            continue

                        if str(names_on_page[i]).split('(')[1].split(')')[0] == "Field-Tested":
                            link = str(link) + "&min_paintwear=0.2&max_paintwear=0.21" + f"&page_num=1"
                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Factory New":
                            link = str(link) + "&min_paintwear=0.001&max_paintwear=0.01" + f"&page_num=1"
                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Minimal Wear":
                            link = str(link) + "&min_paintwear=0.09&max_paintwear=0.1" + f"&page_num=1"
                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Well-Worn":
                            link = str(link) + "&min_paintwear=0.39&max_paintwear=0.44" + f"&page_num=1"
                        elif str(names_on_page[i]).split('(')[1].split(')')[0] == "Battle-Scarred":
                            link = str(link) + "&min_paintwear=0.98&max_paintwear=0.99" + f"&page_num=1"
                        else:
                            continue

                        driver.get('https://example.com/')
                        driver.get(link)
                        time.sleep(4)

                        elements = driver.find_elements(By.CLASS_NAME, 'f_Strong')
                        min_price_for_sell = elements[2].text

                        try:
                            pattern = r'\d+\.\d+'
                            matches = re.findall(pattern, min_price_for_sell)
                            number2 = round(float(matches[0]), 2) * 13.07
                        except:
                            pattern = r'\d+'
                            matches = re.findall(pattern, min_price_for_sell)
                            number2 = round(float(matches[0]), 2) * 13.07

                        item_price = round(number2 * 1.03, 2)
                        price_delta = round(item_price - number2, 2)
                        item_link = item

                        response = (f"{names_on_page[i]}\n"
                                    f"Минимальная цена на продажу - ₽ {number2}\n"
                                    f"Цена предмета - ₽ {item_price}\n"
                                    f"Переплата от минимальной цены - ₽ {price_delta}\n"
                                    f"Конкурент с таким флоатом - ₽ {number1}\n"
                                    f"{item_link}")

                        if item_price * 0.8 >= number1:
                            with open('msg.png', 'rb') as photo:
                                await bot.send_photo(user_id, photo=BufferedInputFile(
                                    photo.read(),
                                    filename="msg.png"
                                ), caption=response
                                                     )
                        else:
                            await bot.send_message(user_id, f"Не подходит\n\n{response}")

                    except Exception as e:
                        print(f'error: {e}')
