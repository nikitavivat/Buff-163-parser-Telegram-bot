#### Description / Описание

This Telegram bot is designed for parsing buff.163.com. It utilizes Selenium to interact with the Buff website. The core functionality is implemented in `buff_163_parser.py`.

Этот телеграм-бот предназначен для парсинга сайта buff.163.com. Для взаимодействия с сайтом используется Selenium. Основной функционал реализован в файле `buff_163_parser.py`.

#### Usage / Использование

1. **Setting up Selenium driver / Настройка драйвера Selenium**:

   Before using the bot, you need to create a Selenium driver and log in to Buff with your phone number and SMS verification.

   Прежде чем использовать бота, необходимо создать драйвер Selenium и войти в Buff, используя свой номер телефона и SMS-верификацию.

   ```python
   from buff_163_parser import buff_login, buff_sms
   from selenium import webdriver

   # Initialize Selenium driver
   driver = webdriver.Chrome(executable_path="path_to_chromedriver")

   # Log in to Buff
   buff_login(driver, phone_number)
   
   # Wait for space
   print("Press Space to continue...")
   keyboard.wait("space")
   
   # Input SMS
   buff_sms(driver, sms)
   ```

2. **Solving Slider Captcha / Решение Slider Captcha**:

   The `solver.py` file contains code for solving the Slider Captcha.

   Файл `solver.py` содержит код для решения Slider Captcha.

3. **Setting up Telegram bot / Настройка телеграм-бота**:

   Specify your Telegram bot token in the `.env` file. The main bot code is located in `main.py`.

   Укажите токен вашего телеграм-бота в файле `.env`. Основной код бота находится в файле `main.py`.

4. **Starting item search / Запуск поиска предметов**:

   The bot searches for items with a low float value in their quality (FN, MW, FT, WW, BS) priced at least 20% lower than those with a higher float value.

   Бот ищет предметы с низким значением флоата в их качестве (FN, MW, FT, WW, BS), цены на которые меньше на 20% по сравнению с предметами с более высоким значением флоата.

   ```python
   from buff_163_parser import start_search

   # Start item search
   await start_search(driver, bot, user_id, 100)
   ```

   - `driver`: Selenium driver
   - `bot`: Telegram bot instance
   - `user_id`: Bot user ID
   - `100`: Minimum price of items to search for

#### Example / Пример использования

```python
import keyboard
from buff_163_parser import buff_login, buff_sms, start_search
from selenium import webdriver

# Initialize Selenium driver
driver = webdriver.Chrome(executable_path="path_to_chromedriver")

# Log in to Buff
buff_login(driver, phone_number)

# Wait for space
print("Press Space to continue...")
keyboard.wait("space")

# Input SMS
buff_sms(driver, sms)

# Start item search
await start_search(driver, bot, user_id, 100)
```
