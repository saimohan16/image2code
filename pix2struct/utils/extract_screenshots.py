import argparse
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webgenerator.ScreenShutter import ScreenShutter

WAIT_SCREENSHOT = 0
CLUSTER = False 
COLAB = False

#CHROME_DRIVER_PATH = './chromedriver/linux-116.0.5793.0/chromedriver-linux64/chromedriver'
CHROME_PATH = 'chrome-linux64/chrome'

CHROME_DRIVER_PATH = 'local/chromedriver_linux/chromedriver'
ASSETS_PATH = "utils/webgenerator/Assets/"


def get_screenshot(html_file_path):
    """ Get Screenshot of website URL passed as argument, and save it """

    print("\nGenerating the screenshot ...")
    # Set webdriver options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,1024')
    
    options.binary_location = os.path.abspath('chrome-linux64/chrome')
    # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")


    # if CLUSTER:
    #     options.binary_location = CHROME_PATH
    # if COLAB or CLUSTER:
    #     options.add_argument('--no-sandbox')
    #     options.add_argument('--disable-dev-shm-usage')

    # Set window size
    options.add_argument("--window-size=1280,1024")

    # Start web browser
    if COLAB:
        driver = webdriver.Chrome('chromedriver', options=options)
    else:
        driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)

    # Launch URL
    driver.get("file://" + os.path.abspath(html_file_path))

    # Wait some time to allow popups to show
    driver.implicitly_wait(WAIT_SCREENSHOT)

    # Obtain browser height and width
    w = driver.execute_script('return document.body.parentNode.scrollWidth')
    h = driver.execute_script('return document.body.parentNode.scrollHeight')

    # Set to new window size
    driver.set_window_size(w, h)

    # Obtain screenshot of page within body tag
    driver.find_element(By.TAG_NAME, "body").screenshot(html_file_path.replace(".html", ".png"))

    # Close web driver
    driver.close()

def extract_screenshots(folder, isWebGenerator=False):
    if isWebGenerator:
        css_folder_path = "/".join(folder.split("/")[0:-2]) + "/"
        print("css_folder_path: ", css_folder_path)
        screen_shutter = ScreenShutter(full_screenshot=False, show_progress=False, input_path=folder,
                                    output_path=css_folder_path, assets_path=ASSETS_PATH, driver_path=CHROME_DRIVER_PATH)
        screen_shutter.capture_and_save()
    else:
        list_files = os.listdir(folder)
        filtered_files = [file for file in list_files if file.endswith('.html') and not file.endswith("separated.html")]

        # Iterate through all files in the given folder
        for filename in tqdm(filtered_files):
            try: 
                if filename.endswith('.html'):
                    if not os.path.exists(folder + filename.replace(".html", ".png")):
                            get_screenshot(os.path.join(folder, filename))
            except Exception as e:
                print("Exception found for file: ", filename)
                print(e)


if __name__ == "__main__":
    folder = "demo"

    # Initialize args parser
    parser = argparse.ArgumentParser(description="Extract screenshots from html files inside a local folder",
                                     usage="python3 extract_screenshots.py --folder {folder}")
    parser.add_argument("--folder",
                        help="Folder with html files to extract screenshots from")

    parser.add_argument("--webGenerator", action='store_true',
                        help="Specifies if we are extracting screenshots using webGenerator screenshotter")
    # Read args
    args = parser.parse_args()

    if args.folder:
        folder = args.folder
        if not folder.endswith("/"):
            folder = folder + "/"

    extract_screenshots(folder, args.webGenerator)
