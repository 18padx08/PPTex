# PPTex
A Latex/Python interpreter for physics lab

Use this interpreter for fast latexing your physics protocols.
Here a simple example:
```Tex
\documentclass[a4paper,twoside,12pt]{article}
\usepackage{graphicx}
\begin{document}
\title{09. Absoluter Nullpunkt}
\maketitle
\section{Diskusion}
\section{Fehlerrechnung}
\section{Anhang}
\subsection{Diagramme und Tabellen}
Alle erhobenen Messdaten befinden sich in diesem Abschnitt \\
{% set eichLuft = {'data' : [{'xdata' : [96098.7632, 10], 'ydata' : [128.08, -7.32], 'range' : [0.0, 100000.0, -100.0,150.0], 'title' : 'Eichkurve', 'desc' : 'Messwerte fuer Eichkurve'}], 'xlabel' : 'Pa', 'ylabel' : 'mV' }  %}
{% table eichLuft %}
{% figure 'Eichpunkt Luftdruck',  eichLuft %}
Eichkurve fuer Piezo Kristall
{% endfigure %}
\(t_0 = \frac{-b + \sqrt{b^2 -4ac}}{2a} = {% evaluate {'variables' : ['a=-25498.77','b=-6396923.795','c=145990253.8'], 'function' : '(-b + np.sqrt(b**2 - 4* a *c))/(2*a)'}  %} \)
\end{document}
```
The formula.png images shows the result of the evaluation of the formula
This file was optimized for use with TeXworks on Mac OS X. For any other system please remove/adjust the sys.path according to where your files are.

Dependencies in this project include the following. Please install those through you favorite package-manager. For Windows Users, the packages neede are normaly included in the anaconda environment.
  - Numpy
  - Scypy
  - Sympy
  - Jinja2
  - Matplotlib

In the current form, the template file has to be in a subfolder of where the binary is. This seems to be because of restrictions in the Jinja2 Template Engine.

Additionaly to the standard tags available in Jinja I've added some custom ones.

### Custom Tags
In each section there is a short description of the parameter (normaly given as python dictionaries), and how the result may look like.
#### figure
Used for simple plotting data. Note that you can define variables in within the Jinja environment, so you can possibly sort your code.
##### parameters
figure needs two parameters. First the title of the graph (which is also used for the \label tag in latex), then the dicitionary holding all values for the graph. Note figure is a block, so you have to end it with endfigure accordingly. Everything in between the block will be written into the \caption of the \figure.

``` python
        {'data' : [
                  {
                   'xdata':[], #array holding the xvalues
                   'ydata' : [], #array holding the yvalues
                   'range' : [], #bounds of the graph, xmin xmax ymin ymax
                   'title' : 'string', #title used for the graph inline
                   'interpolate' : boolean, #could be any type (the parser matches if interpolate is present) draw a interpolation line, with numpy.polyfit (more like linear, quadratic, cubic,..., regression)
                   'dim' : integer #default=1, specifying the dimension of the interpolation polynom
                  }
        ], 'xlabel': 'string for the xlabel', 'ylabel' : 'stringfor ylabel on figure'}
```

##### example

Each entry in the array will be one dataset, which is displayed in the same figure. Note currentyly it's only possible to have multiple datasets with the same x-axis and y-axis.

```Tex
{%set absNull = {'data':
			[{'xdata' : [98.601,0],
			'ydata' : [95658.460,70505.541],
			'range' : [-280,100,0,100000],
			'title':'Measured points', 
			'interpolate' : True, 
			'desc' : 'Calibration function'}, 
			{'xdata' : [98.601,0],'ydata' : [95658.460,70505.541],'range' : [-280,100,0,100000],'title':'Absolute Zero', 'interpolate' : True},
			{'xdata':[-198.82],'ydata' : [19787.518], 'range' : [-280,100,0,100000], 'title' : 'Boiling point (estimated value)'},
			{'xdata' : [-196.27], 'ydata' : [19787.518], 'range' : [-280, 100,0,100000], 'title' : 'Boiling point (exact calculation)'}], 
			'xlabel' : 'Celsius', 
			'ylabel' : 'Pa'} 
%}

{% figure 'Absoluter Nullpunkt', absNull %}
Set of points for a) Calibration function b) determination of absolute zero c) Boiling point of Nitrogene. The line was linearly interpolated with scipy.
{% endfigure %}

```

#### evaluate [deprecated]
Takes a formula as a input and evaluates the numerical value. You should porbably better use evaltex, since evaltex is able to do symbolic calculations, and it also outputs nice latex code. Evaluate is only here for compatibility reasons.
The evaluate takes a python code as string, and a array of python default parameters and creates a function out of the string, which is then evaluated with exec.

##### python code and parameters
``` python
	{
	#dictionary for evaluating functions
#   variables - [] (use default values as initialization of data)
#   function - str
    def _evaluate_function(self, data):
        funcstr = """\
def evalFunc(""" + ",".join(data['variables']) +"""):
    return {e}""".format(e=data['function'])
        exec(funcstr)
        return evalFunc()
	}
	
	
	{
	'function' : 'string', # string representing python code which should be evaluated
	'variables': ['strings'] # array of strings in the form x=5
	}
```

##### example
```Tex
	{% evaluate {'function' : 'x**2 * np.sqrt(y)', 'variables': ['x=2', 'y=3']} %}
```

#### evaltex

#### table

#### calcTable
