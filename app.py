import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. アプリ設定（iPhoneで最も見やすいワイド設定）
st.set_page_config(page_title="Smart-Price Lens", page_icon="🔍", layout="wide")

# 2. デザイン：表とボタンの視認性を最大化
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5rem; font-weight: bold; background-color: #007aff; color: white; border: none; }
    .stCameraInput { border-radius: 20px; }
    /* 表のフォントサイズ調整と横スクロール対応 */
    .stMarkdown table { font-size: 0.9rem; width: 100%; }
    th { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# 3. APIキー設定
api_key = st.secrets.get("GEMINI_API_KEY", "")

# 4. メインUI
st.title("🔍 Smart-Price Lens")
st.write("10店舗の価格を同時調査し、最安値へのリンクを表示します。")

img_file = st.camera_input("商品をスキャン")
text_query = st.text_input("または商品名・型番を入力")

target = img_file if img_file else text_query

if target and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("📊 主要10店舗をリアルタイム調査中..."):
            # プロンプト：10店舗、表形式、リンク、判定の指示を厳格化
            prompt = """
            あなたは日本で最も精度の高い価格比較スペシャリストです。
            入力された対象を特定し、以下の4点を必ず出力してください。

            1. **特定された商品名**: メーカー名と正確な型番。
            2. **10店舗価格比較表**: 
               以下の5つの列を持つMarkdownテーブルを作成してください。
               必ず主要な10店舗（Amazon, 楽天, Yahoo, 価格.com, ヨドバシ, ビックカメラ, ヤマダ, ノジマ, コジマ, ケーズ等）を網羅してください。
               | ショップ名 | 合計価格(送料込目安) | ポイント還元 | 判定 | 商品リンク(検索URL) |
               | :--- | :--- | :--- | :--- | :--- |
               ※「商品リンク」列には、各ショップの検索結果URLをMarkdown形式 [🔍開く](URL) で作成してください。
            3. **最終判定**: 今すぐ「買い」か「待ち」か。
            4. **LINE共有用要約**: 最終行に「商品名：最安値：判定」を1行で。
            """
            
            if img_file:
                response = model.generate_content([prompt, img_file])
            else:
                response = model.generate_content(f"{prompt}\n対象: {text_query}")
            
            st.success("調査が完了しました！")
            
            # 結果表示（表が綺麗にレンダリングされます）
            st.markdown(response.text)
            
            # 5. LINE共有機能
            st.markdown("---")
            lines = response.text.strip().splitlines()
            summary = lines[-1] if lines else "価格調査完了！"
            share_text = f"Smart-Price Lens調査結果\n{summary}"
            line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_text)}"
            st.link_button("🟢 LINEで結果を家族に送る", line_url)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

elif not api_key:
    st.info("💡 左上のメニューからAPIキーを設定してください。")
