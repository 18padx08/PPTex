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
\end{document}
```
