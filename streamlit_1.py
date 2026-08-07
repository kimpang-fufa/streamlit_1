import streamlit as st
import random
import time
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
    st.warning("Roll a dice to win you bums not rock, paper, scissors. Odds, I win. Even, you win.")
    
    with st.spinner("Spinning the wheel to see if you actually win(I know it looks lame, don't judge"):
        time.sleep(2)
    
    spinner_verdict = random.choice(["WIN", "FAILURE"])
    
    if spinner_verdict == "WIN":
        st.success("Yipepepeepepe, you're a winner :3")
        st.balloons()
    else:
        st.error("Of course you lost, you never won in the first place :D")

  else:
    st.error("You lose!")



    
