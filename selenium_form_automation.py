from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get("https://demoqa.com/automation-practice-form")

# Remove all iframes (ads) that might block clicks
driver.execute_script("""
    var iframes = document.getElementsByTagName('iframe');
    while(iframes.length > 0) {
        iframes[0].parentNode.removeChild(iframes[0]);
    }
""")

# Close fixed banner if exists
try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "close-fixedban"))
    ).click()
except:
    pass

# Fill in basic details
driver.find_element(By.ID, "firstName").send_keys("Omkar")
driver.find_element(By.ID, "lastName").send_keys("Sanas")
driver.find_element(By.ID, "userEmail").send_keys("omkar@example.com")

# Handle gender click with scroll and fallback
gender_male = driver.find_element(By.XPATH, "//label[text()='Male']")
driver.execute_script("arguments[0].scrollIntoView(true);", gender_male)
time.sleep(1)
try:
    gender_male.click()
except:
    # If label click blocked, click the actual radio input
    driver.find_element(By.ID, "gender-radio-1").click()

# Mobile number
driver.find_element(By.ID, "userNumber").send_keys("9876543210")

# Date of Birth - scroll into view and click
dob_input = driver.find_element(By.ID, "dateOfBirthInput")
driver.execute_script("arguments[0].scrollIntoView(true);", dob_input)
time.sleep(1)
dob_input.click()

# Select year, month, day
driver.find_element(By.CLASS_NAME, "react-datepicker__year-select").send_keys("2000")
driver.find_element(By.CLASS_NAME, "react-datepicker__month-select").send_keys("May")
driver.find_element(By.XPATH, "//div[contains(@class,'react-datepicker__day--015') and not(contains(@class,'react-datepicker__day--outside-month'))]").click()

# Subject
subject = driver.find_element(By.ID, "subjectsInput")
subject.send_keys("Maths")
subject.send_keys("\n")

# Scroll down to hobbies
driver.execute_script("window.scrollBy(0, 300)")

# Hobbies - scroll and click
reading_checkbox = driver.find_element(By.XPATH, "//label[text()='Reading']")
driver.execute_script("arguments[0].scrollIntoView(true);", reading_checkbox)
reading_checkbox.click()

# Upload Picture - using your specified path
driver.find_element(By.ID, "uploadPicture").send_keys(r"C:\Users\Omkar\Pictures\sample.jpg")

# Current Address
driver.find_element(By.ID, "currentAddress").send_keys("123, Pune, Maharashtra")

# Scroll down to state and city dropdowns
driver.execute_script("window.scrollBy(0, 300)")

# Select State and City using inputs and Enter key
state = driver.find_element(By.ID, "react-select-3-input")
state.send_keys("NCR\n")

city = driver.find_element(By.ID, "react-select-4-input")
city.send_keys("Delhi\n")

# Submit the form
driver.find_element(By.ID, "submit").click()

# Wait to observe submission
time.sleep(3)

# Close browser
driver.quit()
