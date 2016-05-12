#!/usr/bin/env gnuplot

# graph of pressure (and temperature)

# datafile
ifnameh = "/tmp/domod/mysql/sql23h.csv"
ifnamed = "/tmp/domod/mysql/sql23d.csv"
ifnamew = "/tmp/domod/mysql/sql23w.csv"
set output ofname = "/tmp/domod/site/img/day23.png"

# ******************************************************* General settings *****
set terminal png truecolor enhanced font "Vera" 9 size 1280,320
set datafile separator ';'
set datafile missing "NaN"    # Ignore missing values
set grid
tz_offset = utc_offset / 3600 # GNUplot only works with UTC. Need to compensate
                              # for timezone ourselves.
# Positions of split between graphs
LMPOS = 0.36
MRPOS = 0.73
RMARG = 0.96

# ********************************************************* Statistics (R) *****
# stats to be calculated here of column 2 (UX-epoch)
stats ifnameh using 2 name "X" nooutput

Xh_min = X_min + utc_offset - 946684800
Xh_max = X_max + utc_offset - 946684800

# stats to be calculated here for Y-axes
#stats ifnameh using 4 name "Y" nooutput
#Yh_min = Y_min * 0.90
#Yh_max = Y_max * 1.10

# ********************************************************* Statistics (M) *****
# stats to be calculated here of column 2 (UX-epoch)
stats ifnamed using 2 name "X" nooutput

Xd_min = X_min + utc_offset - 946684800
Xd_max = X_max + utc_offset - 946684800

# stats to be calculated here for Y-axes
#stats ifnamed using 4 name "Y" nooutput
#Yd_min = Y_min * 0.90
#Yd_max = Y_max * 1.10

# ********************************************************* Statistics (L) *****
# stats to be calculated here of column 2 (UX-epoch)
stats ifnamew using 2 name "X" nooutput
Xw_min = X_min + utc_offset - 946684800
Xw_max = X_max + utc_offset - 946684800

# stats for Y-axis
stats ifnamew using 3 name "Y" nooutput
Yw_min = Y_min -1
Yw_max = Y_max +1

# stats for Y2-axis
stats ifnamew using 4 name "Y2" nooutput
Y2w_min = Y2_min -1
Y2w_max = Y2_max +1

set multiplot layout 1, 3 title "Pressure & Temperature (BMP183) ".strftime("( %Y-%m-%dT%H:%M )", time(0)+utc_offset)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                       LEFT PLOT: past week
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# ***************************************************************** X-axis *****
set xlabel "past week"       # X-axis label
set xdata time               # Data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%a %d"            # Display time in 24 hour notation on the X axis
set xrange [ Xw_min : Xw_max ]

# ***************************************************************** Y-axis *****
set ylabel "Pressure [mbar]"
set yrange [ Yw_min : Yw_max ]

# **************************************************************** Y2-axis *****
set y2label " "
set y2tics format " "
set y2range [ Y2_min : Y2_max ]

# ***************************************************************** Legend *****
set key inside top left horizontal box
set key samplen 1
set key reverse Left

# ***************************************************************** Output *****
set arrow from graph 0,graph 0 to graph 0,graph 1 nohead lc rgb "red" front
# set arrow from graph 1,graph 0 to graph 1,graph 1 nohead lc rgb "green" front
#set object 1 rect from screen 0,0 to screen 1,1 behind
#set object 1 rect fc rgb "#eeeeee" fillstyle solid 1.0 noborder
#set object 2 rect from graph 0,0 to graph 1,1 behind
#set object 2 rect fc rgb "#ffffff" fillstyle solid 1.0 noborder
set rmargin at screen LMPOS

# ***** PLOT *****
plot ifnamew \
      using ($2+utc_offset):4 title " Temperature [degC]" axes x1y2  with points pt 5 ps 0.2 fc rgb "#cc99bb99" \
  ,'' using ($2+utc_offset):3 title " Pressure [mbar]"    with points pt 5 ps 0.2 fc rgb "#ccbb0000" \



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                     MIDDLE PLOT:  past day
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# ***************************************************************** X-axis *****
set xlabel "past day"       # X-axis label
set xdata time               # Data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xrange [ Xd_min : Xd_max ]

# ***************************************************************** Y-axis *****
set ylabel " "
set ytics format " "
set yrange [ Yw_min : Yw_max ]

# **************************************************************** Y2-axis *****
set y2label " "
set y2tics format " "
set y2range [ Y2_min : Y2_max ]

# ***************************************************************** Legend *****
unset key

# ***************************************************************** Output *****
set arrow from graph 0,graph 0 to graph 0,graph 1 nohead lc rgb "black" front
set lmargin at screen LMPOS+0.001
set rmargin at screen MRPOS

# ***** PLOT *****
plot ifnamed \
      using ($2+utc_offset):4 axes x1y2 with points pt 5 ps 0.2 fc rgb "#cc99bb99" \
  ,'' using ($2+utc_offset):3 with points pt 5 ps 0.2 fc rgb "#ccbb0000" \

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                      RIGHT PLOT: past hour
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# ***************************************************************** X-axis *****
set xlabel "past hour"       # X-axis label
set xdata time               # Data on X-axis should be interpreted as time
set timefmt "%s"             # Time in log-file is given in Unix format
set format x "%R"            # Display time in 24 hour notation on the X axis
set xrange [ Xh_min : Xh_max ]
set xtics textcolor rgb "red"

# ***************************************************************** Y-axis *****
set ylabel " "
set ytics format " "
set yrange [ Yw_min : Yw_max ]

# **************************************************************** Y2-axis *****
set y2label "Temperature [degC]"
set y2tics format "%.0f"
set y2range [ Y2_min : Y2_max ]
set y2tics border

# ***************************************************************** Legend *****
unset key

# ***************************************************************** Output *****
set arrow from graph 1,graph 0 to graph 1,graph 1 nohead lc rgb "green" front
set lmargin at screen MRPOS+0.001
set rmargin at screen RMARG

# ***** PLOT *****
plot ifnameh \
      using ($2+utc_offset):4 axes x1y2 with points pt 5 ps 0.2 fc rgb "#cc99bb99" \
  ,'' using ($2+utc_offset):3 with points pt 5 ps 0.2 fc rgb "#ccbb0000" \

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                                                                 FINALIZING
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

unset multiplot
