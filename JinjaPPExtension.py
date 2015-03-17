#!/usr/bin/python
from os import sys
import os
import fcntl

sys.path += ['/usr/texbin','', '//anaconda/lib/python27.zip', '//anaconda/lib/python2.7', '//anaconda/lib/python2.7/plat-darwin', '//anaconda/lib/python2.7/plat-mac', '//anaconda/lib/python2.7/plat-mac/lib-scriptpackages', '//anaconda/lib/python2.7/lib-tk', '//anaconda/lib/python2.7/lib-old', '//anaconda/lib/python2.7/lib-dynload', '//anaconda/lib/python2.7/site-packages', '//anaconda/lib/python2.7/site-packages/PIL', '//anaconda/lib/python2.7/site-packages/setuptools-2.1-py2.7.egg']

from jinja2 import nodes, contextfunction
from jinja2.ext import Extension
from jinja2 import Environment, FileSystemLoader
import numpy as np
import scipy as sp
from sympy import Symbol, sympify, lambdify, latex
from scipy.interpolate import interp1d
import matplotlib.pyplot as plot
import subprocess



class PPExtension(Extension):
    tags = set(['figure', 'table', 'evaluate', 'evaltex'])
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
            body = parser.parse_statements(['name:endfigure'], drop_needle=True)
            return nodes.CallBlock(self.call_method('_create_figure', arg),[], [], body).set_lineno(linnum)
        elif(lineno.value == 'table'):
            arg = [parser.parse_expression()]
            return nodes.Output([self.call_method('_print_latex_table', arg)])
        elif(lineno.value == 'evaluate'):
            arg = [parser.parse_expression()]
            return nodes.Output([self.call_method('_evaluate_function', arg)])
        elif(lineno.value == 'evaltex'):
            arg = [parser.parse_expression()]
            return nodes.Output([self.call_method('_evaltex_function', arg)])


        #body = parser.parse_statements(['name:endfigure'], drop_needle=True)
        return nodes.Const(None)

    def _evaltex_function(self, data):
        s = sympify(data['function'])
        l = latex(s)
        s = s.doit()
        #print(latex(s))
        vals = []
        syms = []
        for symbol in data['symbols']:
            syms.append(Symbol(symbol['sym']))
            vals.append(symbol['val'])
        #print(syms, vals)
        my_function = lambdify(syms,s, 'numpy')
        result = my_function(*vals)
        #print(str(result))
        #print(l + " = " + str(result))
        return l + " = " + str(result)

# dictionary with entries
# data
#   |_ [xdata, ydata, desc]
# xlabel
# ylabel
    def _print_latex_table(self, data):
        if 'extended' in data:
            #we have in xdata an array and there is an array xheader and yheader (optional otherwise same as xheader) where xheader matches size of xdata and yheader matches size of one entry array of xdata
            #at least one entry
            ylen = len(data['xdata'][0])
            #since len(xheader) and len (xdata) should match we take xheader
            xlen = len(data['xheader'])

            #the xheader string (since latex builds tables per row)
            yheader = data['yheader']
            xheader = "&" if len(yheader) >0 else ""
            #xheader += "&".join(data['xheader'])
            isfirst = True
            for h in data['xheader']:
                if isfirst:
                    xheader += "\\textbf{" + str(h) + "}"
                    isfirst = False
                else:
                    xheader += "&\\textbf{" + str(h) + "}"
            table = '\\begin{figure}\\centering\\begin{tabular}{' + 'c' * (xlen+ (1 if len(yheader) > 0 else 0)) +'}'
            #table += "\\hline\n"
            table += xheader + "\\\\\n\\cline{2-" + str(xlen+1) + "}"
            print(ylen)
            #now iterate over all rows, remember to print in the first row the yheader if there is one
            for i in xrange(0, ylen):
                if(len(yheader) > 0):
                    table += "\\multicolumn{1}{r|}{\\textbf{" + str(data['yheader'][i]) + "}}"
                for o in xrange(0,xlen):
                    print("[",o, i,"]")
                    if o == xlen-1:
                        table += "&\multicolumn{1}{r|}{" + str(data['xdata'][o][i]) + "}"
                    else:
                        table += "&" + str(data['xdata'][o][i])
                table += "\\\\\\cline{2-"  + str(xlen+1) + "}\n"

            table += "\\end{tabular} \\caption{" + data['desc'] + "} \\end{figure}\n"
            print (table)
        else:
            for tab in data['data']:
                table = "\\begin{figure}\\centering\\begin{tabular}{|c|c|}"
                i = 0
                table += "\\hline\n"
                table += str(data['xlabel']) + " & " + str(data['ylabel']) + "\\\\\n"
                table += "\\hline\n"
                for entry in tab['xdata']:
                    table += str(entry) + " & " + str(tab['ydata'][i]) + "\\\\\n"
                    table += "\\hline\n"
                    i+=1
                table += "\\end{tabular} \\caption{" + str(tab['desc']) + "} \\end{figure}\n"
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

#dictionary for evaluating functions
#   variables - [] (use default values as initialization of data)
#   function - str
    def _evaluate_function(self, data):
        funcstr = """\
def evalFunc(""" + ",".join(data['variables']) +"""):
    return {e}""".format(e=data['function'])
        exec(funcstr)
        return evalFunc()

env = Environment(extensions=[PPExtension], loader=FileSystemLoader('.'))
t = env.get_template(sys.argv[2])
f = open(sys.argv[2] + "tmp", 'w')
f.write(t.render())
cmdstr = "/usr/texbin/xelatex -interaction=nonstopmode " + sys.argv[1] + " " + f.name
f.close()
print subprocess.Popen( cmdstr, shell=True, stdout=subprocess.PIPE ).stdout.read()
#os.system("open " + os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".pdf")
