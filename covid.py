import streamlit as st
import pandas as pd
import numpy as np
import urllib.request, json 
from datetime import date, timedelta
import pydeck as pdk
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import altair as alt


COVID_ILE_DE_FRANCE_DATASET_API = 'https://data.iledefrance.fr/api/records/1.0/search/?dataset=donnees-hospitalieres-relatives-a-lepidemie-de-covid-19-en-france&q=&rows=2920&sort=date&facet=date&facet=region_min&facet=nom_dep_min&facet=sex&exclude.sex=Homme&exclude.sex=Femme'
COVID_ILE_DE_FRANCE_DATASET_API_SEX_INCLUDED = 'https://data.iledefrance.fr/api/records/1.0/search/?dataset=donnees-hospitalieres-relatives-a-lepidemie-de-covid-19-en-france&q=&rows=2920&sort=date&facet=date&facet=countrycode_iso_3166_1_alpha3&facet=region_min&facet=nom_dep_min&facet=sex'
st.header('/nouh-rifai \'s works on data')

st.subheader('All my works are educational oriented. \n For further explanations or questions, don\'t hesitate contacting me via LinkedIn or Email')
#Add links with html

st.text('''
        Tho following work is a vizualisatio of an open source dataset. I took in consideration respecting the 5 principles for a good visualization, listed by M. Alberto CAIRO in his book 'Data visualization and The Truthful Art':
        1 - Truthful
        2 - Functionality
        3 - Beauty
        4 - Insightful
        5 - Enlightening
    ''')
#Respect of Ideal visualizations

STATES_COORD = {
    75 : {'lat': 48.8557954256, 'lon': 2.34411308321},
    77 : {'lat': 48.6281210472, 'lon': 2.93531969909},
    78 : {'lat': 48.8145000081, 'lon': 1.84526151273},
    91 : {'lat': 48.5174587303, 'lon': 2.24865517666},
    92 : {'lat': 48.8488903633, 'lon': 2.25051074841},
    93 : {'lat': 48.9083101579, 'lon': 2.48332622588},
    94 : {'lat': 48.7692936982, 'lon': 2.47462077077},
    95 : {'lat': 49.0821697186, 'lon': 2.12479545535},
}

def _get_lat(row):
    try:
        return STATES_COORD[int(row['Departement_Code'])]['lat']
    except:
        return 0

def _get_lon(row):
    try:
        return STATES_COORD[int(row['Departement_Code'])]['lon']
    except:
        return 0

@st.cache(ttl=60*60)
def load_data_covid_ile_de_france():
    data = ''
    with urllib.request.urlopen(COVID_ILE_DE_FRANCE_DATASET_API) as url:
        data = json.loads(url.read().decode())
    data = pd.DataFrame(data['records'][i]['fields'] for i in range(len(data['records'])))        
    data['date'] = pd.to_datetime(data['date'])
    data = data.rename(columns={'reg_code':'Region_Code',
                                'day_intcare_new':'Daily_New_Intensive_Care_Admissions',
                                'day_hosp_new':'Daily_New_Hospitalization',
                                'nom_dep_min':'Departement_Name',
                                'day_death_new':'Daily_Death_Cases',
                                'geo_point_2d':'Geo_Localisation',
                                'day_hosp':'Total_Currently_Hospitalization',
                                'day_intcare':'Total_Currently_Intensive_Care',
                                'tot_out':'Total_Return_Home_Cases',
                                'dep_code':'Departement_Code',
                                'tot_death':'Total_Death_Cases',
                                'date':'Date',
                                'day_out_new':'Daily_Return_Home_Cases'
                                })
    return data

def show_column_map(container,data,col,color):
    st.subheader(' '.join(col.split('_')))
    data['lat'] = data.apply(_get_lat,axis=1)
    data['lon'] = data.apply(_get_lon,axis=1)
    data['elevationValue'] = data[col]
    container.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=48.8,
            longitude=2.5,
            zoom=7.75,
            pitch=60,
            bearing=-24
        ),
        layers=
            pdk.Layer(
                'ColumnLayer',
                data=data,
                get_position='[lon, lat]',
                get_elevation='['+col+']',
                radius=1000,
                elevation_scale=1000,
                elevation_range=[0, 5000],
                pickable=True,
                extruded=True,
                get_fill_color=color
            )
        ,
        tooltip={"html": "<b>{Departement_Name}:</b> {elevationValue}", "style": {"color": "white"}}
    ))    





