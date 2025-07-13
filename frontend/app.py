import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="GenAI Document Assistant", layout="wide")
st.title("📄 GenAI Document Assistant")

if 'doc_id' not in st.session_state:
    st.session_state['doc_id'] = None
if 'summary' not in st.session_state:
    st.session_state['summary'] = None
if 'challenge_questions' not in st.session_state:
    st.session_state['challenge_questions'] = None
if 'challenge_results' not in st.session_state:
    st.session_state['challenge_results'] = None

# --- Document Upload ---
st.sidebar.header("Upload Document")
uploaded_file = st.sidebar.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
    with st.spinner("Uploading and processing..."):
        res = requests.post(f"{API_URL}/upload", files=files)
    if res.status_code == 200:
        data = res.json()
        st.session_state['doc_id'] = data['doc_id']
        st.session_state['summary'] = data['summary']
        st.session_state['challenge_questions'] = None
        st.session_state['challenge_results'] = None
        st.success("Document uploaded and processed!")
    else:
        st.error("Failed to upload document.")

# --- Summary Display ---
if st.session_state['summary']:
    st.subheader("Auto-Summary (≤150 words)")
    st.info(st.session_state['summary'])

# --- Mode Selection ---
mode = st.radio("Choose Mode", ["Ask Anything", "Challenge Me"], horizontal=True)

# --- Ask Anything Mode ---
if mode == "Ask Anything" and st.session_state['doc_id']:
    st.subheader("Ask Anything")
    question = st.text_input("Enter your question about the document:")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            res = requests.post(f"{API_URL}/ask", json={"doc_id": st.session_state['doc_id'], "question": question})
        if res.status_code == 200:
            data = res.json()
            st.markdown(f"**Answer:** {data['answer']}")
            st.markdown(f"**Evidence:** :orange[{data['evidence']}]")
            st.caption(f"Location: {data['location']}")
        else:
            st.error("Failed to get answer.")

# --- Challenge Me Mode ---
if mode == "Challenge Me" and st.session_state['doc_id']:
    st.subheader("Challenge Me: Test Your Understanding")
    if st.button("Generate Questions") or st.session_state['challenge_questions']:
        if not st.session_state['challenge_questions']:
            with st.spinner("Generating questions..."):
                res = requests.get(f"{API_URL}/challenge", params={"doc_id": st.session_state['doc_id']})
            if res.status_code == 200:
                st.session_state['challenge_questions'] = res.json()['questions']
            else:
                st.error("Failed to generate questions.")
        if st.session_state['challenge_questions']:
            answers = []
            for idx, q in enumerate(st.session_state['challenge_questions']):
                st.markdown(f"**Q{idx+1}: {q['question']}")
                ans = st.text_input(f"Your answer to Q{idx+1}", key=f"ans_{idx}")
                answers.append(ans)
            if st.button("Submit Answers"):
                with st.spinner("Grading your answers..."):
                    res = requests.post(f"{API_URL}/challenge/grade", json={
                        "doc_id": st.session_state['doc_id'],
                        "user_answers": answers
                    })
                if res.status_code == 200:
                    st.session_state['challenge_results'] = res.json()['results']
                else:
                    st.error("Failed to grade answers.")
            # Show grading results
            if st.session_state['challenge_results']:
                st.subheader("Results:")
                for idx, result in enumerate(st.session_state['challenge_results']):
                    st.markdown(f"**Q{idx+1}**: {result['grade'].capitalize()}")
                    st.markdown(f"*Feedback:* {result['feedback']}")
                    st.markdown(f"*Evidence:* :orange[{result['evidence']}]")
                    st.caption(f"Location: {result['location']}")
