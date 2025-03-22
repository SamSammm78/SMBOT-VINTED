import json
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import os

def scrape_vinted(url):
    """Scrape les annonces Vinted pour un URL donné"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")  # Réduit les logs
    chrome_options.add_argument("--disable-logging")  # Désactive les logs de Chrome
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".feed-grid__item"))
        )

        # Scrolling pour charger plus d'annonces
        for _ in range(3):  # Réduit le nombre d'itérations pour optimiser
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5, 2.5))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select('.feed-grid__item')

        data = []
        for item in items:
            try:
                title_elem = item.select_one('.web_ui__ItemBox__title')
                price_elem = item.select_one('.title-content')
                img_elem = item.select_one('img')
                link_elem = item.select_one('a')

                title = title_elem.text.strip() if title_elem else "N/A"
                price = price_elem.text.strip() if price_elem else "N/A"
                img_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else "N/A"
                item_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "N/A"

                # Vérifier si l'URL contient "/member/" et l'ignorer
                if "/member/" in item_url:
                    continue

                data.append({
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'url': item_url # Ajout du domaine pour une URL complète
                })

            except Exception as e:
                print(f"Erreur lors du traitement d'un article: {e}")

        return data
    except Exception as e:
        print(f"Erreur lors du scraping: {e}")
        return []
    finally:
        try:
            print("Scrapping réussi ✅")
            driver.quit()
        except Exception as e:
            print(f"Erreur lors de la fermeture du driver : {e}")
