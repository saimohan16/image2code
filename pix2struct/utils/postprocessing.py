import subprocess
import argparse
import os
import json
from tqdm import tqdm
import re
from bs4 import BeautifulSoup

def clean_html_gaps(html_str):
    html_str = re.sub(r'hre\s+f=', 'href=', html_str)
    html_str = re.sub(r'sr\s+c=', 'src=', html_str)
    html_str = re.sub(r're\s+l=', 'rel=', html_str)
    html_str = re.sub(r'class\s+=', 'class=', html_str)
    html_str = re.sub(r'st\s+yle=', 'style=', html_str)
    html_str = re.sub(r'>\s+<', '><', html_str)
    return html_str


def extract_html_file_from_gui(folder_path, file_path):
    subprocess.call(['python3', 'utils/pix2code/compiler/web-compiler.py', os.path.join(folder_path, file_path)])

    return

def process_Pix2Code_html_file(folder, input_file_name, output_file_name):
    with open(folder + input_file_name, "r") as f:
        content = f.read()

    #content_with_spaces_fixed = fix_html_spaces(content)
    content_with_header = content.replace(
        '<html>', '<html> <header> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous"> <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous"> <style> .header{margin:20px 0}nav ul.nav-pills li{background-color:#333;border-radius:4px;margin-right:10px}.col-lg-3{width:24%;margin-right:1.333333%}.col-lg-6{width:49%;margin-right:2%}.col-lg-12,.col-lg-3,.col-lg-6{margin-bottom:20px;border-radius:6px;background-color:#f5f5f5;padding:20px}.row .col-lg-3:last-child,.row .col-lg-6:last-child{margin-right:0}footer{padding:20px 0;text-align:center;border-top:1px solid #bbb} </style> <title>Scaffold</title> </header>')
    content_with_footer_and_scripts = content_with_header.replace('</main>', '<footer class="footer"> <p>&copy; Tony Beltramelli 2017</p> </footer> </main> <script src="js/jquery.min.js"></script> <script src="js/bootstrap.min.js"></script>')

    with open(folder + output_file_name, "w") as f:
        f.write(content_with_footer_and_scripts)
    return


def process_Pix2Code_gui_file(folder, input_file_name, output_file_name):
    with open(folder + input_file_name, "r") as f:
        content = f.read()

    content_with_newlines = content.replace("{ ","{ \n").replace(" }"," \n}\n")
    with open(folder + output_file_name, "w") as f:
        f.write(content_with_newlines)
    return



def process_Pix2Code_html_file(folder, input_file_name, output_file_name):
    with open(folder + input_file_name, "r") as f:
        content = f.read()

    #content_with_spaces_fixed = fix_html_spaces(content)
    content_with_header = content.replace(
        '<html>', '<html> <header> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous"> <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous"> <style> .header{margin:20px 0}nav ul.nav-pills li{background-color:#333;border-radius:4px;margin-right:10px}.col-lg-3{width:24%;margin-right:1.333333%}.col-lg-6{width:49%;margin-right:2%}.col-lg-12,.col-lg-3,.col-lg-6{margin-bottom:20px;border-radius:6px;background-color:#f5f5f5;padding:20px}.row .col-lg-3:last-child,.row .col-lg-6:last-child{margin-right:0}footer{padding:20px 0;text-align:center;border-top:1px solid #bbb} </style> <title>Scaffold</title> </header>')
    content_with_footer_and_scripts = content_with_header.replace('</main>', '<footer class="footer"> <p>&copy; Tony Beltramelli 2017</p> </footer> </main> <script src="js/jquery.min.js"></script> <script src="js/bootstrap.min.js"></script>')

    with open(folder + output_file_name, "w") as f:
        f.write(content_with_footer_and_scripts)
    return


def separate_WebUI2Code_html_css_files(folder, txt_file, output_html_file_name, output_css_file_name):
    token_not_found = False
    title_not_found = False
    with open(folder + txt_file, "r") as f:
        content = f.read()

    if "/* START CSS */" not in content:
        token_not_found = True
        html_content = content 
        css_content = ""
    else: 
        parts = content.split("/* START CSS */")
        html_content = parts[0]
        css_content = parts[1]

    # Make sure to reference the stylesheet correctly inside the html file after the title tag

    # TODO: Handle cases where the title token is missing
    if "</title>" not in content:
        title_not_found = True
    else:
        html_content = html_content.replace('</title>', '</title> <link href="{fname}" rel="stylesheet"/>'.format(fname=output_css_file_name), 1)


    with open(folder + output_html_file_name, "w") as f:
        f.write(html_content)

    with open(folder + output_css_file_name, "w") as f:
        f.write(css_content)

    return token_not_found, title_not_found


