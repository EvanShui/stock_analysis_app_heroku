#import alpha_vantage - grabs stock data
from alpha_vantage.timeseries import TimeSeries

#import Bokeh - visualization module
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.io import curdoc
from bokeh.models import HoverTool, OpenURL, TapTool, CustomJS, ColumnDataSource, Tool, Div, Button
from bokeh.models.widgets import Panel, Tabs, TextInput, Button, Paragraph, CheckboxButtonGroup
from bokeh.embed import components
from bokeh.events import ButtonClick
from bokeh.resources import INLINE
from bokeh.layouts import layout, row, column, widgetbox
from bokeh.models.widgets import RadioButtonGroup
from bokeh import events

#import bs4 - web scraping module
from bs4 import BeautifulSoup

#import datetime - object used for easy date manipulation and access
from datetime import date, timedelta

#import dateutil - used to find differences between datetime objects
from dateutil.relativedelta import *

#import json - data format used to send from bokeh graph to flask app
import json

#import numpy - creating arrays and find difference between datetime objects
import numpy as np

#import re - regular expressions for parsing through marketwatch articles
import re

#import time - ???
import time

#import urllib - creating urllib opener, used to pass to bs4 for web scraping.
import urllib.request

from app_folder.constants import *

def get_data(stock_ticker):
    ts = TimeSeries(key='VVKDMK4DCJUF1NQP', output_format='pandas')
    data, meta_data = ts.get_daily(symbol=stock_ticker, outputsize='full')
    return data,meta_data

data,meta_data = get_data(stock_ticker)

text_input = TextInput(value="NFLX")
text_input.css_classes = ["text-input"]
button = Button(label="main")
button2 = Button(label="submit")
button2.css_classes = ["button"]
output=Paragraph()
radio_button_group = RadioButtonGroup(
        labels=["1w", "1m", "3m", "6m", "1y", "5y"], active=5)
radio_button_group.css_classes = ["radio-button-group"]

# str -> lst
# Hard coded to specifically scrape the google website and returns a list of
# the website titles from the google search results given a string to initate
# the search query
def web_scraper(day, month, year):
    lst = []
    opener = urllib.request.build_opener()
    #use Mozilla because can't access chrome due to insufficient privileges
    #only use for google
    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    #url for search query
    url = "http://www.marketwatch.com/search?q=" + str(stock_ticker).upper() + "&m=Ticker&rpp=15&mp=2005&bd=true&bd=false&bdv=" + str(month) + "%2F" + str(day) + "%2F20" + str(year) + "&rs=true"
    page = opener.open(url)
    soup = BeautifulSoup(page, 'lxml')
    #use beauitful soup to find all divs with the r class, which essentially
    #is the same as finding all of the divs that contain each individiaul search

    soup_tuple_list = zip(soup.findAll(class_="searchresult"), soup.findAll(class_="deemphasized")[1:-1])
    #iterating through a tags which includes title and links
    #appends the title of each individual search result to a list
    #iterating through time published and publishing company
    #gets rid of the prev strings at the beginning and end of the resulting list
    for article, date in soup_tuple_list:
        print(article, date)
        try:
            time = date.contents[1][5:]
            time = re.findall(r'\|.[A-Za-z ]*', time)[0]
            info = date.contents[0].string + time
            article.a['target']="_blank"
            lst.append((article.a.encode("utf-8"),info))
        except:
            continue
    return lst

def data_to_CDS(stock_ticker, data, start_date):
    delta_days = np.busday_count(start_date, date.today())
    data['ticker'] = stock_ticker
    adjusted_data = data.tail(delta_days)
    source = ColumnDataSource(data=dict(
        date=np.array(adjusted_data['close'].index, dtype=np.datetime64),
        price=adjusted_data['close'].values,
        index=adjusted_data['ticker']
    ))
    return source

def data_to_CDS_y(data, start_date):
    delta_days = np.busday_count(start_date, date.today())
    adjusted_data = data['close'].tail(delta_days)
    return (np.array(adjusted_data.values).tolist(), [int(x) for x in (data.tail(1).values)[0]])

