WTF pymeter ?
-------------

Python Bolyfa-BF117 multimeter serial data dump tool

Amazon product page : https://www.amazon.fr/dp/B07MR2S95J/ref=cm_sw_em_r_mt_dp_-qh.Fb2Z6MSH4

How-to use
----------

Let’s say your multimeter is plugged and recognized as "/dev/ttyUSB0" device
(don’t forget to activate USB with a long-press on Rel/USB button on your multimeter :D )

  $ poetry install
  $ poetry shell
  $ ./bf117.py /dev/ttyUSB0

data can easily be converted into .csv, or plotted through gnuplot :

  gnuplot> plot 'yourdatafile' using 1:2 with linespoints
