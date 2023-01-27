import streamlit as st
import numpy as np
from urllib.request import urlopen
import matplotlib.pyplot as plt
from PIL import Image
from mplsoccer import PyPizza, add_image, FontManager
import pandas as pd

st.set_page_config(
    page_title = "Player Plots",
    page_icon = "📊"
)

st.markdown("<h1 style='text-align: center'>Player Analysis</h1>", unsafe_allow_html=True)


font_normal = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/"
                           "Roboto%5Bwdth,wght%5D.ttf?raw=true"))
font_italic = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/"
                           "Roboto-Italic%5Bwdth,wght%5D.ttf?raw=true"))
font_bold = FontManager(("https://github.com/google/fonts/blob/main/apache/robotoslab/"
                         "RobotoSlab%5Bwght%5D.ttf?raw=true"))

data = pd.read_csv(r'D:/Analytics/scouting.csv')

css_file = "D:\Analytics\styles.css"
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    player1 = st.selectbox(
        'Select Player 1',
        data['Player'].unique()
    )
    season1 = st.select_slider(
        'Season 1',
        data['scouting_period'].unique()
    )

with col2:
    player2 = st.selectbox(
        'Select Player 2',
        data['Player'].unique()
    )
    season2 = st.select_slider(
        'Season 2',
        data['scouting_period'].unique()
    )



def player_chart(player,season):

    # parameter list
    params = ["Non-Penalty Goals", "npxG", "Total Shots","Assists","npxG + xA","Open Play\nShot Creating Actions",
                "Progressive\nPasses",
            "Dribbles Completed", "Pass Completion", "Touches", "Pressure Regains",
            "Tackles Made", "Blocks","Interceptions", "Aerial Win %"]

    vals = data.loc[(data['Player']==player) & (data['scouting_period'] == season)]['Percentile'].head(15)
    values = list(vals)

    # color for the slices and text
    slice_colors = ["#1A78CF"] * 5 + ["#FF9300"] * 5 + ["#D70232"] * 5
    text_colors = ["#000000"] * 10 + ["#F2F2F2"] * 5

    # instantiate PyPizza class
    baker = PyPizza(
        params=params,                  # list of parameters
        background_color="black",     # background color
        straight_line_color="#000000",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_color="#000000",    # color for last line
        last_circle_lw=1,               # linewidth of last circle
        other_circle_lw=0,              # linewidth for other circles
        inner_circle_size=20            # size of inner circle
    )

    # plot pizza
    fig, ax = baker.make_pizza(
        values,                          # list of values
        figsize=(8, 8.5),                # adjust the figsize according to your need
        color_blank_space="same",        # use the same color to fill blank space
        slice_colors=slice_colors,       # color for individual slices
        value_colors=text_colors,        # color for the value-text
        value_bck_colors=slice_colors,   # color for the blank spaces
        blank_alpha=0.4,                 # alpha for blank-space colors
        kwargs_slices=dict(
            edgecolor="#000000", zorder=2, linewidth=1
        ),                               # values to be used when plotting slices
        kwargs_params=dict(
            color="white", fontsize=11,
            fontproperties=font_normal.prop, va="center"
        ),                               # values to be used when adding parameter labels
        kwargs_values=dict(
            color="white", fontsize=11,
            fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="white",
                boxstyle="round,pad=0.2", lw=1
            )
        )                                # values to be used when adding parameter-values labels
    )

    # add title
    fig.text(
        0.515, 0.975, f"{player}", size=16,
        ha="center", fontproperties=font_bold.prop, color="red"
    )

    # add subtitle
    fig.text(
        0.515, 0.955,
        "Percentile Rank vs Top-Five League Forwards",
        size=13,
        ha="center", fontproperties=font_bold.prop, color="white"
    )

    # add credits
    CREDIT_1 = "Data: Statsbomb via FBREF"
    CREDIT_2 = "© Sameer Pathan"

    fig.text(
        0.99, 0.02, f"{CREDIT_1}\n{CREDIT_2}", size=9,
        fontproperties=font_italic.prop, color="white",
        ha="right"
    )

    # add text
    fig.text(
        0.34, 0.93, "Attacking        Possession       Defending", size=14,
        fontproperties=font_bold.prop, color="white"
    )

    # add rectangles
    fig.patches.extend([
        plt.Rectangle(
            (0.31, 0.9225), 0.025, 0.021, fill=True, color="#1a78cf",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.462, 0.9225), 0.025, 0.021, fill=True, color="#ff9300",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.632, 0.9225), 0.025, 0.021, fill=True, color="#d70232",
            transform=fig.transFigure, figure=fig
        ),
    ])
    st.pyplot(fig)





pic,info = st.columns(2)

with pic:
    player_chart(player1,season1)
    
with info:
    player_chart(player2,season2)

b1, b2 = st.columns(2)

with b1:
    if st.button('Download Player 1'):
        plt.savefig(f'plot_{player1}.png')

with b2:
    if st.button('Download Player 2'):
        plt.savefig(f'plot_{player2}.png')

with st.expander('Understanding the Chart'):
    st.write('These stats are represented in terms of percentile.')

st.subheader('Goals Scored by Season')
p1 = data.loc[data['Player']==player1].head()

goals = p1['Goals'].unique()

goals = pd.read_csv(r'D:/Analytics/goals.csv')
year = list(goals['scouting_period'])
goal = list(goals['Goals'])
st.bar_chart(goals)

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

st.subheader('Performance Variance')
st.line_chart(chart_data)

with st.expander(f"More about {player2}"):
    st.write('TransferMarket')

