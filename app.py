import streamlit as st
import google.generativeai as genai
import urllib.parse

# アプリのレイアウト設定
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍")

# --- UIデザイン ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; }
    .stCameraInput { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- APIキーの設定 ---
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.api_key)

with st.sidebar:
    st.title("⚙️ 設定")
    if not api_key:
        api_key = st.text_input("APIキーを入力してください", type="password")
        st.session_state.api_key = api_key
    else:
        st.success("APIキー設定済み")

# --- メイン機能 ---
st.title("🔍 Smart-Price Lens")

img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名を入力")

target = img_file if img_file else text_query

if target and api_key:
    try:
        genai.configure(api_key=api_key)
        # 最も安定したモデル名指定形式に変更
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        with st.spinner("リアルタイム調査中..."):
            prompt = "あなたは価格比較の専門家です。この商品の正式名称を特定し、主要10店舗前後の現在の送料込み目安価格と、今買うべきかの判定を日本語で教えてください。最後に、LINE共有用の1行要約も作ってください。"
            
            if img_file:
                response = model.generate_content([prompt, img_file])
            else:
                response = model.generate_content(f"{prompt}\n商品名: {text_query}")
            
            st.success("調査完了！")
            st.markdown(response.text)
            
            # LINE共有
            share_msg = urllib.parse.quote(f"Smart-Price Lensで調査完了！\n{target} の価格をチェックしました。")
            line_link = f"https://line.me/R/msg/text/?{share_msg}"
            st.link_button("🟢 LINEで家族に共有", line_link)

    except Exception as e:
        st.error(f"エラーが発生しました。アプリを再起動してみてください。")
        st.info(f"詳細エラー: {e}")

elif not api_key:
    st.info("APIキーを設定してください。")
