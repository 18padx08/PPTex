#!/usr/bin/python
from os import sys


sys.path += ['/usr/texbin','', '//anaconda/lib/python27.zip', '//anaconda/lib/python2.7', '//anaconda/lib/python2.7/plat-darwin', '//anaconda/lib/python2.7/plat-mac', '//anaconda/lib/python2.7/plat-mac/lib-scriptpackages', '//anaconda/lib/python2.7/lib-tk', '//anaconda/lib/python2.7/lib-old', '//anaconda/lib/python2.7/lib-dynload', '//anaconda/lib/python2.7/site-packages', '//anaconda/lib/python2.7/site-packages/PIL', '//anaconda/lib/python2.7/site-packages/setuptools-2.1-py2.7.egg']

from jinja2 import nodes, contextfunction
from jinja2.ext import Extension
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError
import numpy as np
from sympy import Symbol, sympify, lambdify, latex
import sympy as sp
import matplotlib.pyplot as plot
import subprocess
import re

class PPException(Exception):
    pass


class PPExtension(Extension):
    tags = set(['figure', 'table', 'calcTable', 'evaluate', 'evaltex'])
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
        elif( lineno.value == 'calcTable'):
            arg = [parser.parse_expression()]
            return nodes.Output([self.call_method('_calcTable_function', arg)])


        #body = parser.parse_statements(['name:endfigure'], drop_needle=True)
        return nodes.Const(None)
    
    def _getValue(self, r,c,table, regExps):
        try:
            print("is it a value?")
            return np.round(float(table[r,c]), 6)
        except(ValueError):
            print("no it's not")
            #got string try parse it
            #for reg in regExps:
            val = self._parseValue(r,c,table[r,c],table, regExps)
            if val is not None: return val
            return 0
    
    def _parseValue(self, row, column, entry, table, regExps):
        value = 0
        print('sp lets try parse it')
        for reg in regExps:
            temp = reg.finditer(entry)
            cor= 0
            if temp:
                for match in temp:
                    tup = match.group().replace('$', '')
                    print(tup)
                    r,c = tup.split(',')
                    r = row if int(r) < 0 else r
                    c = column if int(c) < 0 else c
                    print(r,c)
                    tmpVal = str(self._getValue(r,c,table, regExps))
                    entry = entry[0:match.start()-cor] + tmpVal + entry[match.end()-cor:]
                    cor += len(match.group()) - len(tmpVal)
        try:
            value = eval(entry)
        except(Exception):
            return None
        return np.round(value, 6)

    def _calcTable_function(self, data):
        xheader = data['xheader']
        yheader = data['yheader']
        #build up the regex for formula $1,2$ means second row third column $(0:1,0:1)$ the rect (0,0) - (0,1) which yields an array with every entry putting them into an array with same dimension
        #                                                                                        |         |
        #                                                                                        (1,0) - (1,1)
        #replace every placeholder with the value, putting 0 if the index is not valid
        singleVal = re.compile('\$-?\d*,-?\d*\$')
        table = np.array(data['table'])
        print table
        for row in range(np.shape(table)[0]):
            print(row)
            for column in range(np.shape(table)[1]):
                print ("parse (",row,column,")")
                blub = []
                blub.append(singleVal)
                value = self._getValue(row, column, table, blub)
                print(value)
                table[row,column] = value
        datArr = {}
        print('table construction completed')
        datArr['extended'] = True
        datArr['xheader'] = xheader
        datArr['yheader'] = yheader
        datArr['xdata'] = []
        print('building up data array')
        for c in range(np.shape(table)[1]):
            print(c)
            datArr['xdata'].append(table[:,c].tolist())
        datArr['desc'] = data['desc']
        figstr = ''
        if 'figure' in data:
            print( data['figure'])
            for fig in data['figure']:
                xrow = int(fig['xrow'])
                yrow = int(fig['yrow'])
                print(xrow, yrow)
                xdata = table[:,xrow].astype(np.float)
                ydata = table[:,yrow].astype(np.float)
                print(xdata, ydata)
                xmin = np.min(xdata)
                print(xmin)
                xmax = np.max(xdata)
                ymin = np.min(ydata)
                ymax = np.max(ydata)
                print(xmin,xmax,ymin,ymax)
                rang = [xmin, xmax, ymin, ymax]
                print (rang)
                title = fig['title']
                desc = data['desc']
                ylabel = fig['ylabel']
                xlabel = fig['xlabel']
                ref = fig['ref']
                figureArray = {}
                figureArray['xdata'] = xdata.tolist()
                figureArray['ydata'] = ydata.tolist()
                figureArray['title'] = title
                figureArray['desc'] = desc 
                figureArray['range'] = rang
                if 'interpolate' in fig:
                    figureArray['dim'] = fig['dim']
                    figureArray['interpolate'] = fig['interpolate']
                    if 'slope' in fig:
                        figureArray['slope'] = fig['slope']
                print('try creating figure')
                figstr += self._create_figure(ref, {'data': [figureArray], 'ylabel':ylabel, 'xlabel':xlabel}, fig['caption'])
        print('try printing the table')
        return self._print_latex_table(datArr) + figstr

    def _evaltex_function(self, data):
        try:
            s = sympify(data['function'])
        except:
            raise TemplateSyntaxError("could not parse formula", 01)
        try:
            l = latex(s)
            s = s.doit()
        except:
            raise TemplateSyntaxError("could either not make latex output or simpify", 1)
        l2 = None
        #errors is ignoring step
        if 'step' in data:
            l2 = latex(s)
        #print(latex(s))
        vals = []
        syms = []
        indep = []
        unindep = []
        try:
            print(data['symbols'])
            for symbol in data['symbols']:
                print(symbol)
                print(symbol['sym'], symbol['val'])
                syms.append(Symbol(symbol['sym']))
                vals.append(symbol['val'])

                if 'indep' in symbol:
                    indep.append([syms[-1], symbol['uncert'], vals[-1]])
                else:
                    unindep.append([syms[-1], vals[-1]])
        except:
            raise TemplateSyntaxError("something went wrong parsing symbols", 100)
        #print(syms, vals)
        print(syms, vals, indep, s)
        try:
            my_function = lambdify(syms, s, 'numpy')
            result = my_function(*vals)
            print("check if error is set", result)
            if 'errors' in data:
                #start looping through all variables in an extra arra
                error_terms = 0
                partial_terms = []
                partial_terms_squared = []
                uncerts = []
                print(l + " = " + str(result))
                try:
                    for ind in indep:
                        #loop through variables
                        d = Symbol('s_' + ind[0].name)
                        partial = sp.diff(s, ind[0]) * d/s
                        partial_terms.append(partial)
                        partial_terms_squared.append(partial**2)
                        error_terms = error_terms + partial**2
                        uncerts.append([d, str(ind[1])])
                except:
                    raise TemplateSyntaxError("error on building up error_terms", 15)
                #make substitutions
                print("begin substitution", error_terms)

                error_terms = error_terms**0.5
                ptsv1 = []
                try:
                    for pt in partial_terms_squared:
                        ptsv = pt
                        print("substitution started" )
                        #substitue first all dependend variables
                        for ind in indep:
                            print(ind)
                            try:
                                ptsv = ptsv.subs(ind[0], ind[-1])
                                ptsv = ptsv.subs('s_' + ind[0].name, ind[1])
                            except:
                                raise TemplateSyntaxError("Could not substitued dependend var", 100)
                        for unind in unindep:
                            print(unind)
                            try:
                                ptsv = ptsv.subs(unind[0], unind[1])
                            except:
                                raise TemplateSyntaxError("Could not substitued undependend var", 100)
                        ptsv1.append(ptsv)
                except:
                    raise TemplateSyntaxError("the substitution failed for error calculation", 10)
                #error

                uval = sp.sqrt(sum(ptsv1))
                rresult = np.round(result, data['digits'] if 'digits' in data else 5)
                print(rresult)
                print(uval)
                error = (uval * result).round(data['digits'] if 'digits' in data else 5)
                print(rresult, error)
                return """\\(""" + (data['fname'] if 'fname' in data else "f") + """ = """ + l + """ = """ + str(rresult) + """ \pm """ + str(abs(error)) + (data['units'] if 'units' in data else "") + """\\)

                            Error is calculated according to standard error propagation:
                            
                            \\begin{dmath}
                            s_{""" + (data['fname'] if 'fname' in data else "f") +"""} = """ + latex(error_terms) + """ = """ + str(abs(error.round(data['digits'] if 'digits' in data else 5))) +(data['units'] if 'units' in data else "" )+  """
                            \\end{dmath}
                            with uncertainities: \\(""" + ",".join([latex(cert[0]) + ' = ' + cert[1]  for cert in uncerts])  +"""\\)
                            
                           """
            #print(result)
        except:
            raise TemplateSyntaxError("could not evaluate formula", 100)
        try:
            if 'supRes' in data:
                return l
            elif 'step' in data:
                return l + " = " + l2 + " = " + str(result)
            return l + " = " + str(result)
        except:
            raise TemplateSyntaxError("Malformed result...", 100)

