# backend/pdf_parser.py

import fitz  # PyMuPDF
import os
import re

def parse_pdf(pdf_path, image_output_dir="static/images"):
    doc = fitz.open(pdf_path)
    all_text = []
    image_info = []

    os.makedirs(image_output_dir, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        all_text.append({
            "page": page_num + 1,
            "text": text.strip()
        })

        # 匹配图像描述（如 Figure 2: This is a dog...）
        figure_captions = []
        pattern = re.compile(r'(Figure\s*\d+)\s*[:：. ]+(.*?)(?=\n[A-Z]|$)', re.IGNORECASE | re.DOTALL)
        matches = pattern.findall(text)
        for match in matches:
            figure_captions.append({
                "figure_id": match[0].strip(),        # Figure 2
                "caption": match[1].strip(),          # caption text
                "page": page_num + 1
            })
        print("📌 当前页图注信息 figure_captions:", figure_captions)  # ← 加在这里
        # 提取图像
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.n > 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            image_filename = f"page{page_num+1}_img{img_index+1}.png"
            image_path = os.path.join(image_output_dir, image_filename)
            pix.save(image_path)

            # 如果有图注，则匹配给当前图像（一个简单策略：一页一图一注，后续可更细）
            caption_data = figure_captions[0] if len(figure_captions) > 0 else {}

            image_info.append({
                "page": page_num + 1,
                "image_file": image_filename,
                "path": image_path,
                "figure_id": caption_data.get("figure_id", None),
                "caption": caption_data.get("caption", None)
            })

    return all_text, image_info
