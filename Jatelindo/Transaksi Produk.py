import pandas as pd
import re
from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.dates import date2num

# Importing data. Using for loops as there are a lot of CSVs
var = vars()

transaksi_januari = pd.read_csv("Januari Transaksi.csv", header=0).rename(columns={"No HP": "NO HP"})
transaksi_januari = transaksi_januari[:-1]

for t in [("februari", "Februari Transaksi.csv"), ("maret", "Maret Transaksi.csv"), \
          ("april", "April Transaksi.csv"), ("mei", "Mei Transaksi.csv"), ("juni", "Juni Transaksi.csv")]:
    for x, y in [t]:
        var["transaksi_" + x] = pd.read_csv(y, header=0).rename(columns={"USER NAME": "NO HP"})
        var["transaksi_" + x] = var["transaksi_" + x][:-1]

# Row binding the data together into one Data Frame
bulan = ["januari", "februari", "maret", "april", "mei", "juni"]

transaksi_bulanan = transaksi_januari

for b in bulan[1:]:
    transaksi_bulanan = pd.concat([transaksi_bulanan, var["transaksi_" + b]], axis=0)

transaksi_bulanan["JENIS TRANSAKSI"] = transaksi_bulanan["NAMA PRODUK"]

for x in range(len(transaksi_bulanan)):
    if bool(re.search("Pulsa\s*", transaksi_bulanan["NAMA PRODUK"].iloc[x])) or\
    transaksi_bulanan["NAMA PRODUK"].iloc[x] in ["Halo Postpaid"]:
        transaksi_bulanan["JENIS TRANSAKSI"].iloc[x] = "Pulsa"
    elif transaksi_bulanan["NAMA PRODUK"].iloc[x] in ["Bayar BPJS Kesehatan", "Beli Token PLN", "Billing Payment", "PDAM Aetra",\
                                                     "PDAM Palyja", "Tagihan Listrik PLN", "Telkom Speedy Indihome", "Telkom Fixline"]:
        transaksi_bulanan["JENIS TRANSAKSI"].iloc[x] = "Bayar Tagihan"
    elif transaksi_bulanan["NAMA PRODUK"].iloc[x] in ["Charge", "Charge Merchant", "Pembayaran QRIS Off-us", "Pembayaran QRIS On-us",\
                                                      "Purchase"]:
        transaksi_bulanan["JENIS TRANSAKSI"].iloc[x] = "Purchase"
    elif transaksi_bulanan["NAMA PRODUK"].iloc[x] in ["Bank Transfer eMoney"]:
        transaksi_bulanan["JENIS TRANSAKSI"].iloc[x] =  "Topup"
    elif transaksi_bulanan["NAMA PRODUK"].iloc[x] in ["Transfer Member"]: 
        transaksi_bulanan["JENIS TRANSAKSI"].iloc[x] = "Transfer"
    elif transaksi_bulanan["NAMA PRODUK"].iloc[x] in["Ticket Purchase"]:
        transaksi_bulanan["JENIS TRANSAKSI"].iloc[x] = "Transportasi"

transaksi_bulanan["RUPIAH"] = [float(Decimal(re.sub(r'[^\d.]', '', x))) for x in transaksi_bulanan["RUPIAH"]]

transaksi_per_jenis = transaksi_bulanan.groupby(["JENIS TRANSAKSI"]).sum()[["RUPIAH", "JUMLAH TRANSAKSI"]].reset_index()

plt.pie(transaksi_per_jenis["RUPIAH"],
        labels=transaksi_per_jenis["JENIS TRANSAKSI"],
        autopct = "%0.2f%%",
        wedgeprops = {'edgecolor':'black'},
        textprops = {'fontsize':11})
plt.title("Nominal per Jenis Transaksi",
         fontsize=20)
plt.show()

plt.pie(transaksi_per_jenis["JUMLAH TRANSAKSI"],
        labels=transaksi_per_jenis["JENIS TRANSAKSI"],
        autopct = "%0.2f%%",
        wedgeprops = {'edgecolor':'black'},
        textprops = {'fontsize':10},
        startangle=115,
        pctdistance=0.7)
plt.title("Nominal per Jenis Transaksi",
         fontsize=20)
plt.show()

downloader_fello_ios = pd.read_csv("Downloader Fello iOS.csv", sep=";")
downloader_fello_and = pd.read_csv("Downloader Fello Android.csv", sep=";")

tanggal = list(downloader_fello_ios["Tanggal"])
tanggal = [str(x) for x in tanggal]
bulan_no = [str(x) for x in np.arange(1, len(downloader_fello_ios.columns[1:])+1)]

date = [y + "/" + x + "/2023" for x in bulan_no for y in tanggal]

downloader_num_ios = [downloader_fello_ios.iloc[int(y)-1, int(x)] for x in bulan_no for y in tanggal]
downloader_num_and = [downloader_fello_and.iloc[int(y)-1, int(x)] for x in bulan_no for y in tanggal]

downloader_num = [sum(x) for x in zip(downloader_num_ios, downloader_num_and)]

downloader_fello = pd.DataFrame({"Date": date, "Downloaders iOS":downloader_num_ios, "Downloaders Android":downloader_num_and, "Downloaders": downloader_num}).dropna()

downloader_fello["Date"] = [dt.datetime.strptime(x, "%d/%m/%Y") for x in downloader_fello["Date"]]

#Both are inclusive
start_date = dt.datetime(2023,5,1)
end_date = dt.datetime(2023,5,30)

downloader_type = "Downloaders iOS"

date_plot = downloader_fello["Date"][(downloader_fello["Date"] >= start_date)
                                    & (downloader_fello["Date"] <= end_date)]
downloader_plot = downloader_fello[downloader_type][(downloader_fello["Date"] >= start_date)
                                    & (downloader_fello["Date"] <= end_date)]

plt.plot(date_plot, downloader_plot)
plt.show()

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