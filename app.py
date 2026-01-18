import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. 基本設定
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍")

# 2. デザイン
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; border: none; }
    .stCameraInput { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. APIキー取得
api_key = st.secrets.get("GEMINI_API_KEY", "")

# 4. モデルの自動選択ロジック（ここが修正ポイント！）
@st.cache_resource
def initialize_model(key):
    if not key: return None
    try:
        genai.configure(api_key=key)
        # 使えるモデルをすべて取得
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 優先順位をつけてモデルを探す
        targets = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro', 'models/gemini-1.0-pro']
        for t in targets:
            if t in available_models:
                return genai.GenerativeModel(t)
        
        # 見つからない場合は最初に見つかったものを使う
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"モデルの取得に失敗しました: {e}")
    return None

model = initialize_model(api_key)

# 5. メインUI
st.title("🔍 Smart-Price Lens")

if not model:
    st.warning("APIキーを確認してください。Google AI Studioで新しいキーを発行すると解決する場合があります。")
    st.stop()

# 接続中のモデルを表示（安心材料として）
st.caption(f"Connected: {model.model_name}")

img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名を入力")

target = img_file if img_file else text_query

if target:
    try:
        with st.spinner("AIが最安値を調査中..."):
            prompt = "あなたは価格比較の専門家です。この商品の正確な名前、主要ECサイト（Amazon、楽天、Yahooなど）の送料込み目安価格、今買うべきかの判定を日本語で教えてください。最後にLINE共有用の1行要約を作ってください。"
            
            if img_file:
                response = model.generate_content([prompt, img_file])
            else:
                response = model.generate_content(f"{prompt}\n対象: {text_query}")
            
            st.success("調査完了！")
            st.markdown(response.text)
            
            # LINE共有
            share_msg = urllib.parse.quote(f"Smart-Price Lensで見つけたよ！\n{target}")
            line_url = f"https://line.me/R/msg/text/?{share_msg}"
            st.link_button("🟢 LINEで家族に共有", line_url)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
