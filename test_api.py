#pip install shiny
#pip install waiter
#shiny run --reload
from doctest import OutputChecker
from shiny import App, render, ui, reactive
import http.client, urllib.parse
import json
import pandas as pd
from waiter import wait

waiting_screen <- taglist(
    spin_flower(),
    h4("Text being generated...")
)

app_ui = ui.page_fluid(
    useWaiter(),
    #ui.input_file("original_excel", "Upload excel", accept=".xlsx"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            #ui.input_select("website", "Choose a website:", {"independent" : "Kyiv Independent", "inform":"UKInform", "pravda":"Pravda", "[website_name]":"website_name"}),
            ui.input_select("website", "Choose a website:", {"API" : "Mediastack", "inform":"UKInform", "pravda":"Pravda"}),
            ui.input_radio_buttons("use_file", "Use pre-existing data?", file_choices),
            ui.input_action_button("start", "Start"),
            ui.download_button("download_final", "Download", class_="btn-primary")
        ),
        ui.panel_main(
            #ui.output_text_verbatim("scrape", placeholder=True)
            ui.output_table("scrape")
        )
    )
    #ui.output_table("table")
)

server = function(input, output) {
    observeEvent(input$submit, {
        if (input$api_key == ""){
            showModel(modalDialog(title = "Error", "Please enter your API key then submit."))
        }else{
            waiter_show(html = waiting_screen, color = "black")
            # set up the API request
            import http.client, urllib.parse
            rs <- http.client.HTTPConnection('api.mediastack.com')

            # display the response to the user
            output$api_response <- renderText({
                rs$choices$text
            })
            waiter_hide()

        }
    }) 
    }








# run the shiny app -> will pop up interface
#shinyApp(ui=app_ui, server=server)
app = App(app_ui, server, debug=False)

def new_func(input):
    if input.website() == 'API':pp = App(app_ui, server, debug=False)