st.header('\n\n\tCovid-19 Ile-de-france Region')
st.subheader('Dataset')
columns_daily = ['Date','Departement_Code','Departement_Name','Daily_New_Hospitalization','Daily_New_Intensive_Care_Admissions','Daily_Death_Cases','Daily_Return_Home_Cases']
columns_total = ['Date','Departement_Code','Departement_Name','Total_Currently_Hospitalization','Total_Currently_Intensive_Care','Total_Death_Cases','Total_Return_Home_Cases']
st.text('''
    The dataset in this section is extracted from the official Île-de-France Region's open data platform.
    Link : https://data.iledefrance.fr/
''')
data_load_state = st.text('Loading data...')
df = load_data_covid_ile_de_france()
data_load_state.text('Done!')
st.text("This dataset is mainly about daily death cases, return home cases, hospitalizations and intensive care cases caused by Covid-19 virus in the 8 departements of Île-de-France Region.")
df_daily = df[columns_daily]
df_daily2 = df_daily
st.dataframe(df_daily.head(8))
st.text("It also includes some total stats such as total death cases, return home cases.")
df_total = df[columns_total]
st.dataframe(df_total.head(8))
st.subheader('Visualisations and Analysis of **Daily stats** :')
st.text('''
    I am going to plot two different figures in order to extract the maximum of information based on different kinds of analysis.
    The first figure is a 3d map showing Daily_New_Hospitalization, Daily_New_Intensive_Care_Admissions, Daily_Death_Cases and Daily_Return_Home_Cases in the 8 departements.
    I will provide a date selector, to choose which day you want to visualize.
''')

today = date.today()
col1, col2= st.columns(2)
d = col1.date_input("Selected day :", date(today.year, today.month, today.day-1))
choice = col2.selectbox('Selected Stats For Map Chart:', ['Daily New Hospitalization',
                                     'Daily New Intensive Care Admissions',
                                     'Daily Death Cases',
                                     'Daily Return Home Cases'
                                    ])
choice_t = '_'.join(choice.split(' '))
try:
    df_daily = df_daily[df_daily['Date'] == pd.to_datetime(d)][['Daily_New_Hospitalization', 'Daily_New_Intensive_Care_Admissions','Daily_Death_Cases', 'Daily_Return_Home_Cases', 'Departement_Code', 'Departement_Name']]
except KeyError:
    st.info("No data for this day")

if len(df_daily) == 0 :
    st.info("No data for this day")
else:    
    #Daily_New_Hospitalization orange : 255, 149, 0
    show_column_map(st,df_daily,choice_t,'[255, 149, 0]')


#Sum of hospitalizations in the past year    
dept_sum_hospitalizations_year = df_daily2.groupby('Departement_Code')['Daily_New_Hospitalization'].agg('sum').to_dict()

dept_sum_death_year = df_total.groupby('Departement_Code')['Total_Death_Cases'].agg(['max','min']).apply(lambda x:x['max']-x['min'],axis=1).to_dict()
df = df.sort_values('Date')
df['cumsum'] = df.groupby('Departement_Code')['Daily_New_Hospitalization'].transform(pd.Series.cumsum)
df['cumsum_death'] = df.groupby('Departement_Code')['Daily_Death_Cases'].transform(pd.Series.cumsum)
df['cumsum_return_home'] = df.groupby('Departement_Code')['Daily_Return_Home_Cases'].transform(pd.Series.cumsum)
df['cumsum_intensive_care'] = df.groupby('Departement_Code')['Daily_New_Intensive_Care_Admissions'].transform(pd.Series.cumsum)
#computing cumulative values ratios
df['Ratio_Death_Cases_Cumulative'] = df['cumsum_death'] / df['cumsum']
df['Ratio_Return_Home_Cases_Cumulative'] = df['cumsum_return_home'] / df['cumsum']
df['Ratio_Currently_Intensive_Care_Cumulative'] = df['cumsum_intensive_care'] / df['cumsum']

df['Ratio_Currently_Intensive_Care'] = df['Total_Currently_Intensive_Care'] / df['Total_Currently_Hospitalization']
df['Ratio_Death_Cases'] = df['Daily_Death_Cases'] / df['Total_Currently_Hospitalization']
df['Ratio_Return_Home_Cases'] = df['Daily_Return_Home_Cases'] / df['Total_Currently_Hospitalization']

st.subheader('Visualisations and Analysis of **Total stats** :')
st.write('''
    In general, comparison should be done with caution and based on more features such as local testing strategy, laboratory capacity, effectiveness of surveillance systems, hospital capacities and capabilities in term of ressources, and alot more.
''')
st.info('Select a departement in order to focus on its stats')

