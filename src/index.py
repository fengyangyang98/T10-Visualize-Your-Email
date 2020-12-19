from flask import Flask, render_template, request, redirect
import random
import datetime
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Calendar, Sunburst, Radar, Scatter, Timeline
from pyecharts.faker import Faker
import json
import jieba
from datetime import timedelta

from chart import *
from email_api import Email

STOPWORDS = [u'的', u'地', u'得', u'而', u'了', u'在', u'是', u'我', u'有', u'和', u'就',  u'不', u'人', u'都', u'一', u'一个', u'上', u'也', u'很', u'到', u'说', u'要', u'去', u'你',  u'会', u'着', u'没有', u'看', u'好', u'自己', u'这']
PUNCTUATIONS = [u'。', u'，', u'“', u'”', u'…', u'？', u'！', u'、', u'；', u'（', u'）', u'【', u'】', u'(', u')', u',', u'.', u'_', u'-', u'^', u'?', u'[', u']', u'{', u'}', u'「', u'」']   

app = Flask(__name__, static_folder="templates")

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

@app.route("/test")
def test():
    return render_template("graph/lo_gin.html")

@app.route("/")
def index():
    return render_template("graph/login.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        host = request.form['host']
        year = request.form['year']
    except:
        return redirect('/')

    return render_template("graph/charts.html", username=username, password=password, host=host, year=year)


@app.route("/charts", methods=['GET', 'POST'])
def get_charts():
    try:
        username = request.args['username']
        password = request.args['password']
        host = request.args['host']
        year = int(request.args['year'], 10)
    except:
        return None

    # login
    e = Email(host, username, password)
    e.login()

    # get the raw data
    status, mailboxs = e.getMailboxs()
    emails = {}
    for mailbox in mailboxs:
        status, emails[mailbox] = e.getEmailsIn(mailbox, year)
    begin, end = utils.getTimeThisYear(year)
    mailbox_idx = { mailboxs[i] : i for i in range(len(mailboxs))}

    # logout
    e.logout()

    # get calendar chart
    calendar_data = [
        [str(begin + datetime.timedelta(days=i)), 0]
        for i in range((end - begin).days + 1)
    ]

    sunburst_tmp_data = {'Morning' : {}, 'Noon' : {}, 'Afternoon' : {}, 'Night' : {}  }
    radar_data = {}

    email_max_number = 5
    copy_max_number = 5
    copied_max_number = 5
    receiver_max_num = 5
    mail_server_max_number = 5
    timeline_max = 5

    timeline_data = [ [ [0 for i in range(len(mailboxs))], [0 for i in range(len(mailboxs))] ]  for i in range(13)] 
    wordcloud_tmp_data = {}

    for mailbox in mailboxs:
        receiver = []
        mail_server = []
        email_number = 0
        copy_number = 0
        copied_number = 0

        idx = mailbox_idx[mailbox]
        for email in emails[mailbox]:
            # calendar
            calendar_data[( email[-1].date() - begin ).days][1] += 1 

            # sunburst
            period = 'Morning'
            recv_hour = email[-1].hour
            if recv_hour >= 8 and recv_hour <= 12:
                period = 'Morning'
            elif recv_hour >= 13 and recv_hour <= 14:
                period = 'Noon'
            elif recv_hour >= 15 and recv_hour <= 18:
                period = 'Afternoon'
            else:
                period = 'Night'
            email_pre, email_suffix = utils.getSuffix(email[1])

            if mailbox not in sunburst_tmp_data[period]:
                sunburst_tmp_data[period][mailbox] = {}

            if email_suffix not in sunburst_tmp_data[period][mailbox]:
                sunburst_tmp_data[period][mailbox][email_suffix] = 0

            sunburst_tmp_data[period][mailbox][email_suffix] += 1

            # radar
            receiver.append(email[1])
            receiver.append(email[2])

            email_pre, email_suffix = utils.getSuffix(email[1])
            mail_server.append(email_suffix)
            email_pre, email_suffix = utils.getSuffix(email[2])
            mail_server.append(email_suffix)

            email_number += 1
            if email[3] != '':
                copy_number += 1
            if username in email[3]:
                copied_number += 1

            # scatter
            if email[-1].hour >= 8 and email[-1].hour <= 17:
                timeline_data[email[-1].month][0][idx] += 1
            else:
                timeline_data[email[-1].month][1][idx] += 1

            timeline_max = max(timeline_max, timeline_data[email[-1].month][0][idx])
            timeline_max = max(timeline_max, timeline_data[email[-1].month][1][idx])

            # wordcloud
            seg_list = jieba.cut(email[0])
            for seg in seg_list:
                if seg not in STOPWORDS and seg not in PUNCTUATIONS:
                    if seg not in wordcloud_tmp_data:
                        wordcloud_tmp_data[seg] = 1
                    else:
                        wordcloud_tmp_data[seg] += 1

        receiver = set(receiver)
        mail_server = set(mail_server)

        receiver_num = len(receiver)
        mail_server_number = len(mail_server)

        radar_data[mailbox] = [[email_number, copy_number, copied_number, receiver_num, mail_server_number]]
            
        email_max_number = max(email_max_number, email_number)
        copy_max_number = max(copy_max_number, copy_number)
        copied_max_number = max(copied_max_number, copied_number)
        receiver_max_num = max(receiver_max_num, receiver_num)
        mail_server_max_number = max(mail_server_max_number, mail_server_number)

    # sunburst
    sunburst_data = []
    for period in sunburst_tmp_data:
        mailbox_list = []
        for mailbox in sunburst_tmp_data[period]:
            suffix_list = []

            for suffix in sunburst_tmp_data[period][mailbox]:
                suffix_list.append(opts.SunburstItem(name=suffix, value=sunburst_tmp_data[period][mailbox][suffix]))

            if len(mailbox) <= 15:
                mailbox_list.append(opts.SunburstItem(name=mailbox, children=suffix_list))
            else:
                mailbox_list.append(opts.SunburstItem(name='...' + mailbox[-12:-1], children=suffix_list))

        sunburst_data.append(opts.SunburstItem(name=period, children=mailbox_list))
    
    #wordcloud
    wordcloud_data = []
    for word in wordcloud_tmp_data:
        if wordcloud_tmp_data[word] >= 3:
            wordcloud_data.append((word, wordcloud_tmp_data[word]))

    # get the chart and  pages
    sunbudrt_chart = sunburst_base(sunburst_data)
    calendar_chart = calendar_base(calendar_data, begin.year)
    radar_chart = radar_base(
            radar_data, 
            email_max_number + 3, 
            copy_max_number + 3,
            copied_max_number + 3,
            receiver_max_num + 3,
            mail_server_max_number + 3)
    scatter_chart = scatter_base(timeline_data, mailboxs, timeline_max)
    wordcloud_chart = wordcloud_base(wordcloud_data)
            
    return '{ "calendar" : %s, "sunburst" : %s, "radar" : %s, "scatter" : %s, "wordcloud" : %s }' % (
                    calendar_chart.dump_options_with_quotes(),   
                    sunbudrt_chart.dump_options_with_quotes(), 
                    radar_chart.dump_options_with_quotes(),
                    scatter_chart.dump_options_with_quotes(),
                    wordcloud_chart.dump_options_with_quotes())

if __name__ == "__main__":
    app.run()

