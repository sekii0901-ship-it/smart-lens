import streamlit as st
import google.generativeai as genai
import urllib.parse

# アプリのレイアウト設定
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍")

# --- UIデザインの調整 ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; }
    .stCameraInput { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- APIキーの設定（サイドバーで入力または管理画面から取得） ---
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Streamlitの「Secrets」機能またはサイドバーからの入力を優先
api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.api_key)

with st.sidebar:
    st.title("⚙️ 設定")
    if not api_key:
        api_key = st.text_input("APIキーを入力してください", type="password")
        st.session_state.api_key = api_key
    else:
        st.success("APIキーは設定済みです")

# --- メイン機能 ---
st.title("🔍 Smart-Price Lens")

# 撮影または入力
img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名を入力")

target = img_file if img_file else text_query

if target and api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    with st.spinner("リアルタイム調査中..."):
        prompt = "あなたは価格比較の専門家です。この商品の正式名称を特定し、主要10店舗前後の現在の送料込み価格と、今買うべきかの判定を日本語で教えてください。最後に、LINE共有用の短い1行要約も作ってください。"
        
        if img_file:
            response = model.generate_content([prompt, img_file])
        else:
            response = model.generate_content(f"{prompt}\n商品名: {text_query}")
        
        st.markdown("---")
        st.markdown(response.text)
        
        # LINE共有ボタン
        share_msg = urllib.parse.quote(f"Smart-Price Lensで調査完了！\n{response.text[:100]}...")
        line_link = f"https://line.me/R/msg/text/?{share_msg}"
        st.link_button("🟢 LINEで家族に共有", line_link)

elif not api_key:
    st.info("左上の ＞ ボタンから設定を開き、APIキーを入力してください。")
