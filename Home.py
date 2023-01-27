import streamlit as st
from PIL import Image

st.markdown("<h1 style='text-align: center'>Football Dashboard</h1>", unsafe_allow_html=True)

css_file = "styles.css"
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center'>Data Sources</h1>", unsafe_allow_html=True)

SOURCES = {
    "StatsBomb": "https://github.com/statsbomb/statsbombpy",
    "FBREF": "https://fbref.com/en/",
    "Understat": "https://understat.com/",
    "Transfermarkt": "https://www.transfermarkt.co.uk/",
}
st.write('\n')


cols = st.columns(len(SOURCES))
for index, (platform, link) in enumerate(SOURCES.items()):
    cols[index].write(f"[{platform}]({link})")

image = Image.open("D:/Analytics/logo.jpg")
st.image(image)