def plotMultilinesChart(df, title, choices):
    choice2 = st.selectbox(title, choices)
    choice_t2 = '_'.join(choice2.split(' '))
    def getBaseChart():
        """
        Creates a chart by encoding the Data along the X positional axis and rolling mean along the Y positional axis 
        The mark (bar/line..) can be decided upon by the calling function.
        """
        base = (
            alt.Chart(df)
            .encode(
                x=alt.X(
                    "Date:T",
                    axis=alt.Axis(title=None, format=("%b %Y"), labelAngle=0, tickCount=6),
                ),
                y=alt.Y(
                    choice_t2+":Q", axis=alt.Axis(title="")
                ),
            )
            .properties(width=500, height=400)
        )
        return base

    def getSelection():
        """
        This function creates a selection element and uses it to "conditionally" set a color for a categorical variable (stock).
        It return both the single selection as well as the Category for Color choice set based on selection 
        """
        radio_select = alt.selection_multi(
            fields=['Departement_Name'], name="Departement Name", 
        )

        stock_color_condition = alt.condition(
            radio_select, alt.Color('Departement_Name'+":N", legend=None), alt.value("lightgray")
        )
        stock_opacity_condition = alt.condition(
            radio_select, alt.value(1), alt.value(0.1)
        )
        return radio_select, stock_color_condition, stock_opacity_condition
        
    def createChart():
        """
        This function uses the "base" encoding chart to create a line chart.
        The highlight_stocks variable uses the mark_line function to create a line chart out of the encoding.
        The color of the line is set using the conditional color set for the categorical variable using the selection.
        The chart is bound to the selection using add_selection.
        It also creates a selector element of a vertical array of circles so that the user can select between stocks 
        """

        radio_select, stock_color_condition, stock_opacity_condition = getSelection()

        make_selector = (
            alt.Chart(df)
            .mark_circle(size=200)
            .encode(
                y=alt.Y("Departement_Name:N", axis=alt.Axis(title="Pick "+"Departement Name", titleFontSize=15)),
                color=stock_color_condition,
                opacity=stock_opacity_condition
            )
            .add_selection(radio_select)
        )

        base = getBaseChart()

        highlight_stocks = (
            base.mark_line(strokeWidth=2)
            .add_selection(radio_select)
            .encode(color=stock_color_condition, opacity=stock_opacity_condition)
        ).properties(title=choice2)

        return base, make_selector, highlight_stocks, radio_select

    def createTooltip(base, radio_select):
        """
        This function uses the "base" encoding chart and the selection captured.
        Four elements related to selection are created here
        """
        # Create a selection that chooses the nearest point & selects based on x-value
        nearest = alt.selection(
            type="single", nearest=True, on="mouseover", fields=["Date"], empty="none"
        )

        # Transparent selectors across the chart. This is what tells us
        # the x-value of the cursor
        selectors = (
            alt.Chart(df)
            .mark_point()
            .encode(
                x="Date:T",
                opacity=alt.value(0),
                tooltip=["Date:T"]
            )
            .add_selection(nearest)
        )


        # Draw points on the line, and highlight based on selection
        points = base.mark_point(size=5, dy=-10).encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        ).transform_filter(radio_select)
        

        # Draw text labels near the points, and highlight based on selection
        tooltip_text = base.mark_text(
            align="left",
            dx=-30,
            dy=-10,
            fontSize=15,
            fontWeight="bold",
            lineBreak = "\n",
            fill = 'white',
        ).encode(
            text=alt.condition(
                nearest, 
                alt.Text(choice_t2+":Q"), 
                alt.value(" "),
    
            ),
        ).transform_filter(radio_select)

    
            

        # Draw a rule at the location of the selection
        rules = (
            alt.Chart(df)
            .mark_rule(color="white", strokeWidth=2)
            .encode(
                x="Date:T",
            )
            .transform_filter(nearest)
        )
        return selectors, rules, points, tooltip_text

    base, make_selector, highlight_stocks, radio_select  = createChart()

    selectors, rules, points, tooltip_text  = createTooltip(base, radio_select)


    ### Bring all the layers together with layering and concatenation
    (make_selector | alt.layer(highlight_stocks, selectors, points,rules, tooltip_text ))

    


total_title = 'Selected Stats For Total Line Chart:'
ratio_title = 'Selected Stats For Ratio Line Chart:'
ratio_cumulative_title = 'Selected Stats For Ratio Of Cumulative Values Line Chart:'

total_choices = ['Total Currently Hospitalization',
                'Total Currently Intensive Care',
                'Total Death Cases',
                'Total Return Home Cases']
ratio_choices = ['Ratio Currently Intensive Care',
                'Ratio Death Cases',
                'Ratio Return Home Cases'
            ]
ratio_cumulative_choices = ['Ratio Currently Intensive Care Cumulative',
                'Ratio Death Cases Cumulative',
                'Ratio Return Home Cases Cumulative']

plotMultilinesChart(df_total, total_title, total_choices)

st.write('''
    We can vizualize the change and evolution in hospitalizations cases or total deaths cases. as shown above. However, it is not accurate enough in a comparison perspective, given the fact that not all departements have the same capabilities, or at least the same hospitalization rate.
''')

plotMultilinesChart(df, ratio_title, ratio_choices)
st.write('''
    Meanwhile, we can take advantage of available stats and compute some ratios such as currently intensive care cases per currently hospitalization cases which will describe wheather hospital work charge is high, medium or low.
''')


st.write('''
    We can also perform some of the same ratios, only this time with cumulative incidence.
''')
st.info('This plot determines the proportion that provides an estimate of the risk of belonging to a certain class in a specific period. (a year ago until the selected date)')
plotMultilinesChart(df, ratio_cumulative_title, ratio_cumulative_choices)
