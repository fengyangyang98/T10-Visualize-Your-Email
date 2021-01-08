from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Calendar, Sunburst, Radar, Scatter, Timeline, WordCloud
from pyecharts.globals import SymbolType
import random
import datetime

import utils

# the day's email number
def calendar_base(data, year) -> Calendar:
    c = (
        Calendar()
        .add(
            series_name="",
            yaxis_data=data, 
            calendar_opts=opts.CalendarOpts(range_=str(year)))
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(
                max_=11,
                min_=1,
                orient="horizontal",
                is_piecewise=True,
                pos_top="230px",
                pos_left="100px",
            ),
        )
    )
    return c

def sunburst_base(data) -> Sunburst:
    sunburst = (
        Sunburst(init_opts=opts.InitOpts(width="1000px", height="600px"))
        .add(
            series_name="", 
            data_pair=data, 
            radius=[0, "90%"])
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}"
            )
        )
    )
    return sunburst

def radar_base(data, email_max_number, copy_max_number, copied_max_number, receiver_max_num, mail_server_max_number) -> Radar:
    radar = (
        Radar(init_opts=opts.InitOpts(width="1280px", height="720px"))
        .add_schema(
            schema=[
                opts.RadarIndicatorItem(name="邮件数量", max_=email_max_number),
                opts.RadarIndicatorItem(name="含有抄送的邮件数量", max_=copy_max_number),
                opts.RadarIndicatorItem(name="被抄送的邮件数量", max_=copied_max_number),
                opts.RadarIndicatorItem(name="联系人数量", max_=receiver_max_num),
                opts.RadarIndicatorItem(name="服务器个数", max_=mail_server_max_number),
            ],
            splitarea_opt=opts.SplitAreaOpts(
                is_show=True
            ),
            textstyle_opts=opts.TextStyleOpts(color="#000000"),
        )
    )

    for mailbox in data:
        tot = 0
        for num in data[mailbox][0]:
            tot += num
        if num is not 0:
            radar.add(
                series_name=mailbox,
                data=data[mailbox],
                linestyle_opts=opts.LineStyleOpts(color=utils.randomColor(), width=1),
            )

    radar.set_series_opts(label_opts=opts.LabelOpts(is_show=False)).set_global_opts(
            legend_opts=opts.LegendOpts()
        )
        
    return radar
 
def scatter_base(data, mailbox, maxsize) -> Timeline:
    tl = Timeline()
    tl.add_schema(pos_right="10%", pos_left="50%", pos_bottom="87%")
    for i in range(1, 13):
        c = (
            Scatter()
            .add_xaxis(mailbox)
            .add_yaxis("Day", data[i][0])
            .add_yaxis("Night", data[i][1])
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-20)),
                visualmap_opts=opts.VisualMapOpts(type_="size", max_=maxsize, min_=1),
            )
        )
        tl.add(c, "{}月".format(i))    

    return tl

def wordcloud_base(data) -> WordCloud:
    c = (
        WordCloud()
        .add("", data, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
    )
    return c