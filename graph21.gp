#!/usr/bin/env gnuplot

# graph of temperature

# datafile
ifname = "/tmp/sql21.csv"
ofname = "/tmp/domod/site/img/day21.png"

# ******************************************************* General settings *****
set terminal png truecolor enhanced font "Vera" 9 size 1040,320
set datafile separator ';'
set datafile missing "NaN"    # Ignore missing values
set grid
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.
set timestamp 'created: %Y-%m-%d %H:%M' bottom font "Vera,6"

# ************************************************************* Statistics *****
# stats to be calculated here of column 2 (UX-epoch)
stats ifname using 2 name "X" nooutput

X_min = X_min + utc_offset - 946684800
X_max = X_max + utc_offset - 946684800

# stats to be calculated here for Y-axis
stats ifname using 4 name "Y" nooutput
Y_min = Y_min * 0.90
Y_max = Y_max * 1.10

# ****************************************************************** Title *****
set title "Temperature"
#"-".utc_offset."-"

# ***************************************************************** X-axis *****
set xlabel "Date/Time"       # X-axis label
set xdata time               # Data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xtics rotate by 40 right
set xrange [ X_min : X_max ]

# ***************************************************************** Y-axis *****
set ylabel "Temperature [degC]"
#set yrange [10:20]
#set autoscale y
set yrange [ Y_min : Y_max ]

# **************************************************************** Y2-axis *****
# set y2label "Temperature [degC]"
# set autoscale y2
# set y2tics border

# ***************************************************************** Legend *****
set key outside bottom center horizontal box
set key samplen .5
set key reverse Left

# ***************************************************************** Output *****
set arrow from graph 0,graph 0 to graph 0,graph 1 nohead lc rgb "red" front
#set arrow from graph 1,graph 0 to graph 1,graph 1 nohead lc rgb "green" front
set object 1 rect from screen 0,0 to screen 1,1 behind
set object 1 rect fc rgb "#eeeeee" fillstyle solid 1.0 noborder
set object 2 rect from graph 0,0 to graph 1,1 behind
set object 2 rect fc rgb "#ffffff" fillstyle solid 1.0 noborder
set output ofname

# ***** PLOT *****
plot ifname  using ($2+utc_offset):3 title " Temperature [degC]" with points pt 5 ps 0.1 fc rgb "#ccbb0000" \
