from packages.pipeline.gpt import get_chat_response
from packages.pipeline.notebookreader import extract_cells
import streamlit as st

cell_output = extract_cells("Pipeline Testing.ipynb")
cell_output.to_csv("Jupyter Cell Content.csv", index=False)

emotions = "Bored"

get_chat_response(cell_output, emotions)

st.title("Pedagogical Agent")

st.subheader("Jupyter Cell Content")
st.write(cell_output)

st.subheader("Emotions")
st.write(emotions)

if st.button("Get Chat Response"):
    st.write(get_chat_response(cell_output, emotions))