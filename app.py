import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from gtts import gTTS
from googletrans import Translator
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

st.set_page_config(page_title="AI Document Intelligence", layout="wide")

st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
h1 {
    text-align: center;
    font-size: 3rem;
    background: linear-gradient(90deg, #00dbde, #fc00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background: rgba(30,41,59,0.7);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}
.output-box {
    background: #020617;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #334155;
    height: 350px;
    overflow-y: auto;
    font-family: monospace;
    color: #22c55e;
}
button[kind="primary"] {
    background: linear-gradient(90deg, #00dbde, #fc00ff);
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Document Intelligence Pro")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    endpoint = st.text_input("🔗 Endpoint")
    key = st.text_input("🔑 API Key", type="password")

# Tabs
st.markdown('<div class="card">', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📤 Upload", "🌐 URL"])

uploaded_file = None
url = None

with tab1:
    uploaded_file = st.file_uploader("Upload Image/PDF", type=["png", "jpg", "jpeg", "pdf"])

with tab2:
    url = st.text_input("Enter Document URL")

st.markdown('</div>', unsafe_allow_html=True)

# Functions
def analyze_url(client, url):
    poller = client.begin_analyze_document("prebuilt-read", {"urlSource": url})
    result = poller.result()
    text = ""
    for page in result.pages:
        for line in page.lines:
            text += line.content + "\n"
    return text

def analyze_file(client, file):
    poller = client.begin_analyze_document("prebuilt-read", file)
    result = poller.result()
    text = ""
    for page in result.pages:
        for line in page.lines:
            text += line.content + "\n"
    return text

# Output Section
st.markdown('<div class="card">', unsafe_allow_html=True)

if st.button("🚀 Analyze Document"):
    if not endpoint or not key:
        st.error("Enter API key & endpoint")
    else:
        try:
            client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))

            with st.spinner("🤖 AI is analyzing..."):
                if url:
                    text = analyze_url(client, url)
                elif uploaded_file:
                    text = analyze_file(client, uploaded_file)
                else:
                    st.warning("Upload file or enter URL")
                    text = ""

            if text:
                st.success("✅ Analysis Complete")

                st.session_state["result"] = text

        except Exception as e:
            st.error(str(e))

# Show Output
if "result" in st.session_state:

    text = st.session_state["result"]

    st.subheader("📊 Extracted Text")
    st.markdown(f'<div class="output-box">{text}</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    # 🔊 Text-to-Speech
    with col1:
        if st.button("🔊 Speak"):
            tts = gTTS(text)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tmp.name)
            st.audio(tmp.name)

    # 🌍 Translate
    with col2:
        lang = st.selectbox("🌍 Translate to", ["hi", "en", "fr", "es", "de"])
        if st.button("Translate"):
            translator = Translator()
            translated = translator.translate(text, dest=lang)
            st.text_area("Translated Text", translated.text, height=200)

    # 📥 Download TXT
    with col3:
        st.download_button("📄 Download TXT", text, file_name="output.txt")

    # 📥 Download PDF
    def create_pdf(content):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(tmp.name)
        styles = getSampleStyleSheet()
        story = [Paragraph(content, styles["Normal"])]
        doc.build(story)
        return tmp.name

    pdf_file = create_pdf(text)
    st.download_button("📥 Download PDF", open(pdf_file, "rb"), file_name="output.pdf")

st.markdown('</div>', unsafe_allow_html=True)