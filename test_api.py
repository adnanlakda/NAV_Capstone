#pip install shiny
#pip install waiter
#shiny run --reload
from doctest import OutputChecker
from shiny import ui, render, App
import http.client, urllib.parse
import json
import pandas as pd


app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            #ui.input_select("website", "Choose a website:", {"independent" : "Kyiv Independent", "inform":"UKInform", "pravda":"Pravda", "[website_name]":"website_name"}),
            ui.input_select("website", "Choose a website:", {"API" : "Mediastack", "pravda":"Pravda"}),
            #ui.input_radio_buttons("use_file", "Use pre-existing data?", file_choices),
            ui.input_action_button("start", "Start"),
            ui.download_button("download_final", "Download", class_="btn-primary")
        ),
        ui.panel_main(
            #ui.output_text_verbatim("scrape", placeholder=True)
            ui.output_table("scrape_mediastack")
        )
    )
)

def server(input, output, session):
    @output
    @render.table
    @reactive.event(input.start)
    def scrape_mediastack():
        base_url = http.client.HTTPConnection('api.mediastack.com')

        params = urllib.parse.urlencode({
            'access_key': 'd9babc2a947d03f9b887715a6df56a7a',
            'categories': 'general',
            'keywords': 'Ukraine Russian',
            'languages': 'ar, en, fr, ru, zh',
            'sort': 'published_desc',
            'limit': 10,
    })
    
        conn.request('GET', "/v1/news?{}".format(params))

        res = conn.getresponse()
        data = res.read()
        return data.decode('utf-8')
    
    

app = App(app_ui, server)