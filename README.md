# Лабораторна робота №8: Побудова CI/CD Pipeline

Цей репозиторій містить автоматизований BDD-проєкт (Selenium + Behave) для тестування вебзастосунку [Swag Labs](https://www.saucedemo.com/), розширений інфраструктурою безперервної інтеграції (CI/CD Pipeline as Code) на базі **Jenkins** у **Docker**-контейнері.

---

## 1. Архітектура CI/CD та Quality Gate

Пайплайн описано у файлі `Jenkinsfile` та реалізовано за концепцією **Quality Gate**:
1. **Checkout** — клонування актуального коду з гілки `main`.
2. **Static Code Analysis** — статичний аналіз коду лінтером `pylint --disable=C,R features/` у ізольованому `venv` із виводом оцінки та збереженням артефакту `pylint_report.txt`.
3. **Install Dependencies** — встановлення залежностей із `requirements.txt` у віртуальне середовище `venv`.
4. **Run UI Tests** — запуск автотестів `behave` у headless-режимі (`--headless=new`, Chromium) з генерацією результатів `allure-results` (обгорнуто в `catchError`).
5. **Reporting (post-actions)** — автоматичне формування та публікація інтерактивного Allure-звіту й архівація звіту Pylint незалежно від результату тестів (`always`).

---

## 2. Збірка та запуск Jenkins у Docker-контейнері

### Крок 1. Збірка кастомного образу
Образ містить Jenkins LTS, Python 3, venv, Chromium, ChromeDriver, Allure CLI 2.x та необхідні плагіни (`git`, `workflow-aggregator`, `allure-jenkins-plugin`):

```bash
docker build -t my-jenkins .
```

### Крок 2. Запуск контейнера
Запустіть контейнер у фоновому режимі з прокиданням портів `8080` (вебінтерфейс), `50000` (агенти) та монтуванням постійного тому `jenkins_home`:

```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins my-jenkins
```

### Крок 3. Отримання початкового пароля адміністратора
Після запуску відкрийте браузер за адресою [http://localhost:8080](http://localhost:8080). Для першого входу виконайте команду в терміналі:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
Скопіюйте згенерований ключ, вставте у поле входу Jenkins та створіть обліковий запис адміністратора.

---

## 3. Налаштування Allure Commandline у Jenkins

Оскільки Allure CLI вже попередньо завантажений та розпакований в образі за шляхом `/opt/allure-2.30.0` (та має симлінк `/opt/allure`):

1. Перейдіть у **Manage Jenkins** → **Tools** (або **Global Tool Configuration**).
2. Прокрутіть до розділу **Allure Commandline Installations**.
3. Натисніть **Add Allure Commandline**.
4. Вкажіть параметри:
   - **Name:** `allure`
   - **Install automatically:** зніміть прапорець (uncheck).
   - **Installation directory (HOME):** `/opt/allure` (або `/opt/allure-2.30.0`).
5. Натисніть **Save** (або **Apply**).

---

## 4. Створення Pipeline Job у Jenkins

1. На головній сторінці Jenkins натисніть **New Item**.
2. Введіть назву проєкту (наприклад, `SauceDemo-BDD-Pipeline`) та виберіть тип **Pipeline**. Натисніть **OK**.
3. У налаштуваннях завдання перейдіть до секції **Pipeline**:
   - **Definition:** виберіть `Pipeline script from SCM`.
   - **SCM:** оберіть `Git`.
   - **Repository URL:** вкажіть URL вашого репозиторію на GitHub (наприклад, `https://github.com/kasperskaaa/lab8-cicd-jenkins-behave.git`).
   - **Branch Specifier:** `*/main`.
   - **Script Path:** `Jenkinsfile`.
4. Натисніть **Save**.
5. Натисніть **Build Now** для першого запуску.

---

## 5. Налаштування автоматичного тригера (Poll SCM або Webhook)

Для забезпечення автоматичного запуску пайплайну при оновленні коду:

### Варіант А. Poll SCM (періодичне опитування репозиторію)
1. У налаштуваннях Job перейдіть до розділу **Build Triggers**.
2. Поставте прапорець біля **Poll SCM**.
3. У полі **Schedule** задайте розклад, наприклад опитування кожні 5 хвилин:
   ```cron
   H/5 * * * *
   ```
4. Збережіть налаштування. Тепер Jenkins автоматично перевірятиме наявність нових комітів у гілці `main`.

### Варіант Б. GitHub Webhook (миттєвий тригер)
1. У розділі **Build Triggers** виберіть **GitHub hook trigger for GITScm polling**.
2. У налаштуваннях репозиторію на GitHub перейдіть у **Settings** → **Webhooks** → **Add webhook**.
3. Вкажіть **Payload URL:** `http://<ВАШ_ПУБЛІЧНИЙ_IP_АБО_NGROK>:8080/github-webhook/`, Content type: `application/json`, подія: `Just the push event`.

---

## 6. Локальний запуск (без Docker)

Для локальної перевірки сценаріїв та лінтингу:

```bash
# 1. Створення та активація venv
python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 2. Встановлення залежностей
pip install -r requirements.txt

# 3. Статичний аналіз коду
pylint --disable=C,R features/

# 4. Запуск UI-тестів у Headless режимі
behave -f allure_behave.formatter:AllureFormatter -o allure-results
```
