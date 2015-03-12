#!/usr/bin/python
from os import sys
import os
import fcntl

sys.path += ['', '//anaconda/lib/python27.zip', '//anaconda/lib/python2.7', '//anaconda/lib/python2.7/plat-darwin', '//anaconda/lib/python2.7/plat-mac', '//anaconda/lib/python2.7/plat-mac/lib-scriptpackages', '//anaconda/lib/python2.7/lib-tk', '//anaconda/lib/python2.7/lib-old', '//anaconda/lib/python2.7/lib-dynload', '//anaconda/lib/python2.7/site-packages', '//anaconda/lib/python2.7/site-packages/PIL', '//anaconda/lib/python2.7/site-packages/setuptools-2.1-py2.7.egg']

from jinja2 import nodes, contextfunction
from jinja2.ext import Extension
from jinja2 import Environment, FileSystemLoader
import numpy as np
import scipy as sp
from scipy.interpolate import interp1d
import matplotlib.pyplot as plot
import subprocess



class PPExtension(Extension):
    tags = set(['figure', 'table'])
    def __init(self, environment):
        super(PPExtension, self).__init__(environment)
        #add defaults
        environment.extend(error_calculation='gauss', data_mode='tuples', print_figure_for_each_table=True)

    def parse(self, parser):
        #the token
        lineno = parser.stream.next()
        linnum = lineno.lineno
        if(lineno.value == 'figure'):
            #ther argument
            arg = [parser.parse_expression()]
            #the figure data
            if (parser.stream.skip_if('comma')):
                arg.append(parser.parse_expression())
            #the x-axis legend
        #    if(parser.stream.skip_if('comma')):
        #        arg.append(parser.parse_expression())
            #the y-axis legend
        #    if(parser.stream.skip_if('comma')):
        #        arg.append(parser.parse_expression())
            #parse the body
            body = parser.parse_statements(['name:endfigure'], drop_needle=True)
            #print(body)
            #create the figure
            return nodes.CallBlock(self.call_method('_create_figure', arg),[], [], body).set_lineno(linnum)
        elif(lineno.value == 'table'):

            arg = [parser.parse_expression()]

            #body = parser.parse_statements(['name:endtable'], drop_needle=True)
            return nodes.Output([self.call_method('_print_latex_table', arg)]) #nodes.CallBlock(self.call_method('_print_latex_table', arg),[], [], body) .set_lineno(linnum)

        #body = parser.parse_statements(['name:endfigure'], drop_needle=True)
        return nodes.Const(None)


# dictionary with entries
# data
#   |_ [xdata, ydata, desc]
# xlabel
# ylabel
    def _print_latex_table(self, data):

        for tab in data['data']:
            table = "\\begin{figure}\\centering\\begin{tabular}{|c|c|}"
            i = 0
            table += "\\hline\n"
            table += data['xlabel'] + " & " + data['ylabel'] + "\\\\\n"
            table += "\\hline\n"
            for entry in tab['xdata']:
                table += str(entry) + " & " + str(tab['ydata'][i]) + "\\\\\n"
                table += "\\hline\n"
                i+=1
            table += "\\end{tabular} \\caption{" + tab['desc'] + "} \\end{figure}\n"
        return table





# dictionary with entries
# data
#   |_ (xdata,ydata,range = [xmin,xmax,ymin,ymax], title, interpolate)
# ylabel
# xlabel

    def _create_figure(self, title, data, caller):
        plot.figure()
        print (data)
        #foreach data set in data print a figure
        for fig in data['data']:
            if 'range' in fig:
                plot.axis(fig['range'])
            if 'interpolate' in fig :
                f  = np.polyfit(fig['xdata'],fig['ydata'], 1)
                f_n = np.poly1d(f)
                xnew = np.linspace(fig['range'][0], fig['range'][1], 10000)
                plot.plot(xnew, f_n(xnew))
            plot.plot(fig['xdata'], fig['ydata'], label=fig['title'], linestyle="solid", marker="s", markersize=7)
            plot.legend()
        plot.ylabel(data['ylabel'])
        plot.xlabel(data['xlabel'])

        file = plot.savefig(title.replace(" ","")+".png")
        print file
        return u"""
        \\begin{figure}[ht!]
        \centering
        \includegraphics[width=\\textwidth]{""" + title.replace(" ","")  + """.png}
        \\caption{"""+caller().strip()+u"""}
        \\end{figure}\n"""
        #return nodes.
    @contextfunction
    def calculateIntegral(val):
        return "the integral"


env = Environment(extensions=[PPExtension], loader=FileSystemLoader('.'))
t = env.get_template(sys.argv[2])
f = open(sys.argv[2] + "tmp", 'w')
f.write(t.render())
p = subprocess.Popen("xelatex " + " " + sys.argv[1] + " " + f.name , shell=True)
#os.system("open " + os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".pdf")
