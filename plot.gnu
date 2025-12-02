# === MULTI-PLOT FOR ALL CSVs (Kopi) - PLOT SEMUA KOLOM ===
# Script ini membuat 4 PNG otomatis, satu untuk setiap jenis kopi
# Data folder: SAMPLING_1_ROBUSTA (tanpa spasi)

set datafile separator ','
set datafile missing ''

# === BLOK 1: Kopi Arabika ===
set terminal pngcairo size 1600,900 enhanced font 'Arial,10'
set output 'Kopi_Arabika_20251126_104927_plot.png'
set title "Kopi Arabika - All Sensor Traces"
set xlabel 'Time (s)'
set ylabel 'Signal (a.u.)'
set grid
set style data lines
set key outside right top box
plot 'SAMPLING_1_ROBUSTA/Kopi_Arabika_20251126_104927.csv' skip 1 using 1:2 title "CO (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Arabika_20251126_104927.csv' skip 1 using 1:3 title "Ethanol (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Arabika_20251126_104927.csv' skip 1 using 1:4 title "VOC (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Arabika_20251126_104927.csv' skip 1 using 1:5 title "NO2 (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Arabika_20251126_104927.csv' skip 1 using 1:6 title "Ethanol (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Arabika_20251126_104927.csv' skip 1 using 1:7 title "VOC (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Arabika_20251126_104927.csv' skip 1 using 1:8 title "CO (GM)"
unset output

# === BLOK 2: Kopi Campuran ===
set terminal pngcairo size 1600,900 enhanced font 'Arial,10'
set output 'Kopi_Campuran_20251126_120403_plot.png'
set title "Kopi Campuran - All Sensor Traces"
set xlabel 'Time (s)'
set ylabel 'Signal (a.u.)'
set grid
set style data lines
set key outside right top box
plot 'SAMPLING_1_ROBUSTA/Kopi_Campuran_20251126_120403.csv' skip 1 using 1:2 title "CO (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Campuran_20251126_120403.csv' skip 1 using 1:3 title "Ethanol (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Campuran_20251126_120403.csv' skip 1 using 1:4 title "VOC (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Campuran_20251126_120403.csv' skip 1 using 1:5 title "NO2 (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Campuran_20251126_120403.csv' skip 1 using 1:6 title "Ethanol (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Campuran_20251126_120403.csv' skip 1 using 1:7 title "VOC (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Campuran_20251126_120403.csv' skip 1 using 1:8 title "CO (GM)"
unset output

# === BLOK 3: Kopi Luwak ===
set terminal pngcairo size 1600,900 enhanced font 'Arial,10'
set output 'Kopi_Luwak_20251126_112756_plot.png'
set title "Kopi Luwak - All Sensor Traces"
set xlabel 'Time (s)'
set ylabel 'Signal (a.u.)'
set grid
set style data lines
set key outside right top box
plot 'SAMPLING_1_ROBUSTA/Kopi_Luwak_20251126_112756.csv' skip 1 using 1:2 title "CO (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Luwak_20251126_112756.csv' skip 1 using 1:3 title "Ethanol (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Luwak_20251126_112756.csv' skip 1 using 1:4 title "VOC (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Luwak_20251126_112756.csv' skip 1 using 1:5 title "NO2 (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Luwak_20251126_112756.csv' skip 1 using 1:6 title "Ethanol (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Luwak_20251126_112756.csv' skip 1 using 1:7 title "VOC (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Luwak_20251126_112756.csv' skip 1 using 1:8 title "CO (GM)"
unset output

# === BLOK 4: Kopi Robusta ===
set terminal pngcairo size 1600,900 enhanced font 'Arial,10'
set output 'Kopi_Robusta_20251126_100834_plot.png'
set title "Kopi Robusta - All Sensor Traces"
set xlabel 'Time (s)'
set ylabel 'Signal (a.u.)'
set grid
set style data lines
set key outside right top box
plot 'SAMPLING_1_ROBUSTA/Kopi_Robusta_20251126_100834.csv' skip 1 using 1:2 title "CO (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Robusta_20251126_100834.csv' skip 1 using 1:3 title "Ethanol (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Robusta_20251126_100834.csv' skip 1 using 1:4 title "VOC (MCS)", \
      'SAMPLING_1_ROBUSTA/Kopi_Robusta_20251126_100834.csv' skip 1 using 1:5 title "NO2 (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Robusta_20251126_100834.csv' skip 1 using 1:6 title "Ethanol (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Robusta_20251126_100834.csv' skip 1 using 1:7 title "VOC (GM)", \
      'SAMPLING_1_ROBUSTA/Kopi_Robusta_20251126_100834.csv' skip 1 using 1:8 title "CO (GM)"
unset output

# === SELESAI ===
# 4 file PNG berhasil dibuat dengan SEMUA 8 kolom sensor ditampilkan!

