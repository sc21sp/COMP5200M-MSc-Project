import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import streamlit as st
from mplsoccer import Pitch, VerticalPitch, add_image, FontManager, Sbopen
from statsbombpy import sb
from urllib.request import urlopen
import cmasher as cmr
from PIL import Image
from highlight_text import ax_text


st.set_page_config(
    page_title = "Pass Network",
    page_icon = "🕸️"
)


st.markdown("<h1 style='text-align: center'>Pass Network</h1>", unsafe_allow_html=True)

events = sb.competitions()

st.markdown("<h3 style='text-align: center'>Available Match Data for Real Madrid</h1>", unsafe_allow_html=True)
evnts = events[['competition_id','competition_name']]

comp = st.selectbox(
    'Select a Competition',
    evnts['competition_name'].unique())

season = st.selectbox(
    'Select a Season',
    events['season_name'].unique())
st.write(comp,season)

select_match = st.selectbox(
    'Select Match',
    matches)
    
if st.button("Generate pass network"):

    parser = Sbopen()
    events, related, freeze, players = parser.event(select_match)
    TEAM = 'Real Madrid'
    OPPONENT = f'versus  La Liga {season}'
    st.dataframe(events)
    events.loc[events.tactics_formation.notnull(), 'tactics_id'] = events.loc[
        events.tactics_formation.notnull(), 'id']
    events[['tactics_id', 'tactics_formation']] = events.groupby('team_name')[[
        'tactics_id', 'tactics_formation']].ffill()

    formation_dict = {1: 'Ter Stegen', 2: 'Roberto', 3: 'Pique', 4: 'CB', 5: 'Umtiti', 6: 'Alba', 7: 'RWB',
                    8: 'LWB', 9: 'RDM', 10: 'Busquets', 11: 'LDM', 12: 'RM', 13: 'Rakitic',
                    14: 'CM', 15: 'Iniesta', 16: 'LM', 17: 'Messi', 18: 'RAM', 19: 'CAM',
                    20: 'LAM', 21: 'Suarez', 22: 'RCF', 23: 'Alcacer', 24: 'LCF', 25: 'SS'}

    players['pos'] = players.position_id.map(formation_dict)

    sub = events.loc[events.type_name == 'Substitution',
                    ['tactics_id', 'player_id', 'substitution_replacement_id',
                    'substitution_replacement_name']]
    players_sub = players.merge(sub.rename({'tactics_id': 'id'}, axis='columns'),
                                on=['id', 'player_id'], how='inner', validate='1:1')
    players_sub = (players_sub[['id', 'substitution_replacement_id', 'pos']]
                .rename({'substitution_replacement_id': 'player_id'}, axis='columns'))
    players = pd.concat([players, players_sub])
    players.rename({'id': 'tactics_id'}, axis='columns', inplace=True)
    players = players[['tactics_id', 'player_id', 'pos']]

    events = events.merge(players, on=['tactics_id', 'player_id'], how='left', validate='m:1')
    
    events = events.merge(players.rename({'player_id': 'pass_recipient_id'},
                                        axis='columns'), on=['tactics_id', 'pass_recipient_id'],
                        how='left', validate='m:1', suffixes=['', '_receipt'])

    FORMATION = 433
    pass_cols = ['id', 'pos', 'pos_receipt']
    passes_formation = events.loc[(events.team_name == TEAM) & (events.type_name == 'Pass') &
                                (events.tactics_formation == FORMATION) &
                                (events.pos_receipt.notnull()), pass_cols].copy()
    location_cols = ['pos', 'x', 'y']
    location_formation = events.loc[(events.team_name == TEAM) &
                                    (events.type_name.isin(['Pass', 'Ball Receipt'])) &
                                    (events.tactics_formation == FORMATION), location_cols].copy()

    # Calculating average location of players on the pitch
    average_locs_and_count = (location_formation.groupby('pos')
                            .agg({'x': ['mean'], 'y': ['mean', 'count']}))
    average_locs_and_count.columns = ['x', 'y', 'count']

    # Calculating passes exchanged between each position
    passes_formation['pos_max'] = (passes_formation[['pos',
                                                    'pos_receipt']]
                                .max(axis='columns'))
    passes_formation['pos_min'] = (passes_formation[['pos',
                                                    'pos_receipt']]
                                .min(axis='columns'))
    passes_between = passes_formation.groupby(['pos_min', 'pos_max']).id.count().reset_index()
    passes_between.rename({'id': 'pass_count'}, axis='columns', inplace=True)

    passes_between = passes_between.merge(average_locs_and_count, left_on='pos_min', right_index=True)
    passes_between = passes_between.merge(average_locs_and_count, left_on='pos_max', right_index=True,
                                        suffixes=['', '_end'])

    MAX_LINE_WIDTH = 18
    MAX_MARKER_SIZE = 3000
    passes_between['width'] = (passes_between.pass_count / passes_between.pass_count.max() *
                            MAX_LINE_WIDTH)
    average_locs_and_count['marker_size'] = (average_locs_and_count['count']
                                            / average_locs_and_count['count'].max() * MAX_MARKER_SIZE)


    MIN_TRANSPARENCY = 0.3
    color = np.array(to_rgba('white'))
    color = np.tile(color, (len(passes_between), 1))
    c_transparency = passes_between.pass_count / passes_between.pass_count.max()
    c_transparency = (c_transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency


    pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
    fig.set_facecolor("#22312b")
    pass_lines = pitch.lines(passes_between.x, passes_between.y,
                            passes_between.x_end, passes_between.y_end, lw=passes_between.width,
                            color=color, zorder=1, ax=ax)
    pass_nodes = pitch.scatter(average_locs_and_count.x, average_locs_and_count.y,
                            s=average_locs_and_count.marker_size,
                            color='red', edgecolors='black', linewidth=1, alpha=1, ax=ax)
    for index, row in average_locs_and_count.iterrows():
        pitch.annotate(row.name, xy=(row.x, row.y), c='white', va='center',
                    ha='center', size=16, weight='bold', ax=ax)

    st.write(fig)

with st.expander(f"Pass Network"):
    st.write('In a pass network diagram, each player is represented by a node, and the arrows between the nodes represent passes between players. The thickness of the arrow can represent the frequency of passes between those players, with thicker arrows indicating a higher number of passes. The direction of the arrow shows the direction that the pass was made, and the length of the arrow can represent the distance of the pass.')
    st.write('''Lines between players represent passes that were attempted
            The size of a player's dot indicates the number of passes they attempted
            The thickness of a line between players indicates the number of passes attempted between them''')
