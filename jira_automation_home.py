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
#Функция для отправки сообщения в Telegram
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
PHRASES = ["Добавить внешнего сотрудника", "Доступ к VPN", "Доступ в ServiceDesk", "Права доступа в TestIT", "Доступ в Hadoop АП", "Добавление в рассылку", "Redash", "Увеличение объема почтового ящика", "Добавление внешнего", "Grafana", "Отключить внешнего сотрудника", "Управление группой AD"]
SPECIAL_PHRASES = ["Список рассылки", "Увеличение объема почтового ящика", "Общий почтовый ящик"]  # Список для особых координат
CHECK_INTERVAL = 3  # Интервал проверки в секундах
REFRESH_INTERVAL = 6  # Интервал обновления страницы в секундах

# Инициализация драйвера
service = Service(DRIVER_PATH)
driver = webdriver.Chrome(service=service)

# Открываем страницу с очередью заявок
driver.get(JIRA_URL)

# Флаг для паузы
pause_flag = False

# Флаг для режима быстрого действия
quick_action_mode = False

# Время последнего обновления страницы
last_refresh_time = time.time()

# Функция для проверки наличия строк с определенными фразами
def check_for_phrases():
    global pause_flag, last_refresh_time
    try:
        # Ожидаем загрузки таблицы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )
        
        # Получаем все строки таблицы
        rows = driver.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            # Ищем ячейку с классом "string summary"
            summary_cell = row.find_elements(By.CLASS_NAME, "string.summary")
            if summary_cell:
                summary_text = summary_cell[0].text
                # Проверяем, содержит ли текст ячейки одну из фраз из SPECIAL_PHRASES
                if any(phrase in summary_text for phrase in SPECIAL_PHRASES):
                    logging.info(f"Найдена заявка с особой фразой: {summary_text}")
                    send_telegram_message(f"Урвала: {summary_text}")
                    # Находим ссылку в строке
                    link = row.find_element(By.TAG_NAME, "a")
                    # Открываем ссылку в новой вкладке
                    link.send_keys(Keys.CONTROL + Keys.RETURN)
                    # Переключаемся на новую вкладку
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Ожидаем загрузки страницы
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Находим кнопку "Очередь" и нажимаем на неё
                    queue_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "opsbar-transitions_more"))
                    )
                    queue_button.click()
                    logging.info("Кнопка 'Очередь' нажата.")
                    
                    # Ожидаем появления выпадающего меню
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "opsbar-transitions_more_drop"))
                    )
                    
                    # Задержка перед нажатием кнопки
                    time.sleep(2)
                    
                    # Определяем координаты в зависимости от типа заявки
                    x, y = -1163, 710  # Координаты для SPECIAL_PHRASES
                    
                    # Используем pyautogui для нажатия на кнопку "Выполнение"
                    pyautogui.moveTo(x, y, duration=0.5)  # Плавное перемещение
                    pyautogui.click()
                    logging.info(f"Нажатие на кнопку 'Выполнение' по координатам ({x}, {y}).")
                    time.sleep(2)
                    # Закрываем вкладку и возвращаемся к основной
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break
                # Проверяем, содержит ли текст ячейки одну из фраз из PHRASES
                elif any(phrase in summary_text for phrase in PHRASES):
                    logging.info(f"Найдена заявка: {summary_text}")
                    send_telegram_message(f"Урвала: {summary_text}")
                    # Находим ссылку в строке
                    link = row.find_element(By.TAG_NAME, "a")
                    # Открываем ссылку в новой вкладке
                    link.send_keys(Keys.CONTROL + Keys.RETURN)
                    # Переключаемся на новую вкладку
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Ожидаем загрузки страницы
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Находим кнопку "Очередь" и нажимаем на неё
                    queue_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "opsbar-transitions_more"))
                    )
                    queue_button.click()
                    logging.info("Кнопка 'Очередь' нажата.")
                    
                    # Ожидаем появления выпадающего меню
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "opsbar-transitions_more_drop"))
                    )
                    
                    # Задержка перед нажатием кнопки
                    time.sleep(2)
                    
                    # Определяем координаты в зависимости от типа заявки
                    x, y = -1186, 676  # Стандартные координаты
                    
                    # Используем pyautogui для нажатия на кнопку "Выполнение"
                    pyautogui.moveTo(x, y, duration=0.5)  # Плавное перемещение
                    pyautogui.click()
                    logging.info(f"Нажатие на кнопку 'Выполнение' по координатам ({x}, {y}).")
                    time.sleep(2)
                    # Закрываем вкладку и возвращаемся к основной
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

# Функция для обновления страницы
def refresh_page():
    global last_refresh_time, quick_action_mode
    driver.refresh()
    logging.info("Страница обновлена.")
    last_refresh_time = time.time()
    
    # Если включен режим быстрого действия, выполняем его
    if quick_action_mode and not pause_flag:
        # Быстрое движение мыши, чтобы предотвратить блокировку
        pyautogui.moveRel(10, 10, duration=0.1)  # Перемещение мыши на 10 пикселей вправо и вниз
        pyautogui.moveRel(-10, -10, duration=0.1)  # Возвращение мыши на исходное место
        logging.info("Быстрое действие выполнено.")

# Функция для обработки команд из командной строки
def command_listener():
    global pause_flag, quick_action_mode
    while True:
        command = input("Введите команду (0 - пауза, 1 - продолжение, 2 - режим быстрого действия): ")
        if command == "0":
            pause_flag = True
            quick_action_mode = False  # Гарантированно отключаем быстрый режим при паузе
            logging.info("Пауза активирована. Режим быстрого действия выключен.")
        elif command == "1":
            pause_flag = False
            quick_action_mode = False  # Гарантированно отключаем быстрый режим при продолжении
            logging.info("Пауза снята. Режим быстрого действия выключен.")
        elif command == "2":
            if not pause_flag:
                quick_action_mode = not quick_action_mode
                status = "включен" if quick_action_mode else "выключен"
                logging.info(f"Режим быстрого действия {status}.")
            else:
                logging.info("Режим быстрого действия нельзя изменить во время паузы.")

# Запуск потока для прослушивания команд
threading.Thread(target=command_listener, daemon=True).start()

# Основной цикл проверки
try:
    while True:
        if not pause_flag:
            # Проверяем, нужно ли обновить страницу
            if time.time() - last_refresh_time > REFRESH_INTERVAL:
                refresh_page()
            check_for_phrases()
        time.sleep(CHECK_INTERVAL)
except KeyboardInterrupt:
    logging.info("Скрипт остановлен пользователем.")
finally:
    # Закрываем драйвер
    driver.quit()
    logging.info("Драйвер закрыт.")