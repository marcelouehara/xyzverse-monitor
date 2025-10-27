# -*- coding: utf-8 -*-
"""monitor_xyzverse.py
Monitoramento diário do XYZVerse usando Playwright e envio de e-mail.
"""

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
import os
import re

def get_xyzverse_data():
    """Captura os valores do site XYZVerse usando Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://xyzverse.io/pt", timeout=60000)

        # Espera os elementos carregarem
        page.wait_for_selector("span.Cards_amount__XRyyb.Cards_number__tCA2G")
        page.wait_for_selector("span.Cards_gray__b1UW2.Cards_small__6NNSv")
        page.wait_for_selector("div.Cards_small__6NNSv span.Cards_green__M3yEH")

        # Captura os valores corretos
        current_text = page.locator("span.Cards_amount__XRyyb.Cards_number__tCA2G").first.text_content()
        goal_text = page.locator("span.Cards_gray__b1UW2.Cards_small__6NNSv").filter(has_text="$").first.text_content()
        price_now = page.locator("span.Cards_number__tCA2G").nth(1).text_content()
        next_price = page.locator("div.Cards_small__6NNSv span.Cards_green__M3yEH").first.text_content()

        browser.close()

        # Processar números
        current_val = float(re.sub(r"[^\d.]", "", current_text))
        goal_val = float(re.sub(r"[^\d.]", "", goal_text))
        percent = round((current_val / goal_val) * 100, 2)

        # Timestamp SP
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")

        # Mensagem final
        message = (
            f"Atualização XYZVerse - {timestamp}\n\n"
            f"Captação: ${current_val:,.2f} / ${goal_val:,.2f} ({percent}%)\n"
            f"Preço atual: {price_now}\n"
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
