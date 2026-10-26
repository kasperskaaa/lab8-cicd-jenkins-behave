FROM jenkins/jenkins:lts

USER root

# Встановлення Python3, venv, curl та Chromium з ChromeDriver для headless-тестування
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Встановлення Allure Commandline 2.x з офіційного релізу GitHub
ARG ALLURE_VERSION=2.30.0
RUN curl -fsSL -o /tmp/allure.tgz "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz" \
    && tar -zxvf /tmp/allure.tgz -C /opt/ \
    && rm /tmp/allure.tgz \
    && ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure \
    && ln -s /opt/allure-${ALLURE_VERSION} /opt/allure

# Попереднє встановлення плагінів Jenkins: git, workflow-aggregator, allure-jenkins-plugin
RUN jenkins-plugin-cli --plugins git workflow-aggregator allure-jenkins-plugin

# Змінні оточення для безперешкодного запуску браузера та драйвера в контейнері
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV HEADLESS=1

# Повернення прав користувача jenkins
USER jenkins
