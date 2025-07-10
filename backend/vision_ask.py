# backend/vision_ask.py

import os
import base64
from dashscope import MultiModalConversation


def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')


def ask_qwen_vl_sdk(image_base64, question):
    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"data:image/png;base64,{image_base64}"},
                {"text": question}
            ]
        }
    ]

    try:
        response = MultiModalConversation.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen-vl-max-latest",
            messages=messages
        )
        return response.output.choices[0].message.content[0]["text"]
    except Exception as e:
        return f"[SDK Error]: {str(e)}"
