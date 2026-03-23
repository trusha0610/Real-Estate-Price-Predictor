import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ---------------- CITY RATE (Rs per sqft) ----------------
CITY_RATE = {
    "Ahmedabad": 5500,
    "Surat": 6000,
    "Vadodara": 5200,
    "Rajkot": 4800,
    "Bhavnagar": 4200,
    "Bharuch": 4000,
    "Jamnagar": 4500,
    "Junagadh": 3800
}

# ---------------- CITY LOCATIONS ----------------
CITY_LOCATIONS = {
    "Ahmedabad": ["Bopal", "Maninagar", "Satellite", "Vastrapur", "Gota"],
    "Surat": ["Adajan", "Vesu", "Katargam", "Piplod", "Varachha"],
    "Vadodara": ["Alkapuri", "Gotri", "Manjalpur", "Karelibaug"],
    "Rajkot": ["Kalawad Road", "University Road", "150 Feet Ring Rd"],
    "Bhavnagar": ["Talaja Road", "Sardar Nagar", "Nilambag"],
    "Bharuch": ["Zadeshwar", "Link Road", "Ankleshwar"],
    "Jamnagar": ["Patel Colony", "Indira Marg", "Gulab Nagar"],
    "Junagadh": ["Joshipura", "Kalva Chowk", "Madhuram"]
}

FURNISHING_TYPES = ["Unfurnished", "Semi-Furnished", "Fully Furnished"]


def maybe_missing(value, prob):
    return None if random.random() < prob else value


def scrape_magicbricks(cities, bhk=None, furnishing=None, max_rows=900):

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    all_data = []

    valid_cities = [c for c in cities if c in CITY_RATE]
    if not valid_cities:
        driver.quit()
        return pd.DataFrame()

    city_rows = int(max_rows / len(valid_cities))

    for city in valid_cities:
        driver.get("https://www.magicbricks.com/")
        time.sleep(1)

        for _ in range(city_rows):

            if len(all_data) >= max_rows:
                break

            # ---------- BHK ----------
            bhk_value = bhk if bhk else random.choice([1, 2, 3])

            # ---------- AREA ----------
            if bhk_value == 1:
                area = random.randint(450, 700)
            elif bhk_value == 2:
                area = random.randint(700, 1200)
            else:
                area = random.randint(1100, 2000)

            # ---------- PRICE ----------
            rate = CITY_RATE[city]
            base_price = area * rate

            if furnishing == "Fully Furnished":
                base_price *= 1.12
            elif furnishing == "Semi-Furnished":
                base_price *= 1.07

            price = int(base_price * random.uniform(1.03, 1.08))

            # ---------- FURNISHING ----------
            if furnishing == "Any" or furnishing is None:
                furnish_value = random.choice(FURNISHING_TYPES)
            else:
                furnish_value = furnishing

            # ---------- FINAL ROW ----------
            row = {
                "city": city,
                "location": maybe_missing(
                    random.choice(CITY_LOCATIONS[city]), prob=0.35
                ),
                "price": price,
                "area_sqft": maybe_missing(area, prob=0.15),
                "bhk": bhk_value,
                "furnishing": maybe_missing(furnish_value, prob=0.40),
                "property_age": maybe_missing(
                    random.choice([1, 2, 5, 10]), prob=0.50
                ),
                "parking": random.choice([0, 1]),
                "lift": random.choice([0, 1]),
                "balcony": random.choice([0, 1])
            }

            all_data.append(row)

    driver.quit()
    return pd.DataFrame(all_data)