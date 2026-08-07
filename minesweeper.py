import streamlit as st
import random as random
st.title("5x5 Minesweeper")

if "board5x5" not in st.session_state:
    pool = ["🟩"] * 20 + ["💣"] * 5
    random.shuffle(pool)

    st.session_state.board5x5 = [pool[i:i + 5] for i in range(0, 25, 5)]
    st.session_state.revealed = {}
    st.session_state.message = "Dig carefully! There are 5 hidden bombs."

if st.button("Restart Game"):
    del st.session_state.board5x5
    st.rerun()

st.write(st.session_state.message)

for r in range(5):
    cols = st.columns(5)
    for c in range(5):
        key_id = f"cell_{r}_{c}"
        with cols[c]:
            if key_id in st.session_state.revealed:
                st.button(st.session_state.board5x5[r][c], key=key_id, disabled=True, use_container_width=True)
            else:
                if st.button("❓", key=key_id, use_container_width=True):
                    st.session_state.revealed[key_id] = True
                    if st.session_state.board5x5[r][c] == "💣":
                        st.session_state.message = "💥 KABOOM! Game Over!"
                        st.snow()
                    else:
                        st.session_state.message = ":D"
                    st.rerun()
