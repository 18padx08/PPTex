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