# dictionary with entries
# data
#   |_ [xdata, ydata, desc]
# xlabel
# ylabel
    def _print_latex_table(self, data):
        if 'extended' in data:
            #we have in xdata an array and there is an array xheader and yheader (optional otherwise same as xheader) where xheader matches size of xdata and yheader matches size of one entry array of xdata
            #at least one entry
            print("latex print function", data)
            ylen = len(data['xdata'][0])
            #since len(xheader) and len (xdata) should match we take xheader
            xlen = len(data['xheader'])

            #the xheader string (since latex builds tables per row)
            yheader = data['yheader'] if 'yheader' in data else []
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
            #first = True
            #now iterate over all rows, remember to print in the first row the yheader if there is one
            for i in xrange(0, ylen):
                first = True
                if(len(yheader) > 0):
                    try:
                        table += "\\multicolumn{1}{r|}{\\textbf{" + str(data['yheader'][i]) + "}}"
                    except:
                        if i > len(data['yheader'])-1:
                            print("dimension of yheader is wrong")
                        print("ooooops there is an error in yheader")
                        raise TemplateSyntaxError("Yheader is wrong: probably inconsistencies in dimension", i)
                for o in xrange(0,xlen):
                    try:
                        if len(yheader) >0:
                            if o == xlen-1:
                                   table += "&\multicolumn{1}{c|}{" + str(data['xdata'][o][i]) + "}"
                            else:
                                print(data['xdata'][o][i])
                                table += "&" + str(data['xdata'][o][i])
                        else:
                             if not first:
                                 table += "&"
                             first = False
                             if o == xlen-1:
                                   table += "\multicolumn{1}{c|}{" + str(data['xdata'][o][i]) + "}"
                             else:
                                #print(data['xdata'][o][i])
                                table += str(data['xdata'][o][i])
                    except:
                        print("some error at: ", o, i)
                        raise TemplateSyntaxError("some error while parsing table data: ("+str(o)+","+str(i)+")" , o)
                        #raise PPException("Error while parsing datapoints, probably missing an entry; check dimensions")
                #print(table)
                table += "\\\\\\cline{2-"  + str(xlen+1) + "}\n"
            table += "\\end{tabular} \\caption{" + str(data['desc']) + "} \\end{figure}\n"
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
        slopeinter = ''
        #foreach data set in data print a figure
        for fig in data['data']:
            if 'range' in fig:
                plot.axis(fig['range'])
            if 'interpolate' in fig :
                f  = np.polyfit(fig['xdata'],fig['ydata'], fig['dim'] if 'dim' in fig else 1)
                print("slope-intercept",f[0])
                
                if 'slope' in fig:
                    slopeinter = "y = "+str(f[0]) + " + " + str(f[1])
                    #plot.annotate("y = " + f[0]+"*x + "+ f[1], xy=(1,1), xytext=(1,1.5), arrowprops=dict(facecolor='black', shrink=0.05),)
                f_n = np.poly1d(f)
                xnew = np.linspace(fig['range'][0], fig['range'][1], 10000)
                plot.plot(xnew, f_n(xnew), label = slopeinter)
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
        \\caption{"""+(caller().strip() if type(caller) is not str else caller.strip())+u""" \\label{fig:""" + title + """}}
        \\end{figure}\n"""
        #return nodes.

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
cmdstr = "xelatex -interaction=nonstopmode " + sys.argv[1] + " " + f.name
f.close()
print subprocess.Popen( cmdstr, shell=True, stdout=subprocess.PIPE ).stdout.read()
#os.system("open " + os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".pdf")