def y_min_max(data, index):
    delta_days = np.busday_count(dates[index], date.today())
    adjusted_data = data.tail(delta_days)
    maxVal = adjusted_data['close'].max()
    minVal = adjusted_data['close'].min()
    if minVal < 0:
        minVal = 0
    return ((minVal - 5), (maxVal + 5))


p = figure(x_axis_type="datetime", tools=tools_lst, width=1000, height = 500)
source = data_to_CDS(stock_ticker, data, delta_5_year)
p.line('date', 'price', source=source, line_width=2)

p.add_tools(HoverTool(tooltips=[
    ("date", "@date{%F}"),
    ("Price", "$@price{0.2f}")
    ],
    formatters={
        "date": "datetime"
    },
    mode="vline"
))

#finance_info = Div(text="""
#    <b>NFLX</b>
#    <div class='price'>
#        24.31
#    </div>
#""")

div = Div(text="""Click on the graph to display a list of financial articles on and before that date""", width=500, height=500)
div.css_classes = ["scroll-box"]

button_callback = CustomJS(args=dict(radio_button_group = radio_button_group, div=div, text_input=text_input, output=output, source=source),code="""
     output.text = ''
     div.text=''
     var ticker = text_input.value;
     jQuery.ajax({
        type: 'POST',
        url: '/update_y_data',
        data: {"ticker_sent": ticker},
        dataType: 'json',
        success: function (json_from_server) {
            var updated_price_list = json_from_server[ticker][0];
            var current_date_data = json_from_server[ticker][1];
            source.data['price'] = updated_price_list;
            var current_price = updated_price_list[updated_price_list.length-1]
            source.trigger('change');
            var actual_ticker = %r;
            radio_button_group.active = 5
            //finance_info.text = ("<b>" + ticker.toUpperCase() + "</b>")
            //finance_info.text = finance_info.text.concat("<div>" + current_price + "</div>")
        },
        error: function() {
            output.text = "Invalid Ticker"
        }
    });
    """ % (stock_ticker))

tap_callback = CustomJS(args=dict(div=div),code="""
    var x_coordinate = cb_obj['x']
    var myDate = new Date(Math.trunc(cb_obj['x']));
    var year = myDate.getYear() - 100;
    var month = myDate.getMonth() + 1;
    var day = myDate.getDate() + 1;
    jQuery.ajax({
        type: 'POST',
        url: '/get_articles',
        data: {"x_coord": x_coordinate, "day":day, "month":month,"year":year},
        dataType: 'json',
        success: function (json_from_server) {
            div.text = ""
            var list = json_from_server[x_coordinate]
            for(var i =0; i < list.length; i++){
                var article = list[i][0]
                var info = list[i][1]
                var line = "<p>" + article + "<br>" + info + "</p>"
                var lines = div.text.concat(line)
                div.text = lines
            }
            console.log("loading")
        },
        error: function() {
            alert("Oh no, something went wrong. Search for an error " +
                  "message in Flask log and browser developer tools.");
        }
    });
    """)


radio_button_callback = CustomJS(args=dict(fig=p), code="""
            var date_ints = %s;
            var active_button = cb_obj.active
            var stock_ticker = %r;
            console.log(active_button)
            jQuery.ajax({
                type: 'POST',
                url: '/resize_y_range',
                data: {"index": active_button},
                dataType: 'json',
                success: function (json_from_server) {
                    var test = json_from_server[active_button]
                    fig.y_range.start = test[0];
                    fig.y_range.end = test[1];
                    fig.x_range.start = date_ints[active_button]
                    fig.x_range.end = date_ints[6]
                },
                error: function() {
                    alert("Oh no, something went wrong. Search for an error " +
                          "message in Flask log and browser developer tools.");
                }
            });
        """ % (date_ints, stock_ticker))

p.js_on_event('tap', tap_callback)

button2.js_on_event(ButtonClick, button_callback)

radio_button_group.callback = radio_button_callback

lay_out = column(row(text_input, button2), radio_button_group, output, row(p,div))

curdoc().add_root(lay_out)

js,div=components(lay_out, INLINE)
