#!/usr/bin/python -tt

import cairo
import os
import time
import datetime
import math
from pysqlite2 import dbapi2 as sqlite3

app_path = '/srv/www/lighttpd/hostmon/'

db_name = 'hostcheck.sqlite'
db_path = 'dbase/'

graph_path        = 'graph/'
graph_dot_width   = 2
graph_plot_width  = 12*24*graph_dot_width
graph_plot_height = 240
graph_width       = graph_plot_width + 75
graph_height      = 300
graph_left        = 50
graph_top         = 30
graph_font        = 'Liberation Sans'
graph_color_bg    = [1,1,1,1] # not transparent white
graph_color_text  = [0,0,0,1] # not transparent black

class HostGraph:
    """class for graph creation"""
    connection = 0
    cursor     = 0
    host_list  = 0
    today      = int(time.mktime(datetime.date.today().timetuple())) - 0*24*60*60

    def __init__(self):
        # db connect
        self.connection = sqlite3.connect(app_path + db_path + db_name)
        self.cursor = self.connection.cursor()
        # get host list
        self.cursor.execute("select * from hosts")
        self.host_list = self.cursor.fetchall()

    def check_dirs(self):
        for host in self.host_list:
            host_dir = app_path + graph_path + host[1]
            if not os.path.isdir(host_dir):
                os.mkdir(host_dir)

    def make_host_graph_24h(self, host, data):

        #print host
        host_dir = app_path + graph_path + host[1]

        # Setup Cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, graph_width, graph_height)
        ctx = cairo.Context(surface)

        ctx.set_line_width(1)
        ctx.set_source_rgb(graph_color_bg[0], graph_color_bg[1], graph_color_bg[2])
        ctx.rectangle(0, 0, graph_width, graph_height)
        ctx.fill()

        ctx.set_line_width(0.3)
        ctx.set_source_rgba(graph_color_text[0], graph_color_text[1], graph_color_text[2], 0.4)
        ctx.rectangle(graph_left, graph_top, graph_plot_width, graph_plot_height)
        ctx.stroke()

        for i in range(25):
            ctx.move_to(graph_left+i*12*graph_dot_width, graph_top + graph_plot_height)
            #print i, i%2, i/2, i//2
            ctx.line_to(graph_left+i*12*graph_dot_width, graph_top + graph_plot_height+5+(10*(1-i%2)))
            ctx.stroke()

        max = 0
        for ping in data.values():
            if ping > max:
                max = ping
                
        max = math.ceil(max)

        div = 12*int(time.strftime('%H', datetime.datetime.now().timetuple())) + int(time.strftime('%M', datetime.datetime.now().timetuple()))/5

        count = 0
        ctx.set_line_width(graph_dot_width/1.5)
        for i in range(12*24):
            i = i+1
            ping = data.get(self.today + 5*60*i)
            if ping:
                count = count + 1
                ctx.set_source_rgba(graph_color_text[0], graph_color_text[1], graph_color_text[2], 0.03)
                ctx.move_to(graph_left+i*graph_dot_width, graph_top + graph_plot_height - 1)
                ctx.line_to(graph_left+i*graph_dot_width, graph_top + 1)
                ctx.stroke()
                ctx.set_source_rgba(graph_color_text[0], graph_color_text[1], graph_color_text[2], 0.5)
                ctx.move_to(graph_left+i*graph_dot_width, graph_top + graph_plot_height - 1)
                ctx.line_to(graph_left+i*graph_dot_width, 1 + graph_top + graph_plot_height - (graph_plot_height*ping/max))
                ctx.stroke()

            if i == div:
                ctx.set_source_rgba(graph_color_text[0], graph_color_text[1], graph_color_text[2], 0.1)
                ctx.move_to(graph_left+i*graph_dot_width + graph_dot_width, graph_top + graph_plot_height - 1)
                ctx.line_to(graph_left+i*graph_dot_width + graph_dot_width, graph_top + 1)
                ctx.stroke()

        ctx.set_line_width(1)
        ctx.set_source_rgb(graph_color_text[0], graph_color_text[1], graph_color_text[2])
        ctx.move_to(graph_left, graph_top)
        ctx.line_to(graph_left, graph_top+graph_plot_height)
        ctx.line_to(graph_left+graph_plot_width, graph_top+graph_plot_height)
        ctx.stroke()

        ctx.move_to(graph_left, 20)
        ctx.select_font_face(graph_font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(13)
        ctx.set_source_rgba(graph_color_text[0], graph_color_text[1], graph_color_text[2], graph_color_text[3])
        ctx.show_text(host[1])
        ctx.select_font_face(graph_font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        dtime = time.strftime('%Y.%m.%d @ %H:%M (', datetime.datetime.now().timetuple()) + str(count*5/60) + 'h' + str(count*5%60) + 'm)'
        ctx.move_to(graph_left + graph_plot_width - ctx.text_extents(dtime)[4], 20)
        ctx.show_text(dtime)

        ctx.set_font_size(11)
        ctx.set_source_rgba(graph_color_text[0], graph_color_text[1], graph_color_text[2], 0.5)
        for i in range(13):
            ctx.move_to(2+graph_left+i*12*graph_dot_width*2, graph_top + graph_plot_height + 15)
            ctx.show_text(str(i*2))

        ctx.move_to(graph_left - ctx.text_extents(str(int(max)))[4] - 5, 38)
        ctx.show_text(str(int(max)))
        ctx.move_to(graph_left - ctx.text_extents('ms')[4] - 5, 50)
        ctx.show_text('ms')

        surface.write_to_png(host_dir + time.strftime('/%Y%m%d', datetime.datetime.fromtimestamp(self.today).timetuple()) + '.png')

    def make_graph_24h(self):
        for host in self.host_list:
            self.cursor.execute('select pg.time, ch.time_start from pings pg, checks ch where pg.id_check = ch.id and ch.time_start > ' + str(self.today) + ' and ch.time_start <= ' + str(self.today+24*60*60) + ' and pg.id_host = ' + str(host[0]))
            data = self.cursor.fetchall()
            pings = {}
            for ping in data:
                key = str(ping[1])
                key = key[:-2]+'00'
                pings[int(key)] = ping[0]
            self.make_host_graph_24h(host, pings)

hg = HostGraph()
hg.check_dirs()
hg.make_graph_24h()