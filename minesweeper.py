import streamlit as st
import random

st.title("💣 Real 5x5 Minesweeper")

# 1. Setup the 5x5 Board with Numbers
if "board" not in st.session_state:
    board = [["" for _ in range(5)] for _ in range(5)]
    mines_placed = 0
    while mines_placed < 5:
        r, c = random.randint(0, 4), random.randint(0, 4)
        if board[r][c] != "💣":
            board[r][c] = "💣"
            mines_placed += 1

    for r in range(5):
        for c in range(5):
            if board[r][c] == "💣":
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 5 and 0 <= nc < 5:
                        if board[nr][nc] == "💣":
                            count += 1
            board[r][c] = "⬜" if count == 0 else str(count)
            
    st.session_state.board = board
    st.session_state.revealed = {}
    st.session_state.game_over = False
    st.session_state.message = "Dig carefully! 5 mines are hidden here."
    
if st.button("Restart Game"):
    del st.session_state.board
    st.rerun()

st.write(f" {st.session_state.message}")

for r in range(5):
    cols = st.columns(5)
    for c in range(5):
        key_id = f"cell_{r}_{c}"
        with cols[c]:
            if key_id in st.session_state.revealed or (st.session_state.game_over and st.session_state.board[r][c] == "💣"):
                st.button(st.session_state.board[r][c], key=key_id, disabled=True, use_container_width=True)
            elif st.session_state.game_over:
                st.button("❓", key=key_id, disabled=True, use_container_width=True)
            else:
                if st.button("❓", key=key_id, use_container_width=True):
                    st.session_state.revealed[key_id] = True
                    if st.session_state.board[r][c] == "💣":
                        st.session_state.message = "💥 KABOOM! Game Over!"
                        st.session_state.game_over = True
                        st.snow()
                    else:
                        st.session_state.message = "✅ Safe! Keep tracking the numbers."
                    st.rerun()
