import streamlit as st
import os
from pathlib import Path
import PyPDF2
from pptx import Presentation
from openai import OpenAI

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

# 提取 PDF 文本
def extract_pdf_text(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"PDF 读取失败: {str(e)}")
        return None

# 提取 PPT 文本
def extract_ppt_text(file):
    try:
        # 保存临时文件
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        
        # 读取PPT
        prs = Presentation(temp_path)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        
        # 删除临时文件
        os.remove(temp_path)
        return text
    except Exception as e:
        st.error(f"PPT 读取失败: {str(e)}")
        return None

# 调用通义千问API分析
def analyze_with_qwen(text, api_key):
    try:
        # 初始化客户端 - 修复：不传入任何额外参数
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 构建提示词
        prompt = f"""你是一位资深的风险投资分析师。请对以下商业计划书进行全面、专业的分析。

商业计划书内容：
{text}

请从以下维度进行深入分析：

1. **执行摘要**
   - 核心商业模式概述
   - 关键亮点总结

2. **市场分析**
   - 目标市场规模与增长潜力
   - 竞争格局分析
   - 市场机会与威胁

3. **产品/服务评估**
   - 产品独特性与创新点
   - 技术壁垒
   - 用户价值主张

4. **商业模式**
   - 收入模式清晰度
   - 成本结构合理性
   - 盈利能力预测

5. **团队评估**
   - 核心团队背景
   - 团队完整性
   - 执行能力

6. **财务分析**
   - 收入预测合理性
   - 资金需求与使用计划
   - 财务健康度

7. **风险评估**
   - 主要风险因素
   - 风险应对措施

8. **投资建议**
   - 综合评分 (1-10分)
   - 投资价值判断
   - 关键建议

请用专业、客观的语言撰写分析报告，每个部分都要有具体的论据支持。"""

        # 调用API
        response = client.chat.completions.create(
            model="qwen-plus",  # 或使用 "qwen-turbo", "qwen-max"
            messages=[
                {"role": "system", "content": "你是一位经验丰富的风险投资分析师，擅长评估商业计划书。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"API 调用失败: {str(e)}")
        return None

# 显示文件信息
if uploaded_file is not None:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"📄 **文件名**: {uploaded_file.name}")
        st.info(f"📦 **文件大小**: {uploaded_file.size / 1024:.2f} KB")
        st.info(f"📝 **文件类型**: {uploaded_file.type}")
    
    with col2:
        st.success("✅ 文件上传成功！")
        st.markdown("点击下方按钮开始分析")

    # 分析按钮
    st.markdown("---")
    if st.button("🚀 开始分析", type="primary", use_container_width=True):
        
        # 检查API Key
        if not api_key:
            st.error("⚠️ 请先在侧边栏输入通义千问 API Key")
        else:
            # 显示进度
            with st.spinner("正在提取文件内容..."):
                # 根据文件类型提取文本
                if uploaded_file.type == "application/pdf":
                    text = extract_pdf_text(uploaded_file)
                else:  # PPT
                    text = extract_ppt_text(uploaded_file)
                
                if text:
                    st.success("✅ 文件内容提取成功")
                    
                    # 显示提取的文本预览
                    with st.expander("📝 查看提取的文本内容（前500字）"):
                        st.text(text[:500] + "..." if len(text) > 500 else text)
            
            # 调用AI分析
            if text:
                with st.spinner("🤖 AI 正在分析中，请稍候..."):
                    analysis = analyze_with_qwen(text, api_key)
                
                if analysis:
                    st.success("✅ 分析完成！")
                    st.markdown("---")
                    st.header("📊 分析报告")
                    st.markdown(analysis)
                    
                    # 提供下载选项
                    st.markdown("---")
                    st.download_button(
                        label="📥 下载分析报告",
                        data=analysis,
                        file_name=f"分析报告_{uploaded_file.name}.txt",
                        mime="text/plain"
                    )
else:
    # 未上传文件时的提示
    st.info("👆 请在上方上传商业计划书文件")

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>商业计划书 AI 分析助手 | Powered by 通义千问 & Streamlit</p>
    <p>⚠️ 本工具仅供参考，投资决策请结合多方面信息综合判断</p>
</div>
""", unsafe_allow_html=True)

