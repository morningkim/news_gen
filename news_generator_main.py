import streamlit as st
import google.generativeai as genai
import datetime
from embedded_examples import get_embedded_examples_ko, get_embedded_examples_en

st.set_page_config(page_title="📰 기사 내용 생성기", page_icon="📰")

# 초기 상태 설정
defaults = {
    "lang": "ko",
    "api_key": "",
    "generated_articles": [],
    "selected_articles": [],
    "use_embedded_examples": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 언어 선택 (오른쪽 상단)
top1, top2 = st.columns([7, 1])
with top2:
    lang_flag = st.selectbox(" ", ["🇰🇷", "🇺🇸"], label_visibility="collapsed")
    st.session_state["lang"] = "ko" if "🇰🇷" in lang_flag else "en"
is_ko = st.session_state.lang == "ko"

# 다국어 텍스트 딕셔너리
T = {
    "title": "📰 기사 내용 생성기" if is_ko else "📰 Article Content Generator",
    "api_key": "Gemini API 키 입력" if is_ko else "Enter Gemini API Key",
    "api_help": "[API 키 발급 링크](https://makersuite.google.com/app/apikey)" if is_ko else "[Get Your Gemini API Key](https://makersuite.google.com/app/apikey)",
    "model": "Gemini 모델 선택" if is_ko else "Select Gemini Model",
    "content_lang": "기사 내용 언어" if is_ko else "Article Content Language",
    "output_lang": "기사 생성 언어" if is_ko else "Article Output Language",
    "rules": "1️⃣ 기사 생성 규칙" if is_ko else "1️⃣ Article Generation Rules",
    "word_limit": "최대 단어 수" if is_ko else "Max Word Count",
    "style": "기사 스타일" if is_ko else "Article Style",
    "guide": "기사 가이드라인" if is_ko else "Article Guideline",
    "examples": "2️⃣ 예제 입력" if is_ko else "2️⃣ Example Inputs",
    "num_examples": "예제 개수" if is_ko else "Number of Examples",
    "example_label": "예제" if is_ko else "Example",
    "new_input": "3️⃣ 새 기사 정보 입력" if is_ko else "3️⃣ New Article Information",
    "article_content": "기사 내용" if is_ko else "Article Content",
    "who": "누가 (Who)" if is_ko else "Who",
    "when": "언제 (When)" if is_ko else "When", 
    "what": "무엇을 (What)" if is_ko else "What",
    "how": "어떻게 (How)" if is_ko else "How",
    "why": "왜 (Why)" if is_ko else "Why",
    "where": "어디서 (Where)" if is_ko else "Where",
    "generate": "🚀 기사 내용 생성 (1개)" if is_ko else "🚀 Generate Article Content (1 article)",
    "result": "🎯 생성된 기사 내용" if is_ko else "🎯 Generated Article Content",
    "download": "📥 다운로드 (.txt)" if is_ko else "📥 Download (.txt)",
    "warning": "⚠️왼쪽 입력창에 Gemini API 키를 입력해주세요." if is_ko else "⚠️ Please enter your Gemini API key in the sidebar.",
    "sidebar_header": "⚙️ 설정" if is_ko else "⚙️ Settings",
    "use_embedded": "🤖 임베딩 예제 사용" if is_ko else "🤖 Use Embedded Examples",
    "use_manual": "✏️ 직접 입력 예제 사용" if is_ko else "✏️ Use Manual Examples",
    "embedded_examples_info": "뉴다이브, 정부 디지털치료제, 케이메디허브 관련 실제 기사 예제를 사용합니다" if is_ko else "Use real article examples related to NewDive, government digital therapeutics, and K-MEDI Hub",
    "manual_examples_info": "직접 예제를 입력하여 맞춤형 학습을 진행합니다" if is_ko else "Input your own examples for customized training",
    "5w1h_info": "5W1H 형식으로 기사의 핵심 요소를 입력해주세요" if is_ko else "Please enter the key elements of the article in 5W1H format",
}

style_opts = ["뉴스", "블로그", "칼럼"] if is_ko else ["News", "Blog", "Column"]

# 사이드바
st.sidebar.header(T["sidebar_header"])
model_id = st.sidebar.selectbox(T["model"], [
    "gemini-2.5-pro-preview-06-05",
    "gemini-2.5-flash-preview-05-20", 
    "gemini-2.0-pro",
    "gemini-2.0-flash"
])
st.sidebar.markdown(T["api_help"])
st.session_state.api_key = st.sidebar.text_input(
    T["api_key"], type="password", value=st.session_state.api_key)
if not st.session_state.api_key:
    st.warning(T["warning"])
    st.stop()
genai.configure(api_key=st.session_state.api_key)

# 타이틀
st.markdown(f"<h1 style='font-size:38px; text-align:center; margin-bottom:20px;'>{T['title']}</h1>", unsafe_allow_html=True)

# 1️⃣ 기사 생성 규칙
st.markdown(f"<h3 style='font-size:26px;'>{T['rules']}</h3>", unsafe_allow_html=True)
content_lang = st.radio(T["content_lang"], ["🇰🇷 한국어", "🇺🇸 English"], horizontal=True)
output_lang = st.radio(T["output_lang"], ["🇰🇷 한국어", "🇺🇸 English"], horizontal=True)
output_lang_code = "Korean" if "🇰🇷" in output_lang else "English"
max_words = st.number_input(T["word_limit"], min_value=100, value=800)
style = st.selectbox(T["style"], style_opts)
guide = st.text_input(T["guide"])

# 2️⃣ 예제 입력 방식 선택
st.markdown(f"<h3 style='font-size:26px; margin-top:30px;'>{T['examples']}</h3>", unsafe_allow_html=True)

# 예제 사용 방식 선택 버튼
col1, col2 = st.columns(2)
with col1:
    if st.button(T["use_embedded"], use_container_width=True):
        st.session_state.use_embedded_examples = True
with col2:
    if st.button(T["use_manual"], use_container_width=True):
        st.session_state.use_embedded_examples = False

# 선택된 방식에 따른 정보 표시
if st.session_state.use_embedded_examples:
    st.info(f"✅ {T['embedded_examples_info']}")
    # 외부 모듈에서 예제 불러오기
    try:
        embedded_examples = get_embedded_examples_ko() if "🇰🇷" in content_lang else get_embedded_examples_en()
        examples = embedded_examples
        
        # 임베딩된 예제 미리보기
        with st.expander("📋 사용될 예제 미리보기"):
            for i, (info, content) in enumerate(embedded_examples):
                st.write(f"**예제 {i+1}:**")
                st.write(f"누가: {info['who']}, 언제: {info['when']}, 어디서: {info['where']}")
                st.write(f"무엇을: {info['what']}, 어떻게: {info['how']}, 왜: {info['why']}")
                st.write(f"내용: {content[:200]}...")
                st.divider()
    except ImportError:
        st.error("embedded_examples.py 파일을 찾을 수 없습니다. 파일이 존재하는지 확인해주세요.")
        examples = []
    except Exception as e:
        st.error(f"예제 로딩 중 오류 발생: {e}")
        examples = []
else:
    st.info(f"✅ {T['manual_examples_info']}")
    
    # 직접 입력 예제
    num_examples = st.number_input(T["num_examples"], min_value=1, max_value=10, value=3)
    examples = []
    for i in range(int(num_examples)):
        with st.expander(f"📄 {T['example_label']} {i+1}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                who = st.text_input(f"{T['who']}", key=f"who_{i}")
                when = st.text_input(f"{T['when']}", key=f"when_{i}")
            with col2:
                where = st.text_input(f"{T['where']}", key=f"where_{i}")
                what = st.text_input(f"{T['what']}", key=f"what_{i}")
            with col3:
                how = st.text_input(f"{T['how']}", key=f"how_{i}")
                why = st.text_input(f"{T['why']}", key=f"why_{i}")
            
            c = st.text_area(f"{T['article_content']}", key=f"c_{i}", height=200)
            if who and when and what and c:
                info = {"who": who, "when": when, "where": where, "what": what, "how": how, "why": why}
                examples.append((info, c))

# 3️⃣ 새 기사 정보 입력 (5W1H)
st.markdown(f"<h3 style='font-size:26px; margin-top:30px;'>{T['new_input']}</h3>", unsafe_allow_html=True)
st.info(T["5w1h_info"])

col1, col2, col3 = st.columns(3)
with col1:
    new_who = st.text_input(T["who"])
    new_when = st.text_input(T["when"])
with col2:
    new_where = st.text_input(T["where"])
    new_what = st.text_input(T["what"])
with col3:
    new_how = st.text_input(T["how"])
    new_why = st.text_input(T["why"])

# 🚀 기사 내용 생성
if st.button(T["generate"]):
    if new_who and new_when and new_what:
        prompt = (
            f"You are a professional article writer.\n"
            f"Generate 1 high-quality article content in {output_lang_code}.\n"
            f"Style: {style}\nMax word count: {max_words}\n"
        )
        if guide:
            prompt += f"Guideline: {guide}\n"
        
        prompt += "\n### Examples:\n"
        for info, content in examples:
            prompt += f"Who: {info['who']}, When: {info['when']}, Where: {info['where']}\n"
            prompt += f"What: {info['what']}, How: {info['how']}, Why: {info['why']}\n"
            prompt += f"Article Content: {content}\n\n"
        
        prompt += "\n### NEW TASK:\n"
        prompt += f"Who: {new_who}, When: {new_when}, Where: {new_where}\n"
        prompt += f"What: {new_what}, How: {new_how}, Why: {new_why}\n"
        prompt += "Article Content:"

        try:
            model = genai.GenerativeModel(model_id)
            res = model.generate_content(prompt)
            generated_article = res.text.strip()
            
            st.markdown(f"<h3 style='font-size:24px; margin-top:30px;'>{T['result']}</h3>", unsafe_allow_html=True)
            st.markdown(generated_article)

            filename = f"article_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}_{output_lang_code}.txt"
            st.download_button(T["download"], data=generated_article, file_name=filename)

        except Exception as e:
            st.error(f"Gemini 오류: {e}")
    else:
        st.error("누가, 언제, 무엇을 항목은 필수 입력사항입니다." if is_ko else "Who, When, and What are required fields.")