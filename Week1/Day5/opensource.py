"""Local Qwen chat - Clean Light UI, fast startup, happy emoji replies.

Setup:  pip install streamlit transformers torch
        put config.toml in a folder named .streamlit next to this file
Run:    streamlit run qwen_chat_app.py
Run it from the folder that contains ./models/qwen-0.5b
"""
import html
import os
import random
from threading import Thread

# Never phone home to Hugging Face: the model is already on disk (faster, works offline)
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import streamlit as st

MODEL_PATH = "./models/qwen-0.5b"
MAX_HISTORY = 4                       # fewer past messages = less to process = faster replies
HAPPY = ["😊", "😄", "😁", "🙂", "😃"]
TYPING = ["😊", "😄", "😁", "😃"]     # faces that cycle while the answer is being written
AVATARS = {"user": "🙂", "assistant": "🤖"}
SUGGESTIONS = ["Explain a virtual environment", "Write a short poem", "Give me a fun fact"]

st.set_page_config(page_title="Local Qwen Chat", page_icon="😊", layout="centered",
                   initial_sidebar_state="collapsed")

# ---------- Clean Light styling ----------
st.markdown(
    """
<style>
.stApp {background:#f4f6fb;}
.hdr {display:flex; align-items:center; gap:12px; padding:14px 18px; margin-bottom:18px;
      background:#fff; border:1px solid #e3e8f2; border-radius:16px;}
.badge {width:40px; height:40px; border-radius:12px; background:#2f5fe0; color:#fff;
        display:flex; align-items:center; justify-content:center; font-weight:600; font-size:18px;}
.hdr-text {flex:1;}
.hdr-title {font-size:16px; font-weight:600; color:#1b2333;}
.hdr-sub {font-size:13px; color:#5b6679;}
.hdr-status {display:flex; align-items:center; gap:6px; font-size:13px; color:#2f7a4f;}
.dot {width:8px; height:8px; border-radius:50%; background:#2f9e5f; display:inline-block;}
/* assistant bubble: explicit dark text so it is readable even if the dark theme is active */
[data-testid="stChatMessage"] {background:#fff; border:1px solid #e3e8f2; max-width:85%;
    border-radius:18px 18px 18px 4px; padding:10px 16px;}
[data-testid="stChatMessage"], [data-testid="stChatMessage"] * {color:#1b2333 !important;}
[data-testid="stChatMessage"] code {background:#eef1f8 !important;}
/* user bubble: blue, right-aligned */
.ub-wrap {display:flex; justify-content:flex-end; margin:6px 0 10px;}
.ub {background:#2f5fe0; color:#fff !important; padding:12px 16px; max-width:75%; font-size:15px;
     line-height:1.45; border-radius:18px 18px 4px 18px;}
/* input bar + chips in the same light style */
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {background:#f4f6fb !important;}
[data-testid="stChatInput"] {border-radius:26px; background:#fff; border:1px solid #cfd7e6;}
[data-testid="stChatInput"] textarea {color:#1b2333 !important; background:#fff !important;}
div.stButton > button {border-radius:22px; min-height:44px; font-size:13px; background:#fff;
    border:1px solid #cfd7e6;}
div.stButton > button, div.stButton > button p {color:#1b2333 !important;}
</style>
<div class="hdr">
  <div class="badge">Q</div>
  <div class="hdr-text"><div class="hdr-title">Local Qwen</div>
  <div class="hdr-sub">Qwen2.5-0.5B · running on your PC</div></div>
  <div class="hdr-status"><span class="dot"></span>Offline</div>
</div>
""",
    unsafe_allow_html=True,
)

ss = st.session_state
if "messages" not in ss:
    ss.messages = []


def ask(text):
    ss.pending = text


def clear_chat():
    ss.messages = []


def user_bubble(text):
    safe = html.escape(text).replace("\n", "<br>")
    st.markdown(f'<div class="ub-wrap"><div class="ub">{safe}</div></div>', unsafe_allow_html=True)


def has_emoji(text):
    return any(0x1F300 <= ord(c) <= 0x1FAFF or 0x2600 <= ord(c) <= 0x27BF for c in text)


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    max_new_tokens = st.slider("Max reply length (tokens)", 32, 400, 150, step=16,
                               help="Shorter replies finish faster on a CPU.")
    temperature = st.slider("Creativity (temperature)", 0.0, 1.5, 0.7, step=0.1)
    system_prompt = st.text_area(
        "System prompt",
        "You are a cheerful, friendly assistant. Keep answers short and add a happy smiling emoji.",
    )
    st.button("🧹 Clear chat", on_click=clear_chat)

# ---------- Page body (renders instantly, before the model loads) ----------
pending = ss.pop("pending", None)
if not ss.messages and not pending:
    for col, text in zip(st.columns(len(SUGGESTIONS)), SUGGESTIONS):
        col.button(text, on_click=ask, args=(text,), key=f"chip_{text}")

for msg in ss.messages:
    if msg["role"] == "user":
        user_bubble(msg["content"])
    else:
        with st.chat_message("assistant", avatar=AVATARS["assistant"]):
            st.markdown(msg["content"])

typed = st.chat_input("Ask something...")

if not os.path.isdir(MODEL_PATH):
    st.error(f"Model folder not found: {MODEL_PATH}\n\n"
             "Run this app from the folder that contains `models/qwen-0.5b`, or download it with:\n\n"
             "`hf download Qwen/Qwen2.5-0.5B-Instruct --local-dir ./models/qwen-0.5b`")
    st.stop()


# ---------- Model: loaded once, then kept in memory ----------
@st.cache_resource(show_spinner="Getting Qwen ready... 😊 (first time only)")
def load_model():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(6)   # leave a few cores free so the PC stays responsive
    tok = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, local_files_only=True,
                                                 low_cpu_mem_usage=True)
    model.eval()
    # Warm-up: one tiny generation now, so the user's first question isn't slow
    model.generate(**tok("Hi", return_tensors="pt"), max_new_tokens=1)
    return tok, model


tok, model = load_model()


def stream_reply(history):
    """Generate in a background thread and yield text as it arrives."""
    from transformers import TextIteratorStreamer

    chat = [{"role": "system", "content": system_prompt}] + history[-MAX_HISTORY:]
    text = tok.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt")
    streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)

    kwargs = dict(**inputs, streamer=streamer, max_new_tokens=max_new_tokens)
    if temperature > 0:
        kwargs.update(do_sample=True, temperature=temperature, top_p=0.9)
    else:
        kwargs.update(do_sample=False)

    Thread(target=model.generate, kwargs=kwargs).start()
    yield from streamer


# ---------- Handle a new question ----------
prompt = pending or typed
if prompt:
    ss.messages.append({"role": "user", "content": prompt})
    user_bubble(prompt)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        box = st.empty()
        box.markdown(f"{random.choice(HAPPY)} Thinking...")
        reply = ""
        for i, chunk in enumerate(stream_reply(ss.messages)):
            reply += chunk
            box.markdown(f"{reply} {TYPING[(i // 3) % len(TYPING)]}")   # smiley changes while typing
        reply = reply.strip() or "I'm not sure what to say."
        if not has_emoji(reply):
            reply += f" {random.choice(HAPPY)}"                           # always end on a smile
        box.markdown(reply)
    ss.messages.append({"role": "assistant", "content": reply})