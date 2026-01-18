import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. アプリの基本設定
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍", layout="centered")

# 2. iPhoneでの操作性を重視したUIデザイン
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; border: none; }
    .stCameraInput { border-radius: 20px; }
    .stTextInput>div>div>input { border-radius: 15px; }
    /* ローディング中などの余計な表示を消してシンプルに */
    div[data-testid="stStatusWidget"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. APIキーの管理
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# StreamlitのSecretsまたは手動入力からキーを取得
api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.api_key)

with st.sidebar:
    st.title("⚙️ 設定")
    if not api_key:
        api_key = st.text_input("Gemini APIキーを入力", type="password")
        st.session_state.api_key = api_key
    else:
        st.success("API連携済み")
        if st.button("キーを再設定する"):
            st.session_state.api_key = ""
            st.rerun()

# 4. メイン画面
st.title("🔍 Smart-Price Lens")
st.write("店頭の商品をスキャンして、最安値を即座に調査します。")

# 入力インターフェース
img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名・型番を入力", placeholder="例：Dyson V12, ロジクール K380s")

# どちらかの入力があれば実行
target = img_file if img_file else text_query

# 5. リサーチ実行
if target and api_key:
    try:
        genai.configure(api_key=api_key)
        
        # エラー対策：最も標準的なモデル名を使用
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("🔍 ネット上の最安値を調査中..."):
            prompt = """
            あなたはプロの購買アドバイザーです。
            1. 入力された情報から正確な商品名・型番を特定してください。
            2. Amazon, 楽天, Yahoo, 価格.com, 大手家電量販店の「送料込み」目安価格をリストアップしてください。
            3. 現在の底値と比較して、今すぐ「買い」か「待ち」か、理由を添えてハッキリ判定してください。
            4. 最後に、家族へのLINE共有用に「商品名：最安値：判定」を1行で作成してください。
            """
            
            if img_file:
                response = model.generate_content([prompt, img_file])
            else:
                response = model.generate_content(f"{prompt}\n対象: {text_query}")
            
            # 結果表示
            st.markdown("---")
            st.subheader("📊 調査結果")
            st.markdown(response.text)
            
            # 6. LINE共有機能
            st.markdown("### 📢 家族に教える")
            # 最終行の要約を取得
            lines = response.text.strip().splitlines()
            summary = lines[-1] if lines else "調査完了！"
            share_text = f"Smart-Price Lensで見つけたよ！\n{summary}"
            line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_text)}"
            st.link_button("🟢 LINEで共有する", line_url)

    except Exception as e:
        # エラーメッセージを分かりやすく表示
        error_msg = str(e)
        if "NotFound" in error_msg or "404" in error_msg:
            st.error("⚠️ AIモデルの設定エラーが発生しました。アプリを再起動（Reboot）してください。")
        elif "ResourceExhausted" in error_msg:
            st.error("⚠️ 無料枠の制限を超えました。1分待ってから再度試してください。")
        else:
            st.error(f"⚠️ エラーが発生しました: {error_msg}")
            st.info("右下のメニューから 'Reboot app' を試してみてください。")

elif not api_key:
    st.info("💡 アプリを動かすにはAPIキーが必要です。左上の「＞」から設定してください。")
