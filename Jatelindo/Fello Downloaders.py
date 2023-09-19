import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.dates import date2num
import numpy as np

#Read CSV files
downloader_fello_ios = pd.read_csv("Downloader Fello iOS.csv", sep=";")
downloader_fello_and = pd.read_csv("Downloader Fello Android.csv", sep=";")

#Taking the day and month from the table axes
tanggal = list(downloader_fello_ios["Tanggal"])
tanggal = [str(x) for x in tanggal]
bulan_no = [str(x) for x in np.arange(1, len(downloader_fello_ios.columns[1:])+1)]

#Combining the day and month into a single date
date = [y + "/" + x + "/2023" for x in bulan_no for y in tanggal]

#List of downloaders per day
downloader_num_ios = [downloader_fello_ios.iloc[int(y)-1, int(x)] for x in bulan_no for y in tanggal]
downloader_num_and = [downloader_fello_and.iloc[int(y)-1, int(x)] for x in bulan_no for y in tanggal]

#Adding together iOS and Android downloaders
downloader_num = [sum(x) for x in zip(downloader_num_ios, downloader_num_and)]

#Making a dataframe from the previous lists; from wide data to long data
downloader_fello = pd.DataFrame({"Date": date, "Downloaders iOS":downloader_num_ios, "Downloaders Android":downloader_num_and, "Downloaders": downloader_num}).dropna()

downloader_fello["Date"] = [dt.datetime.strptime(x, "%d/%m/%Y") for x in downloader_fello["Date"]]

#Plot 1: Line graph of a determined period of time
#Determine the start and end date of the plot, as well as the downloader type
start_date = dt.datetime(2023,5,1)
end_date = dt.datetime(2023,5,30)

downloader_type = "Downloaders iOS"

#Making the line graph
date_plot = downloader_fello["Date"][(downloader_fello["Date"] >= start_date)
                                    & (downloader_fello["Date"] <= end_date)]
downloader_plot = downloader_fello[downloader_type][(downloader_fello["Date"] >= start_date)
                                    & (downloader_fello["Date"] <= end_date)]

plt.plot(date_plot, downloader_plot)
plt.show()

#Plot 2: Line graph over the course of the whole year, with the start of each month demarcated
plt.figure(figsize=(30,5))
for x in bulan_no:
    plt.axline((date2num(dt.datetime(2023,int(x),1)),0),
               (date2num(dt.datetime(2023,int(x),1)),1),
               c='red', ls='--')
plt.title("Jumlah Downloader Fello Januari-Agustus 2023", fontsize=18)
plt.annotate("Awal bulan ditandai oleh garis merah.",
              fontsize = 12,
              xy = (0.995,0.95), xycoords = "axes fraction",
              horizontalalignment = "right",
              bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))
plt.plot(downloader_fello["Date"], downloader_fello["Downloaders"])