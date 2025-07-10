# backend/qa_engine.py

import numpy as np
import re
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from llm.qwen_client import call_qwen_plus  # ✅ 统一使用新版模型调用


def retrieve_relevant_context(question, pages_text, top_k=3):
    """
    输入问题和PDF页面文字，返回与问题最相关的前k页段落
    """
    texts = [page["text"] for page in pages_text]
    pages = [page["page"] for page in pages_text]

    vectorizer = TfidfVectorizer().fit(texts + [question])
    doc_vectors = vectorizer.transform(texts)
    question_vector = vectorizer.transform([question])

    sim_scores = cosine_similarity(question_vector, doc_vectors).flatten()
    top_k_indices = np.argsort(sim_scores)[-top_k:][::-1]

    results = []
    for idx in top_k_indices:
        # ⏬ 限制每段最多500字符
        short_text = texts[idx][:500] + ("..." if len(texts[idx]) > 500 else "")
        results.append({
            "page": pages[idx],
            "text": short_text
        })
    return results


def answer_question(question, context_blocks):
    """
    构造 prompt 调用 Qwen 回答文本问题，并要求引用依据
    """
    context_str = "\n".join([f"[Page {c['page']}]\n{c['text']}" for c in context_blocks])
    prompt = f"""You are an academic assistant. Based on the following paper content, answer the user's question.

Document content:
{context_str}

Your task:
1. Answer the user's question in an academic tone.
2. Clearly cite the supporting evidence using page numbers.
3. Format your final answer like:

Answer:
[Your answer here]

Evidence:
- Page X: "..." (short quote)
- Page Y: "..." (short quote)

Question:
{question}
"""

    return call_qwen_plus(prompt)


def is_figure_question(question):
    """
    判断用户是否在问“Figure X” 或 “图X”
    """
    return bool(re.search(r'(figure|图)\s*\d+', question, re.IGNORECASE))


def handle_figure_question(question, image_info):
    """
    处理图像类问题：提取图像 + 图注 + 调用 Qwen 回答
    """
    match = re.search(r'(figure|图)\s*(\d+)', question, re.IGNORECASE)
    if not match:
        return {"error": "无法识别图像编号"}

    fig_id = f"Figure {match.group(2)}"

    for image in image_info:
        if (image.get("figure_id") or "").lower() == fig_id.lower():
            with open(image["path"], "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

            caption = image.get("caption", "")
            prompt = f"""你是一名论文阅读助手。根据图像说明（图注）内容，回答用户的问题。

图像说明:
{caption}

用户问题:
{question}

请用学术风格回答，并尽可能引用图注内容："""

            answer = call_qwen_plus(prompt)

            return {
                "image_base64": image_base64,
                "image_file": image["image_file"],
                "figure_id": fig_id,
                "caption": caption,
                "answer": answer
            }

    return {"error": f"未找到图像编号 {fig_id}"}