def process_files(folder, suffix=".txt", isPix2Code=False, isWebUI2Code=False):
    files_paths = [file for file in os.listdir(folder) if file.endswith(suffix)]
    for file_path in tqdm(files_paths):
        if file_path.endswith("_processed" + suffix) or file_path.endswith("_complete" + suffix) or file_path.endswith("_separated" + suffix):
            # Already processed
            continue


        if isPix2Code:
            if suffix == ".gui":
                output_file_path = file_path.split(suffix)[0] + "_processed.gui"
                process_Pix2Code_gui_file(folder, file_path, output_file_path)
                extract_html_file_from_gui(folder, output_file_path)

            else:
                output_file_path = file_path.split(suffix)[0] + "_processed.html"
                process_Pix2Code_html_file(
                    folder, file_path, output_file_path)

            if file_path.endswith("pred" + suffix):
                dict_tmp = {}
                with open(folder + file_path.split("_pred")[0] + ".json", "w") as f:
                    json.dump(dict_tmp, f, indent=2)

        elif isWebUI2Code:
            output_html_file_name = file_path.split(
                suffix)[0] + "_separated.html"
            output_css_file_name = file_path.split(
                suffix)[0] + "_separated.css"
            token_not_found, title_not_found = separate_WebUI2Code_html_css_files(
                folder, file_path, output_html_file_name, output_css_file_name)
            output_file_path = output_html_file_name.split(".html")[0] + "_processed.html"
            errors_from_tidy = process_html(
                folder + output_html_file_name, folder + output_file_path)

            if file_path.endswith("pred" + suffix):
                dict_tmp = {}
                with open(folder + file_path.split("_pred")[0] + ".json", "w") as f:
                    dict_tmp["errors"] = cleanup_errors_from_tidy(errors_from_tidy)
                    dict_tmp["token_not_found"] = token_not_found
                    dict_tmp["title_not_found"] = title_not_found
                    json.dump(dict_tmp, f, indent=2)
            else:
                dict_tmp = {}
                with open(folder + file_path.split("_answer")[0] + "_answer.json", "w") as f:
                    dict_tmp["errors"] = cleanup_errors_from_tidy(errors_from_tidy)
                    dict_tmp["token_not_found"] = token_not_found
                    dict_tmp["title_not_found"] = title_not_found
                    json.dump(dict_tmp, f, indent=2)
            

        else:
            output_file_path = file_path.split(suffix)[0] + "_processed.html"
            errors_from_tidy = process_html(
                folder + file_path, folder + output_file_path)
            if file_path.endswith("pred" + suffix):
                dict_tmp = {}
                with open(folder + file_path.split("_pred")[0] + ".json", "w") as f:
                    dict_tmp["errors"] = cleanup_errors_from_tidy(errors_from_tidy)
                    json.dump(dict_tmp, f, indent=2)



def process_html(input_file_path, output_file_path):
    with open(input_file_path, "r") as f:
        raw_html = f.read()

    cleaned = clean_html_gaps(raw_html)
    soup = BeautifulSoup(cleaned, "html.parser")
    prettified = soup.prettify()

    with open(output_file_path, "w") as f:
        f.write(prettified)

    # Optionally still run tidy for validation
    command = f"tidy -indent -wrap 0 --drop-empty-elements no {output_file_path}"
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    errors = result.stderr.decode()

    return errors



def cleanup_errors_from_tidy(errors_original):
    lines = errors_original.splitlines()
    errors = []
    for line in lines:
        if line.startswith("Info"):
            break
        try:
            position = line.split("-")[0].rstrip()
            error_type = line.split("-")[1].split(":")[0].strip()
            error_message = line.split("-")[1].split(":")[1].lstrip()
            error = {}
            error["position"] = position
            error["error_type"] = error_type
            error["error_message"] = error_message
            errors.append(error)
        except Exception:
            errors.append(line)

    return errors


if __name__ == "__main__":
    folder = "demo"

    # Initialize args parser
    parser = argparse.ArgumentParser(description="post-processing of predictions and answers with correction of syntax errors",
                                     usage="python3 postprocessing.py --folder {folder}")
    parser.add_argument("--folder", help="Folder with files to process")
    parser.add_argument("--suffix", help="Suffix of files to process")
    parser.add_argument("--pix2code", action='store_true',
                        help="Specifies if we are preprocessing the results of Pix2Code experiment, which need particular postprocessing")
    parser.add_argument("--webui2code", action='store_true',
                        help="Specifies if we are preprocessing the results of WebUI2Code experiment, which need particular postprocessing")

    # Read args
    args = parser.parse_args()

    if args.folder:
        folder = args.folder
        if not folder.endswith("/"):
            folder = folder + "/"

    if args.suffix:
        suffix = args.suffix

    process_files(folder,  suffix=suffix, isPix2Code=args.pix2code, isWebUI2Code=args.webui2code)
