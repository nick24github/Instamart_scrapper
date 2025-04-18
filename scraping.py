from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Set up Chrome
options = Options()
# options.add_argument("--headless")  # You can uncomment this if you want it headless
service = Service("/usr/local/bin/chromedriver")

driver = webdriver.Chrome(service=service, options=options)

# Only for one category for now 
url = "https://dir.indiamart.com/impcat/face-mask.html"

driver.get(url)
time.sleep(5)  # Wait for page to load fully

# Scroll a bit to load more results
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# Extract all product blocks
product_blocks = driver.find_elements(By.CSS_SELECTOR, "div.rht.pnt.flx")

results = []

for block in product_blocks:
    try:
        # Get the title
        title_tag = block.find_element(By.CSS_SELECTOR, "a.ptitle h3")
        title = title_tag.text.strip()

        # Get the price
        price_tag = block.find_element(By.CSS_SELECTOR, "p.price span.prc")
        price = price_tag.text.strip()

        results.append({
            "title": title,
            "price": price
        })
    except Exception as e:
        print("Skipping a block due to:", e)
        continue

driver.quit()

# Save to CSV
df = pd.DataFrame(results)
df.to_csv("indiamart_face_masks.csv", index=False)
print("Data saved to indiamart_face_masks.csv")


# ========== PART B: Exploratory Data Analysis ==========
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Load CSV
df = pd.read_csv("indiamart_face_masks.csv")

# Add title length
df["title_length"] = df["title"].apply(len)

# Clean price: extract numeric value from strings like '₹ 1/Piece'
def extract_price(text):
    match = re.search(r'₹\s*([\d.,]+)', text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

df["numeric_price"] = df["price"].apply(extract_price)

# Save cleaned version
df.to_csv("indiamart_face_masks_cleaned.csv", index=False)

# -------- Basic Info --------
print("\n Dataset Info:")
print(df.info())

print("\n Sample Rows:")
print(df.head())

print("\n Price Summary:")
print(df["numeric_price"].describe())

# -------- Visualizations --------

# Title length distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["title_length"], bins=15, kde=True)
plt.title("Distribution of Product Title Lengths")
plt.xlabel("Title Length")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("title_length_distribution.png")
plt.show()

# Price distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["numeric_price"].dropna(), bins=10, kde=True, color="green")
plt.title("Price Distribution of Face Masks")
plt.xlabel("Price (₹)")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("price_distribution.png")
plt.show()
