from alpha_vantage.timeseries import TimeSeries

from bokeh.resources import INLINE
from datetime import date, timedelta
from dateutil.relativedelta import *
import time


resources = INLINE
cdn_js=INLINE.render_js()
cdn_css=INLINE.render_css()
js_resources = resources.render_js()
css_resources = resources.render_css()

stock_ticker = "nflx"

delta_7_days = date.today() + relativedelta(days=-7)
delta_month = date.today() + relativedelta(months=-1)
delta_3_months = date.today() + relativedelta(months=-3)
delta_6_months = date.today() + relativedelta(months=-6)
delta_year = date.today() + relativedelta(years=-1)
delta_5_year = date.today() + relativedelta(years=-5)
dates = [delta_7_days, delta_month, delta_3_months,
        delta_6_months,delta_year, delta_5_year, date.today()]

#dates in integer form, used to set range on graph
date_ints = [date_int for date_int in map(lambda date: time.mktime(date.timetuple()) * 1000, dates)]
tools_lst = "pan,wheel_zoom,box_zoom,reset"
date_titles = ["week", "month", "3 months", "6 months", "1 year", "3 years"]
