import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import io
import re

st.set_page_config(page_title="Meta 광고비 변환기", layout="centered")
st.title("📄 Meta 인보이스 PDF → 엑셀 변환기")

def parse_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # 거래 ID 추출
    transaction_id_match = re.search(r"거래 ID\s+(\d{16}-\d{16})", text)
    transaction_id = transaction_id_match.group(1) if transaction_id_match else "알 수 없음"

    lines = text.splitlines()
    rows = []

    prev_campaign = None
    for line in lines:
        line = line.strip()
        if line.startswith("★"):
            prev_campaign = line
        elif line.startswith("₩") and prev_campaign:
            try:
                amount = int(line.replace("₩", "").replace(",", ""))
                rows.append({
                    "거래ID": transaction_id,
                    "광고이름": prev_campaign,
                    "비용": amount
                })
                prev_campaign = None
            except:
                pass

    return rows

uploaded_files = st.file_uploader("PDF 인보이스 파일 업로드 (여러 개 가능)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        rows = parse_pdf(file)
        all_data.extend(rows)

    if all_data:
        df = pd.DataFrame(all_data)
        st.success("✅ 광고 데이터 추출 성공!")
        st.dataframe(df)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)

        st.download_button(
            label="📥 엑셀 파일 다운로드",
            data=buffer,
            file_name="meta_광고비_정리.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ 유효한 광고 데이터가 없습니다. PDF 내용을 다시 확인하세요.")
