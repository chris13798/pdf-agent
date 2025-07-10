# llm/qwen_client.py

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def call_qwen_plus(prompt, system_prompt="You are a helpful academic assistant."):
    """
    通用 Qwen 文本问答调用接口
    """
    try:
        response = client.chat.completions.create(
            model="qwen-plus",  # 可修改为 qwen-max 等更强模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error] Qwen API call failed: {e}"
