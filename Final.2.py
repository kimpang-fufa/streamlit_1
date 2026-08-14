import streamlit as st
import chromadb
import os
import random
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
import time


st.set_page_config(page_title=":D", layout="wide")
load_dotenv()
MODEL = "llama-3.1-8b-instant"
API_KEY = os.getenv("groq_API_KEY")

if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    st.sidebar.error("Missing groq_API_KEY in environment!")

if "current_page" not in st.session_state:
    st.session_state.current_page = "RAG System"
if "chunk_size" not in st.session_state:
    st.session_state.chunk_size = 250
if "overlap" not in st.session_state:
    st.session_state.overlap = 50
if "num_results" not in st.session_state:
    st.session_state.num_results = 5
if "context" not in st.session_state:
    st.session_state.context = []
if "question" not in st.session_state:
    st.session_state.question = ""
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting!"}]


st.sidebar.title("Sidebar")
st.sidebar.markdown("---")

if st.sidebar.button("RAG System", use_container_width=True):
    st.session_state.current_page = "RAG System"
if st.sidebar.button("Chatbot", use_container_width=True):
    st.session_state.current_page = "Chatbot"
if st.sidebar.button("Minesweeper", use_container_width=True):
    st.session_state.current_page = "Minesweeper"
if st.sidebar.button("Rock Paper Scissors", use_container_width=True):
    st.session_state.current_page = "Rock Paper Scissors"


if st.session_state.current_page == "RAG System":
    st.title("RAG Multi-Document Analyzer")
    st.write("Adjust your chunk sizes and result amounts in the sidebar.")

    st.sidebar.markdown("---")
    st.sidebar.header("RAG Settings")
    st.session_state.chunk_size = st.sidebar.slider("Chunk Size", min_value=100, max_value=1000,
                                                    value=st.session_state.chunk_size, step=50)
    st.session_state.overlap = st.sidebar.slider("Chunk Overlap", min_value=10, max_value=200,
                                                 value=st.session_state.overlap, step=10)
    st.session_state.num_results = st.sidebar.slider("Number of Results", min_value=1, max_value=10,
                                                     value=st.session_state.num_results, step=1)

    file_type = st.selectbox(
        "What type of files do you want to upload?",
        options=["PDF Documents (.pdf)", "Plain Text (.txt)", "Both (.pdf & .txt)"],
        index=2
    )

    if file_type == "PDF Documents (.pdf)":
        allowed_types = ["pdf"]
    elif file_type == "Plain Text (.txt)":
        allowed_types = ["txt"]
    else:
        allowed_types = ["pdf", "txt"]

    files = st.file_uploader("Upload your files here", type=allowed_types, accept_multiple_files=True)

    if files and st.button("Process File"):
        st.write("Processing files...")
        chroma_client = chromadb.Client()
        try:
            chroma_client.delete_collection("documents")
        except:
            pass
        collection = chroma_client.create_collection("documents")

        for file in files:
            text = ""
            if file.name.lower().endswith(".pdf"):
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            elif file.name.lower().endswith(".txt"):
                text = file.read().decode("utf-8") + "\n"

            chunks = []
            step = st.session_state.chunk_size - st.session_state.overlap
            if step <= 0:
                step = 1
            for i in range(0, len(text), step):
                chunk_with_source = f"[Source: {file.name}] {text[i: i + st.session_state.chunk_size]}"
                chunks.append(chunk_with_source)
            tags = [file.name + "_" + str(i) for i in range(len(chunks))]
            collection.add(documents=chunks, ids=tags)

        st.session_state.collection = collection
        st.success("Chunks added to knowledge base!")

    question = st.text_input("Ask a question about the file")

    if st.button("Search"):
        if "collection" not in st.session_state or st.session_state.collection is None:
            st.error("Please upload and process files first!")
        else:
            st.write("thinking!")
            collection = st.session_state.collection
            result = collection.query(query_texts=[question], n_results=st.session_state.num_results)
            if result["documents"] and len(result["documents"]) > 0:
                st.session_state.context = result["documents"][0]
            else:
                st.session_state.context = []

            st.session_state.question = question
            st.write("Distances:", result["distances"])
            for ans in st.session_state.context:
                st.write(ans)

    if st.button("LLM answer"):
        if not st.session_state.context:
            st.error("Please query context from search before processing answers!")
        elif client is None:
            st.error("Missing API Key.")
        else:
            st.write("contacting LLM...")
            context = "\n".join(st.session_state.context)
            question = st.session_state.question

            messages = [
                {"role": "system",
                 "content": "Answer the user's question using only the provided document context. Every text chunk contains its own '[Source: filename]' tag. You must explicitly cite the specific source file name(s) in your answer text."},
                {"role": "user", "content": f"DOCUMENT CONTEXT:\n{context}\n\nQUESTION:\n{question}"}
            ]
            response = client.chat.completions.create(model=MODEL, messages=messages)
            full_response = response.choices[0].message.content
            st.write("LLM Answer:", full_response)

            st.markdown("---")
            st.caption("Click the copy icon to copy response")
            st.code(full_response, language="markdown")
            st.caption("If you don't like this answer, click the LLM answer button again to get a different one.")


elif st.session_state.current_page == "Chatbot":
    st.title("Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            temp = client.chat.completions.create(model=MODEL, messages=st.session_state.messages)
            assistant_response = temp.choices[0].message.content

            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)

                message_placeholder.markdown(full_response + "")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})



