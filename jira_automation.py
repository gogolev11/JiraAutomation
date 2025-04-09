from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import logging
import pyautogui
import threading
import requests

# Настройка логирования
logging.basicConfig(filename='jira_automation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    bot_token = '7554472298:AAHIr0apogP1plAN5XI_Dt7XG_ZlcNS40VI'
    chat_id = '359829132'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response.json()

# Параметры
DRIVER_PATH = r'C:\WebDriver\chromedriver.exe'
JIRA_URL = 'https://help.crpt.ru/secure/QueuesExtensionAction.jspa?queue=1662626461947&queuePageNumber=1'
PHRASES = ["Добавить внешнего сотрудника", "Доступ к VPN", "Доступ в ServiceDesk", "Права доступа в TestIT", "Доступ в Hadoop АП", "Добавление в рассылку", "Redash", "Увеличение объема почтового ящика", "Добавление внешнего", "Grafana", "Отключить внешнего сотрудника", "Управление группой AD", "Сброс пароля учетной записи"]
SPECIAL_PHRASES = ["Список рассылки", "Увеличение объема почтового ящика", "Общий почтовый ящик","Redash"]
LAZY_PHRASES = ["Доступ к VPN", "Доступ в ServiceDesk","Доступ в Hadoop АП","Grafana","▲ Добавление в рассылку"]
CHECK_INTERVAL = 3
REFRESH_INTERVAL = 6

# Инициализация драйвера
service = Service(DRIVER_PATH)
driver = webdriver.Chrome(service=service)
driver.get(JIRA_URL)

pause_flag = False
quick_action_mode = False
lazy_mode = False  # Добавлен флаг ленивого режима
last_refresh_time = time.time()

def check_for_phrases():
    global pause_flag, last_refresh_time
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )
        rows = driver.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            summary_cell = row.find_elements(By.CLASS_NAME, "string.summary")
            if summary_cell:
                summary_text = summary_cell[0].text
                
                if lazy_mode:
                    target_phrases = LAZY_PHRASES
                else:
                    target_phrases = SPECIAL_PHRASES + PHRASES

                if any(phrase in summary_text for phrase in target_phrases):
                    logging.info(f"Найдена заявка: {summary_text}")
                    send_telegram_message(f"Урвала: {summary_text}")
                    link = row.find_element(By.TAG_NAME, "a")
                    link.send_keys(Keys.CONTROL + Keys.RETURN)
                    driver.switch_to.window(driver.window_handles[1])

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    queue_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "opsbar-transitions_more"))
                    )
                    queue_button.click()
                    logging.info("Кнопка 'Очередь' нажата.")

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "opsbar-transitions_more_drop"))
                    )

                    time.sleep(2)
                    x, y = -1163, 357 if summary_text in SPECIAL_PHRASES else -1145, 323
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    logging.info(f"Нажатие на кнопку 'Выполнение' по координатам ({x}, {y}).")
                    time.sleep(2)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

def refresh_page():
    global last_refresh_time, quick_action_mode
    driver.refresh()
    logging.info("Страница обновлена.")
    last_refresh_time = time.time()
    if quick_action_mode:
        pyautogui.moveRel(10, 10, duration=0.1)
        pyautogui.moveRel(-10, -10, duration=0.1)
        logging.info("Быстрое действие выполнено.")

def command_listener():
    global pause_flag, quick_action_mode, lazy_mode
    while True:
        command = input("Команда (0 - пауза, 1 - продолжить, 2 - быстро, 3 - lazy): ")
        if command == "0":
            pause_flag = True
            logging.info("Пауза активирована.")
        elif command == "1":
            pause_flag = False
            logging.info("Пауза снята.")
        elif command == "2":
            quick_action_mode = not quick_action_mode
            status = "включен" if quick_action_mode else "выключен"
            logging.info(f"Режим быстрого действия {status}.")
        elif command == "3":
            lazy_mode = not lazy_mode
            status = "включен" if lazy_mode else "выключен"
            logging.info(f"Lazy mode {status}.")

threading.Thread(target=command_listener, daemon=True).start()

try:
    while True:
        if not pause_flag:
            if time.time() - last_refresh_time > REFRESH_INTERVAL:
                refresh_page()
            check_for_phrases()
        time.sleep(CHECK_INTERVAL)
except KeyboardInterrupt:
    logging.info("Скрипт остановлен пользователем.")
finally:
    driver.quit()
    logging.info("Драйвер закрыт.")
