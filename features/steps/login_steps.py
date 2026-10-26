# pylint: disable=not-callable
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


@given('I open the Swag Labs login page')
def step_open_login_page(context):
    """Відкриває головну сторінку авторизації."""
    context.driver.get("https://www.saucedemo.com/")


@when('I enter username "{user}" and password "{pwd}"')
def step_enter_credentials(context, user, pwd):
    """Знаходить поля введення та заповнює передані параметри."""
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    user_input = wait.until(EC.visibility_of_element_located((By.ID, "user-name")))
    user_input.clear()
    user_input.send_keys(user)

    pwd_input = context.driver.find_element(By.ID, "password")
    pwd_input.clear()
    pwd_input.send_keys(pwd)


@when('I click the login button')
def step_click_login(context):
    """Натискає кнопку Login."""
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
    login_btn.click()


@then('I should be redirected to the inventory page')
def step_verify_redirect(context):
    """Перевіряє успішний перехід до каталогу товарів."""
    wait = WebDriverWait(context.driver, 10)
    wait.until(EC.url_contains("/inventory.html"))
    assert "/inventory.html" in context.driver.current_url, (
        f"Очікувався перехід на /inventory.html, але поточна адреса: {context.driver.current_url}"
    )


@then('the page title should be "{expected_title}"')
def step_verify_title(context, expected_title):
    """Перевіряє текст заголовка сторінки."""
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    title_elem = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "title")))
    assert title_elem.text == expected_title, (
        f"Очікувався заголовок '{expected_title}', фактично: '{title_elem.text}'"
    )


@then('I should see an error message containing "{error_text}"')
def step_verify_error_message(context, error_text):
    """Перевіряє вміст повідомлення про помилку у разі невдалого входу."""
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    error_elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']")))
    assert error_text.lower() in error_elem.text.lower(), (
        f"Очікувався фрагмент '{error_text}' у повідомленні, отримано: '{error_elem.text}'"
    )


# --- Кроки для сценаріїв взаємодії з товарами та кошиком ---

@given('I am logged in as "{user}" with password "{pwd}"')
def step_logged_in_as(context, user, pwd):
    """Комплексний крок підготовки: перехід та успішна авторизація."""
    context.driver.get("https://www.saucedemo.com/")
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    user_input = wait.until(EC.visibility_of_element_located((By.ID, "user-name")))
    user_input.clear()
    user_input.send_keys(user)

    pwd_input = context.driver.find_element(By.ID, "password")
    pwd_input.clear()
    pwd_input.send_keys(pwd)

    context.driver.find_element(By.ID, "login-button").click()
    wait.until(EC.url_contains("/inventory.html"))


@when('I add "{item_name}" to the cart')
def step_add_item_to_cart(context, item_name):
    """Знаходить кнопку додавання товару за його назвою або ID."""
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    if "backpack" in item_name.lower():
        btn = wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack")))
        btn.click()
    else:
        xpath = f"//div[text()='{item_name}']/ancestor::div[@class='inventory_item']//button"
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        btn.click()


@then('the cart badge should display "{count}"')
def step_verify_cart_badge(context, count):
    """Перевіряє індикатор кількості товарів на іконці кошика."""
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    badge = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge")))
    assert badge.text == count, f"Очікувалося {count} на бейджі кошика, фактично: {badge.text}"


@when('I navigate to the shopping cart')
def step_open_shopping_cart(context):
    """Переходить на сторінку кошика."""
    wait = WebDriverWait(context.driver, 10, ignored_exceptions=[StaleElementReferenceException])
    cart_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "shopping_cart_link")))
    cart_link.click()
    wait.until(EC.url_contains("/cart.html"))


@then('the cart page should display "{item_name}"')
def step_verify_cart_item(context, item_name):
    """Перевіряє присутність товару в кошику із захистом від StaleElement."""
    def _check_item(driver):
        try:
            elems = driver.find_elements(By.CLASS_NAME, "inventory_item_name")
            names = [e.text for e in elems if e.is_displayed()]
            return item_name in names
        except (StaleElementReferenceException, NoSuchElementException):
            return False

    wait = WebDriverWait(
        context.driver,
        10,
        ignored_exceptions=[StaleElementReferenceException, NoSuchElementException],
    )
    assert wait.until(_check_item), f"Товар '{item_name}' не знайдено на сторінці кошика"
