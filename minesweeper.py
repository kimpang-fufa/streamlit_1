import streamlit as st
import random

st.title("Minesweeper")

if "board" not in st.session_state:
    # Create empty grid
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
                    if 0 <= nr < 5 and 0 <= nc < 5 and board[nr][nc] == "💣":
                        count += 1
            board[r][c] = "0" if count == 0 else str(count)
            
    st.session_state.board = board
    st.session_state.revealed = {}  # Tracks dug positions
    st.session_state.flags = set()   # Tracks flagged positions
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.flag_mode = False  # Track toggle state
    st.session_state.message = "Dig carefully! 5 mines are hidden here."


if st.session_state.won:
    st.success("CONGRATULATIONS! You cleared all safe spots and won!")
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
        if st.button(mode_label, type="secondary" if st.session_state.flag_mode else "primary", use_container_width=True):
            st.session_state.flag_mode = not st.session_state.flag_mode
            st.rerun()

st.write("---")


for r in range(5):
    cols = st.columns(5)
    for c in range(5):
        key_id = f"{r},{c}"
        with cols[c]:
        
            if key_id in st.session_state.revealed:
                st.button(st.session_state.board[r][c], key=f"btn_{key_id}", disabled=True, use_container_width=True)
            elif st.session_state.game_over and st.session_state.board[r][c] == "💣":
                st.button("💣", key=f"btn_{key_id}", disabled=True, use_container_width=True)
            elif st.session_state.game_over or st.session_state.won:
                label = "🚩" if key_id in st.session_state.flags else "❓"
                st.button(label, key=f"btn_{key_id}", disabled=True, use_container_width=True)
            else:
                display_label = "🚩" if key_id in st.session_state.flags else "❓" 
                 
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
                                st.snow()
                            else:
                                st.session_state.message = ":D"
                                
                                total_safe_spots = 20
                                if len(st.session_state.revealed) == total_safe_spots:
                                    st.session_state.won = True
                                    st.balloons()
                    st.rerun()
                
