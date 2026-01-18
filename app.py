import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. アプリの基本設定（iPhoneで見やすいレイアウト）
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍", layout="centered")

# 2. iPhoneアプリ風のカスタムデザイン
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; border: none; }
    .stCameraInput { border-radius: 20px; }
    .stTextInput>div>div>input { border-radius: 15px; }
    div[data-testid="stStatusWidget"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. APIキーの安全な取得
# Secrets設定がない場合はサイドバーから手動入力
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.api_key)

with st.sidebar:
    st.title("⚙️ アプリ設定")
    if not api_key:
        api_key = st.text_input("Gemini APIキーを入力", type="password")
        st.session_state.api_key = api_key
    else:
        st.success("API連携済み")
        if st.button("キーをリセット"):
            st.session_state.api_key = ""
            st.rerun()

# 4. メインUI
st.title("🔍 Smart-Price Lens")
st.write("店頭の商品をスキャンして、最安値を即座に判定します。")

# カメラとテキスト入力の切り替え
img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名・型番を入力", placeholder="例：Dyson V12")

# 調査対象の確定
target = img_file if img_file else text_query

# 5. リサーチ実行ロジック
if target and api_key:
    try:
        genai.configure(api_key=api_key)
        # 最も安定したモデル名を指定
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("🔍 全ECサイトを調査中..."):
            prompt = """
            あなたは超優秀な購買アドバイザーです。
            1. 入力された商品名、または画像から正確な商品名と型番を特定してください。
            2. Amazon, 楽天, Yahoo, ヨドバシ, ビックカメラ等、主要サイトの「送料込み」目安価格をリストアップしてください。
            3. 今の物価や底値をふまえ、今すぐ「買い」か「待ち」か、理由を添えて判定してください。
            4. 最後に、LINEで家族に送るための「1行要約（商品名：最安値：判定）」を作成してください。
            """
            
            if img_file:
                response = model.generate_content([prompt, img_file])
            else:
                response = model.generate_content(f"{prompt}\n商品名: {text_query}")
            
            # 結果表示
            st.markdown("---")
            st.subheader("📊 リサーチ結果")
            st.markdown(response.text)
            
            # 6. LINE共有機能（URLスキーム）
            st.markdown("### 📢 家族へ連絡")
            # AIの回答の最終行に要約がある前提で抽出（簡易実装）
            summary = response.text.splitlines()[-1]
            share_text = f"Smart-Price Lensで調べたよ！\n{summary}"
            line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_text)}"
            st.link_button("🟢 LINEで共有する", line_url)

    except Exception as e:
        if "ResourceExhausted" in str(e):
            st.error("⚠️ AIの無料枠（1分間の回数）を超えました。1分待ってから再度お試しください。")
        elif "NotFound" in str(e) or "404" in str(e):
            st.error("⚠️ モデル名が見つかりません。設定を確認してください。")
        else:
            st.error(f"⚠️ エラーが発生しました: {e}")

elif not api_key:
    st.info("💡 アプリを動かすにはAPIキーが必要です。左上の「＞」から設定してください。")
