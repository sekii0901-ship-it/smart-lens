import streamlit as st
import google.generativeai as genai
import urllib.parse

# アプリ設定
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍")

# デザイン
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; }
    .stCameraInput { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# APIキー取得
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.api_key)

# メインUI
st.title("🔍 Smart-Price Lens")

img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名を入力")

target = img_file if img_file else text_query

if target and api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 【修正】モデル名を最も標準的な形式に固定
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("AIが調査中..."):
            prompt = "あなたは価格比較の専門家です。この商品の正確な名前、主要ECサイトの送料込み最安値、判定を日本語で教えてください。最後に1行要約を作ってください。"
            
            if img_file:
                response = model.generate_content([prompt, img_file])
            else:
                response = model.generate_content(f"{prompt}\n対象: {text_query}")
            
            st.success("調査完了！")
            st.markdown(response.text)
            
            # LINE共有
            share_msg = urllib.parse.quote(f"Smart-Price Lensで調査完了！\n{target}")
            line_link = f"https://line.me/R/msg/text/?{share_msg}"
            st.link_button("🟢 LINEで家族に共有", line_link)

    except Exception as e:
        # 詳細なエラーを出して原因を特定
        st.error("⚠️ 接続エラーが発生しました")
        with st.expander("🛠️ 診断情報を確認"):
            st.write(f"エラー詳細: {e}")
            st.write("対策: このエラーが出る場合、Streamlitでアプリを一度『Delete』して作り直すのが最も確実です。")

elif not api_key:
    st.info("APIキーを設定してください。")
