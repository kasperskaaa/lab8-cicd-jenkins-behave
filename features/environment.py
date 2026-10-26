# pylint: disable=not-callable,unused-argument,broad-exception-caught
"""
Hooks and environment setup for Behave BDD tests with Selenium.
Supports headless execution in CI/CD (Docker / Jenkins) and local environments.
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import allure


def before_scenario(context, scenario):
    """
    Ініціалізація браузера перед початком кожного BDD-сценарію.
    Встановлює обов'язкові параметри для стабільного запуску в headless-режимі.
    """
    options = Options()

    # Опції headless-режиму для безперешкодної роботи в CI/Docker
    is_headless = os.getenv("HEADLESS", "1").strip().lower() not in ("0", "false", "no")

    if is_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

    # Додаткові опції стабільності та усунення сторонніх спливаючих вікон
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument("--disable-features=PasswordGeneration,PasswordManagerUI")
    options.add_argument("--disable-save-password-bubble")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
    }
    options.add_experimental_option("prefs", prefs)

    # Вказівка на бінарний файл браузера (якщо задано CHROME_BIN, наприклад /usr/bin/chromium)
    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin and os.path.exists(chrome_bin):
        options.binary_location = chrome_bin

    # Визначення шляху до виконуваного файлу ChromeDriver:
    # 1. Прямий шлях зі змінної оточення CHROMEDRIVER_PATH (якщо вказано в Docker/CI)
    # 2. Динамічне встановлення через ChromeDriverManager
    # 3. Резервний запуск через вбудований Selenium Manager
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
    if chromedriver_path and os.path.exists(chromedriver_path):
        service = Service(executable_path=chromedriver_path)
        context.driver = webdriver.Chrome(service=service, options=options)
    else:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            context.driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            context.driver = webdriver.Chrome(options=options)

    if not is_headless:
        context.driver.maximize_window()

    context.driver.implicitly_wait(5)


def after_step(context, step):
    """
    Хук після кожного кроку: у разі збою автоматично робить скріншот
    і прикріплює його до звітності Allure.
    """
    if step.status == "failed" and hasattr(context, "driver") and context.driver:
        try:
            screenshot = context.driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"Failed step: {step.name}",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass


def after_scenario(context, scenario):
    """Гарантоване закриття браузера після завершення кожного сценарію."""
    if hasattr(context, "driver") and context.driver:
        context.driver.quit()
