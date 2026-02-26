import streamlit as st
from pypdf import PdfReader
from pptx import Presentation
import dashscope
import os

# ==========================
# 获取 API Key（Streamlit Secrets）
# ==========================
# 在 Streamlit Cloud: Settings → Secrets
# 添加一行：DASHSCOPE_API_KEY=你的通义千问API_KEY
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")

# 页面配置
st.set_page_config(
    page_title="商业计划书AI分析助手",
    page_icon="📊",
    layout="wide"
)

# 标题和说明
st.title("📊 商业计划书 AI 分析助手")
st.markdown("---")
st.markdown("""
### 使用说明
1. 在左侧上传您的商业计划书（支持 PDF 或 PPT 格式）
2. 点击"开始分析"按钮
3. 等待 AI 生成专业的分析报告

**注意**: 首次使用需要在侧边栏输入通义千问 API Key
""")

# 侧边栏 - API Key 输入
with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input(
        "通义千问 API Key",
        type="password",
        help="请输入您的通义千问 API Key。获取地址: https://dashscope.aliyun.com/"
    )
    
    st.markdown("---")
    st.markdown("""
    ### 如何获取 API Key？
    1. 访问 [通义千问控制台](https://dashscope.aliyun.com/)
    2. 登录/注册阿里云账号
    3. 进入 API-KEY 管理页面
    4. 创建新的 API Key
    5. 复制并粘贴到上方输入框
    """)

# 主界面 - 文件上传
st.header("📁 上传商业计划书")
uploaded_file = st.file_uploader(
    "选择文件",
    type=['pdf', 'ppt', 'pptx'],
    help="支持 PDF 和 PowerPoint 格式"
)

# ==========================
# 读取 PDF
# ==========================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ==========================
# 读取 PPT
# ==========================
def read_ppt(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text

# ==========================
# 点击分析按钮
# ==========================
if uploaded_file:
    # 判断文件类型
    if uploaded_file.name.endswith(".pdf"):
        bp_text = read_pdf(uploaded_file)
    else:
        bp_text = read_ppt(uploaded_file)

    st.success("文件读取成功！")

    if st.button("开始分析"):
        # ==========================
        # Prompt 模板
        # ==========================
        prompt = f"""
你是一个项目评价助手。

请严格分析以下商业计划书，并按模块输出分析结果：
- 产品技术
- 市场
- 行业竞争情况
- 核心团队构成
- 财务指标
- 公司架构合规情况
- 融资规模及资金用途

禁止输出融资建议或融资规模建议。

商业计划书内容：
{bp_text}
"""

        # ==========================
        # 调用通义千问
        # ==========================
        with st.spinner("分析中...请稍等"):
            try:
                response = dashscope.Generation.call(
                    model="qwen-max",
                    prompt=prompt
                )
                result = response.output.text
            except Exception as e:
                st.error(f"分析失败: {e}")
                result = ""

        # ==========================
        # 显示分析结果
        # ==========================
        if result:
            st.subheader("分析结果")
            st.write(result)
</div>
""", unsafe_allow_html=True)
