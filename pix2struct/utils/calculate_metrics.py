import argparse
import os
import json
from tqdm import tqdm
from tree_distance import calculate_ted, extract_html_tree
from skimage.metrics import structural_similarity as ssim
import cv2
from matplotlib.figure import Figure
import numpy as np
from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
from nltk import edit_distance
from bs4 import BeautifulSoup
from zss import Node

import multiprocessing
from itertools import product

import time

def remove_texts(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
        
    for text_node in soup.find_all(text=True):
        text_node.replace_with(" ")
    return str(soup)


def calculate_ssim_index(folder, imageA_path, imageB_path, index_sample):
    imageA = cv2.imread(imageA_path)
    imageB = cv2.imread(imageB_path)

    imageB = cv2.resize(imageB, (imageA.shape[1], imageA.shape[0]))

    imageA_gray = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    imageB_gray = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    ssim_index, gradient, ssim_map = ssim(imageA_gray, imageB_gray, full=True, gradient=True)


    # Create a figure for the SSIM map
    fig_ssim = Figure(figsize=(6, 6))
    ax_ssim = fig_ssim.add_subplot(1, 1, 1)
    ax_ssim.imshow(ssim_map, cmap='Blues', vmin=-1, vmax=1)
    ax_ssim.set_title("SSIM map")
    fig_ssim.colorbar(ax_ssim.imshow(ssim_map, cmap="Blues", vmin=-1, vmax=1), ax=ax_ssim)
    fig_ssim.savefig(f"{folder}{index_sample}_ssim_map.png")

    # Create a figure for the gradient map
    gradient_magnitude = np.sqrt(np.square(gradient))
    fig_gradient = Figure(figsize=(6, 6))
    ax_gradient = fig_gradient.add_subplot(1, 1, 1)
    ax_gradient.imshow(gradient_magnitude, cmap="Blues")
    ax_gradient.set_title("Gradient map")
    fig_gradient.colorbar(ax_gradient.imshow(gradient_magnitude, cmap="Blues"), ax=ax_gradient)
    fig_gradient.savefig(f"{folder}{index_sample}_gradient_map.png")

    return ssim_index


def calculate_metric(args):
    json_file, folder, pix2codeOriginal, rico, ui2code, webUI2code = args

    with open(folder + json_file, "r") as fr:
        json_dict = json.load(fr)

    if pix2codeOriginal:
        answer_raw_file_path = folder + json_file.replace(".json", "_answer.gui")
        prediction_raw_file_path = folder + json_file.replace(".json", "_pred.gui")
    elif rico or ui2code:
        answer_raw_file_path = folder + json_file.replace(".json", "_answer.txt")
        prediction_raw_file_path = folder + json_file.replace(".json", "_pred.txt")
    elif webUI2code:
        answer_raw_file_path = folder + json_file.replace(".json", "_answer.txt")
        prediction_raw_file_path = folder + json_file.replace(".json", "_pred.txt")
        answer_file_path = folder + json_file.replace(".json", "_answer_separated_processed.html")
        prediction_file_path = folder + json_file.replace(".json", "_pred_separated_processed.html")
    else:
        answer_raw_file_path = folder + json_file.replace(".json", "_answer.txt")
        prediction_raw_file_path = folder + json_file.replace(".json", "_pred.txt")
        answer_file_path = folder + json_file.replace(".json", "_answer_processed.html")
        prediction_file_path = folder + json_file.replace(".json", "_pred_processed.html")

    with open(prediction_raw_file_path, 'r') as f:
        pred_raw = f.read()

    with open(answer_raw_file_path, 'r') as f:
        answer_raw = f.read()

   
    if pix2codeOriginal or rico or ui2code:
        pred = pred_raw
        answer = answer_raw
    else: 
        with open(prediction_file_path, 'r') as f:
            pred = f.read()
            pred_html = extract_html_tree(pred)

        with open(answer_file_path, 'r') as f:
            answer = f.read()
            answer_html = extract_html_tree(answer)


    # Normalized Edit Distance
    ed_score = edit_distance(pred_raw, answer_raw)
    normalized_ed_score = ed_score / max(len(pred_raw), len(answer_raw))
    
    # Bleu Score
    bleu_score = corpus_bleu([[answer_raw]], [pred_raw], smoothing_function=SmoothingFunction().method4)

    if not pix2codeOriginal and not rico and not ui2code:

        # HTML Tree edit distance
        ted, normalized_ted = calculate_ted(answer_html, pred_html)

        # Structural Bleu Score
        answer_no_texts = remove_texts(answer_raw)
        pred_no_texts = remove_texts(pred_raw)
        str_bleu_score = corpus_bleu([[answer_no_texts]], [pred_no_texts], smoothing_function=SmoothingFunction().method4)

        # Structural visual similarity
        if webUI2code:
            answer_png_file_path = folder + json_file.replace(".json", "_answer_separated_processed.png")
            prediction_png_file_path = folder + json_file.replace(".json", "_pred_separated_processed.png")
        else:
            answer_png_file_path = folder + json_file.replace(".json", "_answer_processed.png")
            prediction_png_file_path = folder + json_file.replace(".json", "_pred_processed.png")

        if os.path.exists(answer_png_file_path) and os.path.exists(prediction_png_file_path):
            ssim_index = calculate_ssim_index(folder, answer_png_file_path, prediction_png_file_path, json_file.split(".")[0])
        else:
            ssim_index = None
 
    elif pix2codeOriginal:
        # Structural visual similarity
        answer_png_file_path = folder + json_file.replace(".json", "_answer.png")
        prediction_png_file_path = folder + json_file.replace(".json", "_pred.png")

        if os.path.exists(answer_png_file_path) and os.path.exists(prediction_png_file_path):
            ssim_index = calculate_ssim_index(folder, answer_png_file_path, prediction_png_file_path, json_file.split(".")[0])
        else:
            ssim_index = None

        str_bleu_score = -1
        ted = -1
        normalized_ted = -1

    elif rico or ui2code:
        str_bleu_score = -1
        ted = -1
        normalized_ted = -1
        ssim_index = -1


    json_dict["len_pred"] = len(pred) 
    json_dict["len_answer"] = len(answer) 
    json_dict["max_len"] = max(len(pred), len(answer))
    json_dict["bleu"] = bleu_score
    json_dict["ed"] = ed_score 
    json_dict["n_ed"] = normalized_ed_score
    if not rico and not ui2code:
        if ssim_index:
            json_dict["ssim_index"] = ssim_index 

    if not pix2codeOriginal and not rico and not ui2code:
        json_dict["s_bleu"] = str_bleu_score
        json_dict["ted"] = ted
        json_dict["n_ted"] = normalized_ted

    with open(folder + json_file, "w") as fw:
        json.dump(json_dict, fw, indent=2)      
    
    return ted, ssim_index, ed_score, bleu_score, str_bleu_score
    
if __name__ == "__main__":
    folder = "results/demo"

    # Initialize args parser
    parser = argparse.ArgumentParser(description="Calculate metrics for predictions",
                                     usage="python3 calculate_metrics.py --folder {folder}")
    parser.add_argument("--folder",
                        help="Folder with files to calculate metrics")

    parser.add_argument("--pix2codeOriginal", action='store_true',
                        help="Specifies if it is the original experiment on pix2code, with guis and not html files")

    parser.add_argument("--rico", action='store_true',
                        help="Specifies if it is the rico dataset")

    parser.add_argument("--ui2code", action='store_true',
                        help="Specifies if it is the ui2code dataset")

    parser.add_argument("--webUI2code", action='store_true',
                        help="Specifies if it is the ui2code dataset")

    # Read args
    args = parser.parse_args()

    if args.folder:
        folder = args.folder
        if not folder.endswith("/"):
            folder = folder + "/"

    if args.rico or args.ui2code:
        files = [file for file in os.listdir(folder) if file.endswith('_pred.txt')]
        for filename in files:
            dict_tmp = {}
            with open(os.path.join(folder, filename.split("_pred.txt")[0] + ".json"), "w") as f:
                json.dump(dict_tmp, f, indent=2)

    json_files= [file for file in os.listdir(folder) if file.endswith('.json') if not file.endswith("_answer.json")]
    print(f"Number of files: {len(json_files)}")
    start = time.time()
    pool_size = multiprocessing.cpu_count()

    with multiprocessing.Pool(processes=pool_size) as pool:
        results = []
        for result in tqdm(pool.imap_unordered(func=calculate_metric, iterable=[(filename, folder, args.pix2codeOriginal, args.rico, args.ui2code, args.webUI2code) for filename in json_files]), total=len(json_files)):
            results.append(result)

    teds, ssims, eds, bleus, s_bleus = zip(*results)


    avg_ed = np.mean(eds)
    print(f"   Avg Edit Distance = {avg_ed:.3f}")

    avg_bleu = np.mean(bleus)
    print(f"             Avg Bleu Score = {avg_bleu:.3f}")

    if not args.pix2codeOriginal and not args.rico:
        avg_ted = np.mean(teds)
        avg_s_bleu = np.mean(s_bleus)
        print(f"Avg HTML Tree Edit Distance = {avg_ted:.3f}")

    if not args.rico and not args.ui2code:
        filtered_ssims = [x for x in ssims if x is not None]
        avg_ssim_index = np.mean(filtered_ssims)
        print(f"             Avg SSIM index = {avg_ssim_index:.3f}")
    
    print(f"/nExecution time: {time.time() - start}")
    


