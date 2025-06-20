from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
import os
import csv

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def select_material_dropdown_option(button_xpath, option_index):
    try:
        # Open the dropdown
        dropdown_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        try:
            dropdown_btn.click()
        except:
            driver.execute_script("arguments[0].click();", dropdown_btn)

        time.sleep(1)

        # Wait for options to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//body/div[@role='presentation']//ul/li"))
        )

        options = driver.find_elements(By.XPATH, "//body/div[@role='presentation']//ul/li")

        if option_index >= len(options):
            raise Exception(f"Option index {option_index} is out of range (max: {len(options)-1})")

        # Get text BEFORE clicking to avoid stale reference
        selected_text = options[option_index].text.strip()

        # Scroll into view and click using JS to avoid intercept
        driver.execute_script("arguments[0].scrollIntoView(true);", options[option_index])
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", options[option_index])
        time.sleep(1)

        # Send ESCAPE to ensure dropdown closes
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(0.5)

        print(f"Selected: {selected_text}")
        return selected_text

    except Exception as e:
        print(f"Dropdown selection error: {e}")
        traceback.print_exc()
        driver.quit()
        exit()


# open district dropdown and count its number
def count_material_dropdown_options(dropdown_xpath):
    try:
        # Open dropdown
        dropdown_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
        )
        dropdown_btn.click()
        time.sleep(1)

        # Material UI renders list in separate div under <body>
        options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//body/div[@role='presentation']//ul/li")
            )
        )

        count = len(options)
        print(f"Found {count} options")

        # Close dropdown with ESCAPE
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(2)

        return count

    except Exception as e:
        print("Error while counting dropdown options")
        traceback.print_exc()
        driver.quit()
        exit()

import re

def safe_filename(name):
    # Replace unsafe characters with underscore
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# main 
try:
    driver.get("https://soilhealth.dac.gov.in/piechart")
    time.sleep(5)

    #  Click "MacroNutrient (Table View)"
    macro_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'MacroNutrient') and contains(text(), 'Table')]"))
    )
    try:
        macro_btn.click()
    except:
        driver.execute_script("arguments[0].click();", macro_btn)
    time.sleep(3)

    # Select Year, State, District, Block
    for i in range(3):
        year = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[1]/div/div/div", i)
        time.sleep(1)

        for j in range(5,35):
            state = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/div", j)
            time.sleep(2)

            try:
                print("Attempting to count Districts...")
                district_dropdown_xpath = "/html/body/div/div/div[2]/div/div[2]/div/div/div[3]/div/div/div"
                district_count = count_material_dropdown_options(district_dropdown_xpath)
                print(f"Found {district_count} districts.")
            except Exception as e:
                print(f"Failed to count districts for state: {state}")
                traceback.print_exc()
                driver.quit()
                exit()

            for k in range(2,district_count):    
                district = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[3]/div/div/div", k)
                time.sleep(1)

                block_dropdown_xpath = "/html/body/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div"
                block_count = count_material_dropdown_options(block_dropdown_xpath)
                print(f"Found {block_count} blocks in {district}")
                time.sleep(2)

                for l in range(1,block_count):
                    block = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div", l)
                    time.sleep(20)
    
                    # extract table data
                    table_xpath_base = "/html/body/div/div/div[2]/div/div[2]/div/div/div[5]/div/div[2]/div/div"
                    rows = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.XPATH, f"{table_xpath_base}/div"))
                    )

                    all_data = []

                    for i, _ in enumerate(rows, start=1):
                        cell_xpath = f"{table_xpath_base}/div[{i}]/div"
                        cells = driver.find_elements(By.XPATH, cell_xpath)
                        row_data = [year, state, district, block] + [cell.text.strip() for cell in cells]
                        all_data.append(row_data)

                    print(f"\nExtracted {len(all_data)} rows")

                    # writing to CSV file
                    folder_path = os.path.join("data", "raw", year, state, district)
                    os.makedirs(folder_path, exist_ok=True)
                    safe_block = safe_filename(block)
                    file_path = os.path.join(folder_path, f"{safe_block}_macro.csv")


                    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Year", "State", "District", "Block",
                                        "Village", "Nitrogen - High", "Nitrogen - Medium", "Nitrogen - Low",
                                        "Phosphorous - High", "Phosphorous - Medium", "Phosphorous - Low",
                                        "Potassium - High", "Potassium - Medium", "Potassium - Low",
                                        "OC - High", "OC - Medium", "OC - Low",
                                        "EC - Saline", "EC - Non Saline",
                                        "pH - Acidic", "pH - Neutral", "pH - Alkaline"])
                        writer.writerows(all_data)

                    print(f"Saved to {file_path}")


    # ------------------------------------------------------------------------------------
    # microNutrient (same) - todo modularization
    micro_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'MicroNutrient') and contains(text(), 'Table')]"))
    )
    try:
        micro_btn.click()
    except:
        driver.execute_script("arguments[0].click();", micro_btn)
    time.sleep(3)

    # Select Year, State, District, Block
    for i in range(3):
        year = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[1]/div/div/div", i)
        time.sleep(1)

        for j in range(2,35):
            state = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/div", j)
            time.sleep(2)

            try:
                print("Attempting to count Districts...")
                district_dropdown_xpath = "/html/body/div/div/div[2]/div/div[2]/div/div/div[3]/div/div/div"
                district_count = count_material_dropdown_options(district_dropdown_xpath)
                print(f"Found {district_count} districts.")
            except Exception as e:
                print(f"Failed to count districts for state: {state}")
                traceback.print_exc()
                driver.quit()
                exit()

            for k in range(2,district_count):    
                district = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[3]/div/div/div", k)
                time.sleep(1)

                block_dropdown_xpath = "/html/body/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div"
                block_count = count_material_dropdown_options(block_dropdown_xpath)
                print(f"Found {block_count} blocks in {district}")
                time.sleep(2)

                for l in range(1,block_count):
                    block = select_material_dropdown_option("/html/body/div/div/div[2]/div/div[2]/div/div/div[4]/div/div/div", l)
                    time.sleep(20)
    
                    # extract table data
                    table_xpath_base = "/html/body/div/div/div[2]/div/div[2]/div/div/div[5]/div/div[2]/div/div"
                    rows = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.XPATH, f"{table_xpath_base}/div"))
                    )

                    all_data = []

                    for i, _ in enumerate(rows, start=1):
                        cell_xpath = f"{table_xpath_base}/div[{i}]/div"
                        cells = driver.find_elements(By.XPATH, cell_xpath)
                        row_data = [year, state, district, block] + [cell.text.strip() for cell in cells]
                        all_data.append(row_data)

                    print(f"\nExtracted {len(all_data)} rows")

                    # Save to CSV file
                    folder_path = os.path.join("data", "raw", year, state, district)
                    os.makedirs(folder_path, exist_ok=True)
                    safe_block = safe_filename(block)
                    file_path = os.path.join(folder_path, f"{safe_block}_macro.csv")
                    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Year", "State", "District", "Block",
                                        "Village","Village","Copper - Sufficient","Copper - Deficient",
                                        "Boron - Sufficient","Boron - Deficient",
                                        "S - Sufficient","S - Deficient",
                                        "Fe - Sufficient","Fe - Deficient",
                                        "Zn - Sufficient","Zn - Deficient",
                                        "Mn - Sufficient","Mn - Deficient"])
                        writer.writerows(all_data)

                    print(f"Saved to {file_path}")


except Exception as e:
    print(f"ERROR: {e}")
finally:
    driver.quit()

