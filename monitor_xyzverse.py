# -*- coding: utf-8 -*-
"""monitor_xyzverse.py
Monitoramento diário do XYZVerse usando Playwright e envio de e-mail.
"""

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

def get_xyzverse_data():
    """Captura os valores do site XYZVerse usando Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://xyzverse.io/pt")
        
        # Captura os valores desejados
        current_text = page.locator(".Cards_amount__XRyyb.Cards_number__tCA2G").text_content()
        goal_text = page.locator(".Cards_gray__b1UW2.Cards_small__6NNSv").text_content().replace(" / ","")
        next_price = page.locator("div:has-text('Próximo Preço') span").text_content()

        # Converte para float
        try:
            current_val = float(current_text.replace("$","").replace(",",""))
            goal_val = float(goal_text.replace("$","").replace(",",""))
        except ValueError:
            raise Exception(f"Não foi possível converter para float: current={current_text}, goal={goal_text}")

        percent = round((current_val / goal_val) * 100, 2)
        
        timestamp = (datetime.utcnow() - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")
        
        browser.close()
        
        message = (
            f"{timestamp}\n"
            f"Captação: ${current_val} / ${goal_val} ({percent}%)\n"
            f"Preço atual: {current_val}\n"
            f"Próximo preço: {next_price}"
        )
        return message

def send_email(message):
    """Envia o relatório por e-mail usando SMTP e variáveis de ambiente."""
    sender = os.environ['EMAIL_USER']
    password = os.environ['EMAIL_PASS']
    receiver = sender

    msg = MIMEText(message)
    msg['Subject'] = "Atualização XYZVerse"
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    try:
        email_text = get_xyzverse_data()
        send_email(email_text)
        print(email_text)
    except Exception as e:
        print("Erro ao executar monitoramento:", e)