elif st.session_state.current_page == "Minesweeper":
    import random
    import streamlit as st
    st.title("Minesweeper")

    difficulty = st.selectbox(
        "Choose Grid Size:",
        ["Beginner (5x5, 5 Mines)", "Intermediate (8x8, 10 Mines)", "Expert (10x10, 25 Mines)"]
    )

    if "Beginner" in difficulty:
        grid_size, mine_count = 5, 5
    elif "Intermediate" in difficulty:
        grid_size, mine_count = 8, 10
    else:
        grid_size, mine_count = 10, 25
    total_safe_spots = (grid_size * grid_size) - mine_count

    if "current_difficulty" not in st.session_state:
        st.session_state.current_difficulty = difficulty

    if st.session_state.current_difficulty != difficulty:
        st.session_state.current_difficulty = difficulty
        if "board" in st.session_state:
            del st.session_state.board
        st.rerun()

    if "board" not in st.session_state:
        board = [["" for _ in range(grid_size)] for _ in range(grid_size)]
        mines_placed = 0
        while mines_placed < mine_count:
            r, c = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
            if board[r][c] != "💣":
                board[r][c] = "💣"
                mines_placed += 1

        for r in range(grid_size):
            for c in range(grid_size):
                if board[r][c] == "💣":
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < grid_size and 0 <= nc < grid_size and board[nr][nc] == "💣":
                            count += 1
                board[r][c] = "0" if count == 0 else str(count)

        st.session_state.board = board
        st.session_state.revealed = {}
        st.session_state.flags = set()
        st.session_state.game_over = False
        st.session_state.won = False
        st.session_state.flag_mode = False
        st.session_state.message = f"Good luck! (There are {mine_count} mines FYI)"

    if st.session_state.won:
        st.success("Yipepepepepepe! You won! :3")
    elif st.session_state.game_over:
        st.error("Boom! Game Over! 'o'")
    else:
        st.info(st.session_state.message)

    col_reset, col_toggle = st.columns(2)

    with col_reset:
        if st.button("Restart Game", use_container_width=True):
            del st.session_state.board
            st.rerun()

    with col_toggle:
        if not st.session_state.game_over and not st.session_state.won:
            mode_label = "🚩 Flag Mode: ON" if st.session_state.flag_mode else "⛏️ Dig Mode: ON"
            if st.button(mode_label, type="secondary" if st.session_state.flag_mode else "primary",
                         use_container_width=True):
                st.session_state.flag_mode = not st.session_state.flag_mode
                st.rerun()

    st.write("---")

    for r in range(grid_size):
        cols = st.columns(grid_size)
        for c in range(grid_size):
            key_id = f"{r},{c}"
            with cols[c]:

                if key_id in st.session_state.revealed:
                    st.button(st.session_state.board[r][c], key=f"btn_{key_id}", disabled=True,
                              use_container_width=True)
                elif st.session_state.game_over and st.session_state.board[r][c] == "💣":
                    st.button("💣", key=f"btn_{key_id}", disabled=True, use_container_width=True)
                elif st.session_state.game_over or st.session_state.won:
                    label = "🚩" if key_id in st.session_state.flags else ""
                    st.button(label, key=f"btn_{key_id}", disabled=True, use_container_width=True)
                else:
                    display_label = "🚩" if key_id in st.session_state.flags else ""

                    if st.button(display_label, key=f"btn_{key_id}", use_container_width=True):
                        if st.session_state.flag_mode:
                            if key_id in st.session_state.flags:
                                st.session_state.flags.remove(key_id)
                            else:
                                st.session_state.flags.add(key_id)

                        else:
                            if key_id not in st.session_state.flags:
                                st.session_state.revealed[key_id] = True

                                if st.session_state.board[r][c] == "💣":
                                    st.session_state.game_over = True
                                else:
                                    st.session_state.message = ":D"

                                    if len(st.session_state.revealed) == total_safe_spots:
                                        st.session_state.won = True
                                        st.balloons()
                        st.rerun()



elif st.session_state.current_page == "Rock Paper Scissors":
    st.title("Rock Paper Scissors")
    choices = ["Rock", "Paper", "Scissors"]
    col1, col2, col3 = st.columns(3)
    user_choice = None
    if col1.button("Rock"):
        user_choice = "Rock"
    if col2.button("Paper"):
        user_choice = "Paper"
    if col3.button("Scissors"):
        user_choice = "Scissors"

    if user_choice:
        comp_choice = random.choice(choices)
        st.write(f"You chose: {user_choice}")
        st.write(f"Computer chose: {comp_choice}")

        if user_choice == comp_choice:
            st.info("It's a tie!")
        elif (
                (user_choice == "Rock" and comp_choice == "Scissors")
                or (user_choice == "Paper" and comp_choice == "Rock")
                or (user_choice == "Scissors" and comp_choice == "Paper")
        ):
            st.success("You win!")
            st.warning("50/50 to win you bums not rock, paper, scissors. Odds, I win. Even, you win.")

            with st.spinner("50/50'ing rn to see if you actually win(I know it looks lame, don't judge"):
                time.sleep(5)

            spinner_verdict = random.choice(["Even", "Odd"])

            if spinner_verdict == "Even":
                st.success("Yipepepeepepe, you're a winner :3")
                st.balloons()
            else:
                st.error("Of course you lost, you never won in the first place :D")

        else:
            st.error("You Lost!")

