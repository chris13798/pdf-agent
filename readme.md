# 📄 PDF Agent


该系统支持用户上传英文 PDF 文献，自动提取文字与图像信息，并提供自然语言问答、图像问答、原文依据展示等功能，提升用户对学术文献的理解效率。

---

## 💡 项目功能简介

- ✅ 上传英文 PDF 文献，自动提取文本与图像
- ✅ 支持自然语言提问（如“本文提出了什么方法？”）
- ✅ 支持图像问答（如“图2展示了什么？”或截图粘贴）
- ✅ 返回结构化回答 + 原文依据（如“第 7 页第 2 段”或“图 Figure 3”）

---

## 🚀 运行方式

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/pdf-agent.git
cd pdf-agent

2. 创建虚拟环境
bash
conda create -n pdfagent python=3.10
conda activate pdfagent

3. 安装依赖
bash
pip install -r requirements.txt

4. 设置 API Key（阿里云 DashScope）
bash
export DASHSCOPE_API_KEY=你的API密钥

5. 启动服务
bash
python app.py
浏览器访问 http://127.0.0.1:5000 即可使用。

