import glob
import os
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as expected_conditions
from selenium.webdriver.common.by import By
from .ColorManager import ColorManager
import fnmatch
import json
import time
from tqdm import tqdm


class ScreenShutter:
    


    def __init__(self, full_screenshot: bool = False, window_size: tuple = (1024,1), 
        output_path:str = "./output/", 
        input_path:str = "./output/html/", 
        assets_path:str = "./Assets/",
        show_progress: bool = True, 
        driver_path=""):


        self.full_screenshot = full_screenshot
        self.window_size = window_size
        self.input_path = input_path
        self.output_path = output_path
        self.assets_path = assets_path
        self.show_progress = show_progress
        self.driver_path = driver_path

    def capture_and_save(self, max_shoots=100000):



        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Full absolute path
        options.binary_location = os.path.abspath("chrome-linux64/chrome")
        print("Using Chrome binary at:", options.binary_location)
        
        driver = webdriver.Chrome(service=Service(self.driver_path), options=options)
        
        
        
        
        #print("Generating Screenshots...")
        # get a list of all the files to open
        window_width = self.window_size[0]
        window_height = self.window_size[1]
        glob_folder = os.path.join(os.getcwd(), self.input_path+'*.html')
        
        files_count = len(fnmatch.filter(os.listdir(self.input_path), '*.html'))
        
        html_file_list = glob.glob(glob_folder)
        
        # options = webdriver.ChromeOptions()
        # options.headless = True 
        # options.binary_location = os.path.abspath('chrome-linux64/chrome')
        
        
        
        tic = time.time()
        count = 0 
        
        scripts = {"labeler":"", "prepare_shutting":"", "bridge_metadata":""}
        
        with open(self.assets_path+"prepare_shutting.js", "r") as f:
            
            scripts["prepare_shutting"] = f.read()
        with open(self.assets_path+"extract_meta.js", "r") as f:
            scripts["extract_meta"] = f.read()
        
        files_with_problems = [
        "/Users/giuseppesalvi/Desktop/Tesi/tools/webUI2code-experiments/results/synthBootstrap/synthBootstrap_mini/rw_863_pred_processed.html",
        "/Users/giuseppesalvi/Desktop/Tesi/tools/webUI2code-experiments/results/synthBootstrap/synthBootstrap_mini/rw_28_pred_processed.html",
        "/Users/giuseppesalvi/Desktop/Tesi/tools/webUI2code-experiments/results/synthBootstrap/synthBootstrap_mini/rw_395_pred_processed.html",
        "/Users/giuseppesalvi/Desktop/Tesi/tools/webUI2code-experiments/results/synthBootstrap/synthBootstrap_mini/rw_787_pred_processed.html"
        ]
        for html_file in tqdm(html_file_list):
            
            if os.path.isfile(self.output_path + os.path.basename(html_file)[:-5] + '.png'):
                count += 1           
                continue
            
            driver.set_window_size(window_width, window_height)
            
            if count > max_shoots:
                break
            else:
                count += 1
            if self.show_progress:
                progress = round(count/files_count, 2)*100
                print("{0}/{1} files generated [{2}%]".format(count,files_count,progress))
            
            # get the name into the right format
            temp_name = "file://" + html_file
            
            # open in webpage
            driver.get(temp_name)
            save_name = os.path.basename(temp_name)[:-5] + '.png'       
            
            #script execution only to get palette
            driver.execute_script(scripts["extract_meta"])
            palette = driver.execute_script("return window.palette;")
            
           
####
            if palette is not None and isinstance(palette, str):
                # try:
                    palette = json.loads(palette)
                # except json.JSONDecodeError as e:
                #     print(f"❌ JSON decode failed: {e}")
                #     print("Returned palette:", palette)
                #     palette = None
                    

####

                 # if palette is not None:
                
                    
                    ColorManager.compile_color(primary=palette["primary"], secondary=palette["secondary"], light=palette["light"], 
                    dark=palette["dark"], enable_gradients=palette["enable-gradients"], output_path=self.output_path, assets_path=self.assets_path)
                    driver.execute_script("window.location.reload();")
        
            w = 0
            h = 0 
            while h < 10000 and not (w==driver.execute_script('return document.body.parentNode.scrollWidth') and h==driver.execute_script('return document.body.parentNode.scrollHeight')):
                w = driver.execute_script('return document.body.parentNode.scrollWidth')
                h = driver.execute_script('return document.body.parentNode.scrollHeight')
                driver.set_window_size(w, h)
        
        # Set to new window size
            driver.execute_script("window.screenshotHeight = "+str(h)+";")
            driver.execute_script(scripts["prepare_shutting"])
            
            # Obtain screenshot of page within body tag
            driver.find_element(By.TAG_NAME, "html").screenshot(self.input_path+save_name)
        
        tac = time.time()
        print("Generated {0} PNG files in {1} seconds. Files are in {2}.".format(count,round(tac-tic, 1),self.output_path))