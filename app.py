import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. アプリ設定
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍")

# 2. デザイン
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; border: none; }
    .stCameraInput { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. APIキー取得
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.api_key)

# 4. メインUI
st.title("🔍 Smart-Price Lens")

img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名を入力")

target = img_file if img_file else text_query

if target and api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 【修正ポイント】最も確実なモデル指定
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("AIが調査中..."):
            prompt = "あなたは価格比較の専門家です。この商品の正確な名前、主要ECサイトの送料込み最安値、今買うべきかの判定を日本語で教えてください。最後にLINE共有用の1行要約を作ってください。"
            
            if img_file:
                response = model.generate_content([prompt, img_file])
            else:
                response = model.generate_content(f"{prompt}\n対象: {text_query}")
            
            st.success("調査完了！")
            st.markdown(response.text)
            
            # LINE共有
            share_text = f"Smart-Price Lensで調査完了！\n{target}"
            line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_text)}"
            st.link_button("🟢 LINEで家族に共有", line_url)

    except Exception as e:
        st.error(f"⚠️ 接続エラーが発生しました")
        # デバッグ情報を表示
        with st.expander("詳細なエラー内容を確認"):
            st.write(f"Error: {e}")
            st.write("対策: APIキーが正しいか、またはGoogle AI Studioで新しいキーを発行してみてください。")

elif not api_key:
    st.info("左上の ＞ ボタンからAPIキーを設定してください。")
