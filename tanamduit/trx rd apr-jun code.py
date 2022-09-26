import numpy as np
import pandas as pd
import math as mt
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
from siuba import group_by, summarize, _, mutate, arrange
import dateutil as dtu
var = vars()
#%%
#Import two datasets 'TRX RD APRIL - JUNE 2022.csv' and 'Data AUM RD dan SBN as of balance 30 Apr 2022.csv'
#'TRX RD APRIL - JUNE 2022.csv' contains the transactions from Apr-Jun 2022
#'Data AUM RD dan SBN as of balance 30 Apr 2022.csv' contains data from the consumers
trx_rd = pd.read_csv('TRX RD APRIL - JUNE 2022.csv', sep = ";")
aum_rd = pd.read_csv('Data AUM RD dan SBN as of balance 30 Apr 2022.csv', sep = ";")

#Cleaning up data, ensuring data types are correct
trx_rd["Tanggal Transaksi"] = [dt.datetime.strptime(x, "%d/%m/%Y %H:%M") if type(x) == str else x for x in trx_rd["Tanggal Transaksi"]]
trx_rd["Jam Transaksi"] = [dt.datetime.time(x).hour for x in trx_rd["Tanggal Transaksi"]]
trx_rd["Hari Transaksi"] = [dt.datetime.date(x).day for x in trx_rd["Tanggal Transaksi"]]
trx_rd["Tanggal Transaksi"] = [dt.datetime.date(x) for x in trx_rd["Tanggal Transaksi"]]
trx_rd["Tanggal NAV"] = [dt.datetime.strptime(x, "%d/%m/%Y") if type(x) == str else x for x in trx_rd["Tanggal NAV"]]
trx_rd["Nominal"] = [x.replace(",",".") for x in trx_rd["Nominal"]] #Replace "," with "." in numbers
trx_rd["Unit"] = [x.replace(",",".") for x in trx_rd["Unit"]]
trx_rd = trx_rd.astype({"Nominal" : "float64", 
                        "Unit" : "float64"})

#Creating weekly bounds so that we can group dates by week
tahun_trx = list(set([x.year for x in trx_rd["Tanggal Transaksi"]]))
bulan_trx = list(set([x.month for x in trx_rd["Tanggal Transaksi"]]))
for x in tahun_trx:
    for y in bulan_trx:
        var["bounds" + "_" + str(x) + "_" + str(y)] = [dt.date(x, y, 1) + (n-1)*dt.timedelta(days = 7) for n in range(1,6)]

#Group dates by week    
minggu_trx = [y for x in trx_rd["Tanggal Transaksi"] for y in sum([var["bounds" + "_" + str(x) + "_" + str(y)] for x in tahun_trx for y in bulan_trx],[]) if (y <= x) & (y.month == x.month) & (y.year == x.year) & (x.day-y.day < 7)]
weeks_trx = ["Week " + str(int((x.day-1)/7 + 1)) + ", " +  str(x.month) + "/" + str(x.year) for x in minggu_trx]
weeks_trx = pd.DataFrame(minggu_trx, columns = ["Minggu Transaksi"])
trx_rd = pd.concat([trx_rd,weeks_trx], axis = 1)

#Select columns
trx_rd = pd.concat([trx_rd.loc[:,"Customer Id":"Tanggal Transaksi"], 
                    trx_rd.loc[:,"Hari Transaksi"], 
                    trx_rd.loc[:,"Minggu Transaksi"], 
                    trx_rd.loc[:,"Jam Transaksi"], 
                    trx_rd.loc[:,"Tanggal NAV":"Tipe"]], axis = 1)

#Separate transactions based on type of transaction: "SUBSCRIPTION", "REDEEM", "bulk"
trx_rd_bulk = trx_rd[trx_rd['Tipe'] == "bulk"]
trx_rd = trx_rd[trx_rd['Tipe'] != "bulk"]
trx_rd_sub = trx_rd[trx_rd['Jenis Transaksi'] == "SUBSCRIPTION"].reset_index(drop = True)
trx_rd_red = trx_rd[trx_rd['Jenis Transaksi'] == "REDEEM"].reset_index(drop = True)
trx_rd_swi = trx_rd[trx_rd['Jenis Transaksi'] == "SWITCHING"].reset_index(drop = True)

#Cleaning up the aum_rd dataset
aum_rd = pd.concat([aum_rd.loc[:,"customer_id":"first_trx_date"], aum_rd.loc[:,"aum_rd"], aum_rd.loc[:,"customer_type"]],
         axis = 1)
aum_rd["kyc_date"] = [dt.datetime.strptime(x, "%m/%d/%y") if pd.notna(x) else x for x in aum_rd["kyc_date"]]
aum_rd["first_trx_date"] = [dt.datetime.strptime(x, "%m/%d/%y %H:%M") if pd.notna(x) else x for x in aum_rd["first_trx_date"]]
aum_rd["aum_rd"] = [x.replace(",",".") if pd.notna(x) else x for x in aum_rd["aum_rd"]]
aum_rd = aum_rd.astype({"aum_rd" : "float64"})

#Adding age to aum_rd
age = [dt.datetime.strptime(x, "%m/%d/%y") if pd.notna(x) else x for x in aum_rd["date_of_birth"]]
age = [x.replace(year = x.year - 100) if (x.year > 2022) else x for x in age if (pd.notna(x))]
age = [dt.datetime(2022, 6, 30) - x if pd.notna(x) else x for x in age]
age = [mt.floor(x.days/365.25) if pd.notna(x) else x for x in age]
age_bracket = ["19 ke bawah" if x >= 16 and x <= 19 else "20-29" if x >= 20 and x <= 29 else "30-39" if x >= 30 and x <= 39 else "40-49" if x >= 40 and x <= 49 else "50-59" if x >= 50 and x <= 59 else "60-69" if x >= 60 and x <= 69 else "70 ke atas" for x in age]
age_bracket = pd.DataFrame(age_bracket, columns = ["age_bracket"])
aum_rd = pd.concat([aum_rd, age_bracket], axis = 1)

#Adding the number of days from first transaction to aum_rd
days_from_first = [(dt.datetime(2022,6,30) - x).days if pd.notna(x) else x for x in aum_rd["first_trx_date"]]
days_from_first = pd.DataFrame(days_from_first, columns = ["days_from_first"])
aum_rd = pd.concat([aum_rd, days_from_first], axis = 1)
aum_rd = aum_rd.rename(columns = {"customer_id" : "Customer Id"})
#%%
#Group by Day of Transaction and sum the subscription transactions in each day
trx_rd_sub_sum = (trx_rd_sub
                    .groupby(by = "Hari Transaksi").sum()["Customer Id"]
                    .reset_index())

#Plot the transaction sum over time
fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.lineplot(x = "Hari Transaksi", y = "Customer Id", data = trx_rd_sub_sum, ax = ax, color = "black")
sns.scatterplot(x = "Hari Transaksi", y = "Customer Id", data = trx_rd_sub_sum, ax = ax, color = "tab:blue")
plt.title("Total AUM Pembelian untuk Setiap Tanggal", fontsize = 20)
plt.xlabel("Tanggal", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

plt.annotate("Tanggal 1,\n{}".format(trx_rd_sub_sum.set_index("Hari Transaksi").loc[1,"Customer Id"]),
             xy = (1, trx_rd_sub_sum.set_index("Hari Transaksi").loc[1,"Customer Id"]), xycoords = 'data',
             fontsize = 20, xytext = (0.34,0.89), 
             horizontalalignment='center', textcoords = 'axes fraction',
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"),
             arrowprops = dict(arrowstyle="->",
                    connectionstyle="angle3,angleA=180,angleB=-20"))
plt.annotate("Tanggal 8,\n{}".format(trx_rd_sub_sum.set_index("Hari Transaksi").loc[8,"Customer Id"]),
             xy = (8, trx_rd_sub_sum.set_index("Hari Transaksi").loc[8,"Customer Id"]), xycoords = 'data',
             fontsize = 20, xytext = (0.34,0.79), 
             horizontalalignment='center', textcoords = 'axes fraction',
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"),
             arrowprops = dict(arrowstyle="->",
                    connectionstyle="angle3,angleA=220,angleB=25"))
plt.annotate("Tanggal 27,\n{}".format(trx_rd_sub_sum.set_index("Hari Transaksi").loc[27,"Customer Id"]),
             xy = (27, trx_rd_sub_sum.set_index("Hari Transaksi").loc[27,"Customer Id"]), xycoords = 'data',
             fontsize = 20, xytext = (0.64,0.84), 
             horizontalalignment='center', textcoords = 'axes fraction',
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"),
             arrowprops = dict(arrowstyle="->",
                    connectionstyle="angle3,angleA=10,angleB=25"))

#Group by Day of Transaction and sum the redeem transactions in each day
trx_rd_red_sum = (trx_rd_red
                    .groupby(by = "Hari Transaksi").sum()["Customer Id"]
                    .reset_index())

#Plot the transaction sum over time
fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.lineplot(x = "Hari Transaksi", y = "Customer Id", data = trx_rd_red_sum, ax = ax, color = "black")
sns.scatterplot(x = "Hari Transaksi", y = "Customer Id", data = trx_rd_red_sum, ax = ax, color = "tab:blue")
plt.title("Total AUM Penjualan untuk Setiap Tanggal", fontsize = 20)
plt.xlabel("Tanggal", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

plt.annotate("Tanggal 8,\n{}".format(trx_rd_red_sum.set_index("Hari Transaksi").loc[8,"Customer Id"]),
             xy = (8, trx_rd_red_sum.set_index("Hari Transaksi").loc[8,"Customer Id"]), xycoords = 'data',
             fontsize = 20, xytext = (0.47,0.89), 
             horizontalalignment='center', textcoords = 'axes fraction',
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"),
             arrowprops = dict(arrowstyle="->",
                    connectionstyle="angle3,angleA=180,angleB=-25"))

#%%
#Get first transaction date for each customer that transacted in Apr-Jun 2022
trx_rd_retention = (pd.DataFrame((trx_rd_sub.copy()
                                  .sort_values(by = "Tanggal Transaksi")
                                  .merge(aum_rd[aum_rd["customer_type"] == "individual"], how = "outer", on = "Customer Id")
                                  .groupby(by = ["Customer Id"])["first_trx_date"].apply(set)))
                    .reset_index())

#Get list of all dates when customers transacted in Apr-Jun 2022
trx_rd_retention = trx_rd_retention.merge(
                    (pd.DataFrame(trx_rd_sub.copy()
                                  .sort_values(by = "Tanggal Transaksi")
                                  .merge(aum_rd, how = "left", on = "Customer Id")
                                  .groupby(by = ["Customer Id"])["Tanggal Transaksi"].apply(list))),
                    how = "left", on = "Customer Id")

#Convert from set to a singular date time
trx_rd_retention["first_trx_date"] = [list(x)[0] for x in trx_rd_retention["first_trx_date"]]
#If "first_trx_date" is NA use the first date where they transacted in Apr-Jun 2022
#As aum_rd only has data up until the 30th of April, then there will understandably be some NAs
trx_rd_retention["first_trx_date"] = [trx_rd_retention["Tanggal Transaksi"][x][0]
                                      if (pd.isna(trx_rd_retention["first_trx_date"][x])) &
                                     (type(trx_rd_retention["Tanggal Transaksi"][x]) == list)
                                      else trx_rd_retention["first_trx_date"][x]
                                      for x in range(len(trx_rd_retention))]
trx_rd_retention = trx_rd_retention[[type(x) == pd._libs.tslibs.timestamps.Timestamp 
                                     for x in trx_rd_retention["first_trx_date"]]].reset_index(drop = True)

#Determine the Start Year of their transactions
trx_rd_retention["Start Year"] = ["Pre-April 2022" if x.month < 4 else "Post-April 2022"
                                  if x.year == 2022 
                                  else x.year 
                                  for x in trx_rd_retention["first_trx_date"]]

#Determine if their last transaction is Recent or Not Recent
#Recent if within Apr-Jun 2022                                  
trx_rd_retention["Recent"] = ["Recent" if type(x) == list else "Not Recent"
                              for x in trx_rd_retention["Tanggal Transaksi"]]

#Find proportion of Recent and Not Recent per Start Year    
trx_rd_retention1 = trx_rd_retention.copy()
trx_rd_retention2 = trx_rd_retention1[(_["Recent"] == "Not Recent") & (_["Start Year"] == "Post-April 2022")]
trx_rd_retention = (trx_rd_retention
                    .groupby(by = ["Start Year", "Recent"])
                    .count()["Customer Id"]
                    .reset_index()
                    .rename(columns = {"Customer Id":"Count"})
                    .merge((trx_rd_retention
                            .groupby(by = "Start Year")
                            .count()["Customer Id"]
                            .reset_index()
                            .rename(columns = {"Customer Id":"Total"})),
                            how = "left",
                            on = "Start Year") >>
                    mutate(Prop = _["Count"]/_["Total"]*100))

#Plot proportion of customers with Recent and Not Recent transactions based on their Start Year
fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_rd_retention[_["Start Year"] != "Post-April 2022"],
            x = "Start Year", y = "Count", hue = "Recent", ax = ax)
plt.title("Proporsi Nasabah yang Masih Transaksi, Dibagi Berdasarkan Tahun Transaksi Pertamanya", fontsize = 20)
plt.xlabel("Tahun Transaksi Pertama", fontsize = 20)
plt.ylabel("Jumlah Nasabah", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)
plt.legend(prop = {"size":18})

for x in range(len(set(trx_rd_retention["Start Year"][_ != "Post-April 2022"]))):
    y = list(set(trx_rd_retention["Start Year"][_ != "Post-April 2022"]))
    plt.annotate("{t}\n({p}%)".format(t = trx_rd_retention.query("`Start Year` == @y[@x] and `Recent` == \"Recent\"")["Count"].iloc[0], 
                                     p = trx_rd_retention.query("`Start Year` == @y[@x] and `Recent` == \"Recent\"")["Prop"].iloc[0].round(2)),
                 fontsize = 14, xy = (x+0.2,
                                      trx_rd_retention.query("`Start Year` == @y[@x] and `Recent` == \"Recent\"")["Count"].iloc[0]+150), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "None"))
    
for x in range(len(set(trx_rd_retention["Start Year"][_ != "Post-April 2022"]))):
    y = list(set(trx_rd_retention["Start Year"][_ != "Post-April 2022"]))
    plt.annotate("{t}".format(t = trx_rd_retention.query("`Start Year` == @y[@x] and `Recent` == \"Not Recent\"")["Count"].iloc[0]),
                 fontsize = 14, xy = (x-0.2,
                                      trx_rd_retention.query("`Start Year` == @y[@x] and `Recent` == \"Not Recent\"")["Count"].iloc[0]+150), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "None"))

#Plot proportion of customers with Recent transactions based on their Start Year    
fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_rd_retention[(_["Start Year"] != "Post-April 2022") & (_["Recent"] == "Recent")],
            x = "Start Year", y = "Prop", hue = "Recent", ax = ax, palette = ["tab:orange"])
plt.title("Proporsi Nasabah yang Masih Transaksi, Dibagi Berdasarkan Tahun Transaksi Pertamanya", fontsize = 20)
plt.xlabel("Tahun Transaksi Pertama", fontsize = 20)
plt.ylabel("Proporsi", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(set(trx_rd_retention["Start Year"][_ != "Post-April 2022"]))):
    y = list(set(trx_rd_retention["Start Year"][_ != "Post-April 2022"]))
    plt.annotate("{p}%".format(p = trx_rd_retention.query("`Start Year` == @y[@x] and `Recent` == \"Recent\"")["Prop"].iloc[0].round(2)),
                 fontsize = 14, xy = (x,
                                      trx_rd_retention.query("`Start Year` == @y[@x] and `Recent` == \"Recent\"")["Prop"].iloc[0]+0.2), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "None"))
#%%
#List out all dates of each transaction 
trx_post_kyc = ((trx_rd_sub >>
                 mutate(Tipe = ["normal" for x in range(len(trx_rd_sub))]))
                .reset_index(drop = True))
trx_post_kyc = (trx_post_kyc
                  .sort_values(by = "Tanggal Transaksi")
                  .groupby(by = "Customer Id")["Tipe"]
                  .apply(list)
                  .reset_index()
                  .assign(Tanggal = 
                         list((trx_post_kyc
                              .sort_values(by = "Tanggal Transaksi")
                              .groupby(by = "Customer Id")["Tanggal Transaksi"]
                              .apply(list)
                              .reset_index(drop = True))))
                  .rename(columns = {"Tanggal":"Tanggal Transaksi"})
                  .merge(aum_rd.loc[:,["Customer Id", "first_trx_date"]], 
                        how = "left", on = "Customer Id"))

#If "first_trx_date" is NA use the first date where they transacted in Apr-Jun 2022
#As aum_rd only has data up until the 30th of April, then there will understandably be some NAs
trx_post_kyc["first_trx_date"] = [trx_post_kyc["first_trx_date"][x]
                                    if (type(trx_post_kyc["first_trx_date"][x]) == pd._libs.tslibs.timestamps.Timestamp)
                                    else trx_post_kyc["Tanggal Transaksi"][x][0]
                                    for x in range(len(trx_post_kyc))]

#Determine if the first transaction is in Apr-Jun and how many afterwards
trx_post_kyc["First Trx in Apr-Jun"] = [trx_post_kyc["first_trx_date"][x] == trx_post_kyc["Tanggal Transaksi"][x][0]
                                          for x in range(len(trx_post_kyc))]
trx_post_kyc["No. Trx After First"] = [len(x)-1 for x in trx_post_kyc["Tipe"]]

#Get all available months and years
months_year = [[int(a) for a in z.split(", ")] 
               for z in set([str(y.month) + ", " + str(y.year) 
                             for x in trx_post_kyc["Tanggal Transaksi"] 
                             for y in x])]

#Check if any transactions occured within every month and year combination
for x in sorted(months_year):
    trx_post_kyc[str(x[0]) + ", " + str(x[1])] = [any([z.month == x[0] for z in y]) for y in trx_post_kyc["Tanggal Transaksi"]]

#Determine number of months as a customer
trx_post_kyc["No. of Months Active"] = [dtu.relativedelta.relativedelta(dt.datetime(2022,7,1), dt.datetime(x.year,x.month,1)).months 
                                          + dtu.relativedelta.relativedelta(dt.datetime(2022,7,1), dt.datetime(x.year,x.month,1)).years*12 
                                          for x in trx_post_kyc["first_trx_date"]]
trx_post_kyc["No. of Months Active"] = [3 if x > 3 else x for x in trx_post_kyc["No. of Months Active"]]

#Determine the regularity = No. of months where they transacted/no. of months as a customer
trx_post_kyc["Regularity"] = [sum([trx_post_kyc[str(y[0]) + ", " + str(y[1])][x] for y in months_year])/trx_post_kyc["No. of Months Active"][x] 
                                 for x in range(len(trx_post_kyc))]

# trx_post_kyc = (trx_post_kyc
#                   .merge(trx_rd_sub.groupby(by = "Customer Id")
#                          .sum()["Nominal"], 
#                          how = "left", on = "Customer Id")
#                   .rename(columns = {"Nominal":"Total Subscriptions per Month"}))
# trx_post_kyc["Total Subscriptions per Month"] = [trx_post_kyc["Total Subscriptions per Month"][x]/trx_post_kyc["No. of Months Active"][x]
#                                              for x in range(len(trx_post_kyc))]

#Look at only those whose first transactions were in Apr-Jun
trx_post_kyc = trx_post_kyc[_["First Trx in Apr-Jun"]]

#Split into categories
#0.3-0.5 is low (Means only transacted once)
#0.6 is medium (Twice only)
#1 is high (Has transacted every month)
trx_post_kyc["Regularity Level"] = pd.cut(trx_post_kyc["Regularity"], [0,0.5,0.7,1], labels = ["Low Regularity", "Medium Regularity", "High Regularity"])

#Look at only those whose first transactions were before the 1st of June
trx_post_kyc = trx_post_kyc[(_["first_trx_date"] < dt.datetime(2022,6,1))]

#Group by regularity level and determine the proportion of each level
trx_post_kyc = (trx_post_kyc
                .groupby(by = ["Regularity Level"])
                .count()["Customer Id"]
                .reset_index()
                .rename(columns = {"Customer Id":"Count"})
                .assign(Total = [len(trx_post_kyc) for x in range(3)])
                .assign(Prop = lambda x: x.Count/x.Total*100))

#Plot the regularity of new customers
fig, ax = plt.subplots(figsize = (20.625,13.75))
plt.title("Regularitynya Nasabah-Nasabah Baru pada Bulan Apr-Jun 2022", fontsize = 20)
plt.xlabel("Tingkat Regularity", fontsize = 20)
plt.ylabel("Jumlah Nasabah", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

sns.barplot(data = trx_post_kyc,
            x = "Regularity Level", y = "Count")
for x in range(len(set(trx_post_kyc["Regularity Level"]))):
    y = list(trx_post_kyc["Regularity Level"])
    plt.annotate("{t}\n({p}%)".format(t = trx_post_kyc.query("`Regularity Level` == @y[@x]")["Count"].iloc[0], 
                                     p = trx_post_kyc.query("`Regularity Level` == @y[@x]")["Prop"].iloc[0].round(2)),
                 fontsize = 20, xy = (x,
                                      trx_post_kyc.query("`Regularity Level` == @y[@x]")["Count"].iloc[0]-8), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))
#%%

trx_swi_btw = trx_rd_swi.copy()

# trx_swi_btw["Firm"] = [re.search("([\\w-]+)\\s.*", x).group(1) for x in trx_swi_btw["Nama Produk"]]

# trx_swi_btw["Firm"] = ["BNI-AM" if x == "BNI" else x for x in trx_swi_btw["Firm"]]

# trx_swi_btw["Firm"] = ["Trimegah" if (x == "TRAM") | (x == "TRIM") | (x == "Trim") else x for x in trx_swi_btw["Firm"]]

# trx_swi_btw["Firm"] = ["BNP Paribas" if x == "BNP" else x for x in trx_swi_btw["Firm"]]

#Associate each product with a risk level 
tingkat_risiko = (pd.read_csv("Produk dan Risiko.csv", sep = ";", index_col = 0)
                  .reset_index(drop = True))
trx_swi_btw = (trx_swi_btw.merge(tingkat_risiko, 
                                 on = "Nama Produk", how = "left")
               .rename(columns = {"Risk":"Original Risk"}))
trx_swi_btw = (trx_swi_btw.merge((tingkat_risiko
                                  .rename(columns = {"Nama Produk":"Dialihkan ke Produk"})),
                                 on = "Dialihkan ke Produk", how = "left")
               .rename(columns = {"Risk":"New Risk"}))

trx_swi_btw = (trx_swi_btw.assign(Switch = lambda a: a["Original Risk"] + "-" + a["New Risk"]))

# risk_order = {"Rendah":1, "Menengah":2, "Tinggi":3}

# trx_swi_btw["Direction"] = trx_swi_btw["New Risk"].replace(risk_order)-trx_swi_btw["Original Risk"].replace(risk_order)

#Group by type of Switch and count the sum and number of transactions for each
trx_swi_btw_gb = (trx_swi_btw
                  .groupby(by = "Switch").count()["Nominal"]
                  .reset_index()
                  .rename(columns = {"Nominal":"Count"})
                  .merge((trx_swi_btw
                                    .groupby(by = "Switch").sum()["Nominal"]
                                    .reset_index()
                                    .rename(columns = {"Nominal":"Total"})),
                         on =  "Switch", how = "left"))

#Plot the counts and sums for each type of Switch
fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb[[x in ["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"] for x in trx_swi_btw_gb["Switch"]]],
            x = "Switch", y = "Count", ax = ax, palette = ["grey","tab:green","tab:green"],
            order = ["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"])
plt.arrow(x = -0.3, y = 225, dx = 1.5, dy = 0, width = 1.5, head_width = 6,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menurun", xy = (0.23,0.9), xycoords = "axes fraction", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.xlabel("Arah Pengalihan", fontsize = 20)
plt.ylabel("Jumlah Transasksi", fontsize = 20)
plt.title("Jumlah Transaksi per Arah Pengalihan (Tingkat Risiko Tinggi)", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"])):
    y = ["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb.query("`Switch` == @y[@x]")["Count"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb.query("`Switch` == @y[@x]")["Count"].iloc[0]-2), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb[[x in ["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"] for x in trx_swi_btw_gb["Switch"]]],
            x = "Switch", y = "Count",ax = ax, palette = ["tab:red","grey","tab:green"],
            order = ["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"])
plt.arrow(x = 0.95, y = 275, dx = -1.1, dy = 0, width = 1.5, head_width = 6,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menaik", xy = (0.21,0.964), xycoords = "axes fraction", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.arrow(x = 1.05, y = 275, dx = 1.1, dy = 0, width = 1.5, head_width = 6,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menurun", xy = (0.59,0.964), xycoords = "axes fraction", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.xlabel("Arah Pengalihan", fontsize = 20)
plt.ylabel("Jumlah Transasksi", fontsize = 20)
plt.title("Jumlah Transaksi per Arah Pengalihan (Tingkat Risiko Menengah)", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"])):
    y = ["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb.query("`Switch` == @y[@x]")["Count"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb.query("`Switch` == @y[@x]")["Count"].iloc[0]-2), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb[[x in ["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"] for x in trx_swi_btw_gb["Switch"]]],
            x = "Switch", y = "Count", ax = ax, palette = ["tab:red","tab:red","grey"],
            order = ["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"])
plt.arrow(x = 2.3, y = 420, dx = -1.5, dy = 0, width = 3, head_width = 10,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menaik", xy = (0.59,0.9), xycoords = "axes fraction", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.xlabel("Arah Pengalihan", fontsize = 20)
plt.ylabel("Jumlah Transasksi", fontsize = 20)
plt.title("Jumlah Transaksi per Arah Pengalihan (Tingkat Risiko Rendah)", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"])):
    y = ["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb.query("`Switch` == @y[@x]")["Count"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb.query("`Switch` == @y[@x]")["Count"].iloc[0]-2), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white")) 

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb[[x in ["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"] for x in trx_swi_btw_gb["Switch"]]],
            ax = ax, y = "Total", x = "Switch", palette = ["grey","tab:green","tab:green"],
            order = ["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"])
plt.arrow(x = -0.3, y = 13750000000, dx = 1.5, dy = 0, width = 100000000, head_width = 400000000,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menurun", xy = (0.23,0.9), xycoords = "axes fraction", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.xlabel("Arah Pengalihan", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Total AUM per Arah Pengalihan (Tingkat Risiko Tinggi)", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"])):
    y = ["Tinggi-Tinggi", "Tinggi-Menengah", "Tinggi-Rendah"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb.query("`Switch` == @y[@x]")["Total"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb.query("`Switch` == @y[@x]")["Total"].iloc[0]-15), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb[[x in ["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"] for x in trx_swi_btw_gb["Switch"]]],
            ax = ax, y = "Total", x = "Switch", palette = ["tab:red","grey","tab:green"],
            order = ["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"])
plt.arrow(x = 0.95, y = 33000000000, dx = -1.1, dy = 0, width = 150000000, head_width = 600000000,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menaik", xy = (0.21,0.964), xycoords = "axes fraction", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.arrow(x = 1.05, y = 33000000000, dx = 1.1, dy = 0, width = 150000000, head_width = 600000000,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menurun", xy = (0.59,0.964), xycoords = "axes fraction", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.xlabel("Arah Pengalihan", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Total AUM per Arah Pengalihan (Tingkat Risiko Menengah)", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"])):
    y = ["Menengah-Tinggi", "Menengah-Menengah", "Menengah-Rendah"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb.query("`Switch` == @y[@x]")["Total"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb.query("`Switch` == @y[@x]")["Total"].iloc[0]-15), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))   

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb[[x in ["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"] for x in trx_swi_btw_gb["Switch"]]],
            ax = ax, y = "Total", x = "Switch", palette = ["tab:red","tab:red","grey"],
            order = ["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"])
plt.arrow(x = 2.3, y = 26000000000, dx = -1.5, dy = 0, width = 130000000, head_width = 520000000,head_length = 0.05, color = "black")
plt.annotate("Tingkat Risiko Menaik", xy = (1.27,26650000000), xycoords = "data", 
             bbox = dict(boxstyle = "square, pad=0.3", fc = "None"), fontsize = 20)
plt.xlabel("Arah Pengalihan", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Total AUM per Arah Pengalihan (Tingkat Risiko Rendah)", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"])):
    y = ["Rendah-Tinggi", "Rendah-Menengah", "Rendah-Rendah"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb.query("`Switch` == @y[@x]")["Total"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb.query("`Switch` == @y[@x]")["Total"].iloc[0]-15), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))
    
trx_swi_btw_gb1 = (trx_swi_btw
                   .groupby(by = "Original Risk").count()["Nominal"]
                   .reset_index()
                   .rename(columns = {"Nominal":"Original Count"})
                   .merge((trx_swi_btw
                           .groupby(by = "Original Risk").sum()["Nominal"]
                           .reset_index()
                           .rename(columns = {"Nominal":"Original Total"})),
                          on =  "Original Risk", how = "left")
                   .rename(columns = {"Original Risk":"Risk"}))

trx_swi_btw_gb2 = (trx_swi_btw
                   .groupby(by = "New Risk").count()["Nominal"]
                   .reset_index()
                   .rename(columns = {"Nominal":"New Count"})
                   .merge((trx_swi_btw
                           .groupby(by = "New Risk").sum()["Nominal"]
                           .reset_index()
                           .rename(columns = {"Nominal":"New Total"})),
                          on =  "New Risk", how = "left")
                   .rename(columns = {"New Risk":"Risk"}))

trx_swi_btw_gb1 = (trx_swi_btw_gb1
                   .merge(trx_swi_btw_gb2,
                          on = "Risk", how = "left")
                   .assign(ΔTotal = lambda x: x["New Total"] - x["Original Total"],
                           ΔCount = lambda x: x["New Count"] - x["Original Count"]))
#                   .set_index("Risk"))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb1, ax = ax, 
            y = "ΔTotal", x = "Risk", palette = ["tab:green","tab:orange","tab:red"],
            order = ["Rendah", "Menengah", "Tinggi"])
plt.axhline(0, color = "black", lw = 1)
plt.xlabel("Tingkat Risiko", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Perubahan Total AUM per Tingkat Risiko Setelah Pengalihan", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)

for x in range(len(["Rendah", "Menengah", "Tinggi"])):
    y = ["Rendah", "Menengah", "Tinggi"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb1.query("`Risk` == @y[@x]")["ΔTotal"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb1.query("`Risk` == @y[@x]")["ΔTotal"].iloc[0]-3), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = trx_swi_btw_gb1, ax = ax, 
            y = "ΔCount", x = "Risk", palette = ["tab:green","tab:orange","tab:red"],
            order = ["Rendah", "Menengah", "Tinggi"])
plt.axhline(0, color = "black", lw = 1)
plt.xlabel("Tingkat Risiko", fontsize = 20)
plt.ylabel("Jumlah Transaksi", fontsize = 20)
plt.title("Perubahan Jumlah Transaksi per Tingkat Risiko Setelah Pengalihan", fontsize = 20)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)   

for x in range(len(["Rendah", "Menengah", "Tinggi"])):
    y = ["Rendah", "Menengah", "Tinggi"]
    plt.annotate("{t}".format(t = trx_swi_btw_gb1.query("`Risk` == @y[@x]")["ΔCount"].iloc[0]),                                     
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_btw_gb1.query("`Risk` == @y[@x]")["ΔCount"].iloc[0]-3), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))
#%%General summary
#Top 10 Products with the most number of transactions (subscriptions)
trx_sub_general_gb = pd.DataFrame(trx_rd_sub["Nama Produk"].value_counts()[:10]).reset_index()

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.countplot(data = trx_rd_sub, x =  "Nama Produk", 
              order = trx_rd_sub["Nama Produk"].value_counts()[:10].index)
plt.xlabel("Nama Produk", fontsize = 20)
plt.ylabel("Jumlah Transasksi", fontsize = 20)
plt.title("Sepuluh Produk dengan Jumlah Pembelian Terbanyak", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18)

plt.annotate("Total Transaksi: {t}".format(t = len(trx_rd_sub)),
             fontsize = 20, 
             xy = (0.95,0.9), xycoords = "axes fraction",
             horizontalalignment = "right",
             bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_sub_general_gb["index"])):
    y = trx_sub_general_gb["index"]
    plt.annotate("{t}\n({p}%)".format(t = trx_sub_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0],
                                      p = (trx_sub_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0]*100/len(trx_rd_sub)).round(2)),
                 fontsize = 20, 
                 xy = (x,
                       trx_sub_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0]-20), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

#Top 10 Products with the most number of transactions (redeems)
trx_red_general_gb = pd.DataFrame(trx_rd_red["Nama Produk"].value_counts()[:10]).reset_index()

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.countplot(data = trx_rd_red, x =  "Nama Produk", 
              order = trx_rd_red["Nama Produk"].value_counts()[:10].index)
plt.xlabel("Nama Produk", fontsize = 20)
plt.ylabel("Jumlah Transasksi", fontsize = 20)
plt.title("Sepuluh Produk dengan Jumlah Penjualan Terbanyak", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18)

plt.annotate("Total Transaksi: {t}".format(t = len(trx_rd_red)),
             fontsize = 20, 
             xy = (0.95,0.9), xycoords = "axes fraction",
             horizontalalignment = "right",
             bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_red_general_gb["index"])):
    y = trx_red_general_gb["index"]
    plt.annotate("{t}\n({p}%)".format(t = trx_red_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0],
                              p = (trx_red_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0]*100/len(trx_rd_red)).round(2)),
                 fontsize = 20, 
                 xy = (x,
                       trx_red_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0]-20), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

#Top 10 Products with the most number of transactions (switching from)
trx_swi_general_gb = pd.DataFrame(trx_rd_swi["Nama Produk"].value_counts()[:10]).reset_index()

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.countplot(data = trx_rd_swi, x =  "Nama Produk", 
              order = trx_rd_swi["Nama Produk"].value_counts()[:10].index)
plt.xlabel("Nama Produk Asal", fontsize = 20)
plt.ylabel("Jumlah Transasksi", fontsize = 20)
plt.title("Sepuluh Produk dengan Jumlah Pengalihan Terbanyak dari Produk Tersebut", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18)

plt.annotate("Total Transaksi: {t}".format(t = len(trx_rd_swi)),
             fontsize = 20, 
             xy = (0.95,0.9), xycoords = "axes fraction",
             horizontalalignment = "right",
             bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_swi_general_gb["index"])):
    y = trx_swi_general_gb["index"]
    plt.annotate("{t}\n({p}%)".format(t = trx_swi_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0],
                              p = (trx_swi_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0]*100/len(trx_rd_swi)).round(2)),
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_general_gb.query("`index` == @y[@x]")["Nama Produk"].iloc[0]-2), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

#Top 10 Products with the most number of transactions (switching to)
trx_swi_general_gb = pd.DataFrame(trx_rd_swi["Dialihkan ke Produk"].value_counts()[:10]).reset_index()

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.countplot(data = trx_rd_swi, x =  "Dialihkan ke Produk", 
              order = trx_rd_swi["Dialihkan ke Produk"].value_counts()[:10].index)
plt.xlabel("Nama Produk Tujuan", fontsize = 20)
plt.ylabel("Jumlah Transasksi", fontsize = 20)
plt.title("Sepuluh Produk dengan Jumlah Pengalihan Terbanyak ke Produk Tersebut", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18)

plt.annotate("Total Transaksi: {t}".format(t = len(trx_rd_swi)),
             fontsize = 20, 
             xy = (0.95,0.9), xycoords = "axes fraction",
             horizontalalignment = "right",
             bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_swi_general_gb["index"])):
    y = trx_swi_general_gb["index"]
    plt.annotate("{t}\n({p}%)".format(t = trx_swi_general_gb.query("`index` == @y[@x]")["Dialihkan ke Produk"].iloc[0],
                              p = (trx_swi_general_gb.query("`index` == @y[@x]")["Dialihkan ke Produk"].iloc[0]*100/len(trx_rd_swi)).round(2)),
                 fontsize = 20, 
                 xy = (x,
                       trx_swi_general_gb.query("`index` == @y[@x]")["Dialihkan ke Produk"].iloc[0]-2), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

#Top 10 Products with the highest total AUM (subscriptions)
trx_sub_general_gb = pd.DataFrame((trx_rd_sub
                                  .groupby(by = "Nama Produk").sum()["Nominal"]
                                  .reset_index().sort_values("Nominal", ascending = False)[:10]
                                  .reset_index(drop = True)))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = (trx_rd_sub
                    .groupby(by = "Nama Produk").sum()["Nominal"]
                    .reset_index().sort_values("Nominal", ascending = False)[:10]),
            x = "Nama Produk", y = "Nominal" ,ax = ax)
plt.xlabel("Nama Produk", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Sepuluh Produk dengan Total AUM Pembelian Terbanyak", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18) 

plt.annotate("Total AUM: {t}".format(t = np.sum(trx_rd_sub["Nominal"])),
              fontsize = 20, 
              xy = (0.95,0.9), xycoords = "axes fraction",
              horizontalalignment = "right",
              bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_sub_general_gb["Nama Produk"])):
    y = trx_sub_general_gb["Nama Produk"]
    plt.annotate("{t}\n({p}%)".format(t = trx_sub_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0],
                                     p = (trx_sub_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0]/np.sum(trx_rd_sub["Nominal"])*100).round(2)), 
                 fontsize = 12, 
                 xy = (x,
                       trx_sub_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0]-20), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

#Top 10 Products with the highest total AUM (redeems)
trx_red_general_gb = pd.DataFrame((trx_rd_red
                                  .groupby(by = "Nama Produk").sum()["Nominal"]
                                  .reset_index().sort_values("Nominal", ascending = False)[:10]
                                  .reset_index(drop = True)))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = (trx_rd_red
                    .groupby(by = "Nama Produk").sum()["Nominal"]
                    .reset_index().sort_values("Nominal", ascending = False)[:10]),
            x = "Nama Produk", y = "Nominal" ,ax = ax)
plt.xlabel("Nama Produk", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Sepuluh Produk dengan Total AUM Penjualan Terbanyak", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18)

plt.annotate("Total AUM: {t}".format(t = np.sum(trx_rd_red["Nominal"])),
              fontsize = 20, 
              xy = (0.95,0.9), xycoords = "axes fraction",
              horizontalalignment = "right",
              bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_red_general_gb["Nama Produk"])):
    y = trx_red_general_gb["Nama Produk"]
    plt.annotate("{t}\n({p}%)".format(t = trx_red_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0],
                              p = (trx_red_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0]/np.sum(trx_rd_red["Nominal"])*100).round(2)),                                     
                 fontsize = 12, 
                 xy = (x,
                       trx_red_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0]-20), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

#Top 10 Products with the highest total AUM (switching from)
trx_swi_general_gb = pd.DataFrame((trx_rd_swi
                                  .groupby(by = "Nama Produk").sum()["Nominal"]
                                  .reset_index().sort_values("Nominal", ascending = False)[:10]
                                  .reset_index(drop = True)))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = (trx_rd_swi
                    .groupby(by = "Nama Produk").sum()["Nominal"]
                    .reset_index().sort_values("Nominal", ascending = False)[:10]),
            x = "Nama Produk", y = "Nominal" ,ax = ax)
plt.xlabel("Nama Produk Asal", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Sepuluh Produk dengan Total AUM Pengalihan Terbanyak dari Produk Tersebut", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18)

plt.annotate("Total AUM: {t}".format(t = np.sum(trx_rd_swi["Nominal"])),
              fontsize = 20, 
              xy = (0.95,0.9), xycoords = "axes fraction",
              horizontalalignment = "right",
              bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_swi_general_gb["Nama Produk"])):
    y = trx_swi_general_gb["Nama Produk"]
    plt.annotate("{t}\n({p}%)".format(t = trx_swi_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0],
                              p = (trx_swi_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0]/np.sum(trx_rd_swi["Nominal"])*100).round(2)),                                      
                 fontsize = 12, 
                 xy = (x,
                       trx_swi_general_gb.query("`Nama Produk` == @y[@x]")["Nominal"].iloc[0]-20), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

#Top 10 Products with the highest total AUM (switching to)
trx_swi_general_gb = pd.DataFrame((trx_rd_swi
                                  .groupby(by = "Dialihkan ke Produk").sum()["Nominal"]
                                  .reset_index().sort_values("Nominal", ascending = False)[:10]
                                  .reset_index(drop = True)))

fig, ax = plt.subplots(figsize = (20.625,13.75))
sns.barplot(data = (trx_rd_swi
                    .groupby(by = "Dialihkan ke Produk").sum()["Nominal"]
                    .reset_index().sort_values("Nominal", ascending = False)[:10]),
            x = "Dialihkan ke Produk", y = "Nominal" ,ax = ax)
plt.xlabel("Nama Produk Tujuan", fontsize = 20)
plt.ylabel("Total AUM", fontsize = 20)
plt.title("Sepuluh Produk dengan Total AUM Pengalihan Terbanyak ke Produk Tersebut", fontsize = 20)
plt.xticks(fontsize = 18, rotation = 90)
plt.yticks(fontsize = 18)

plt.annotate("Total AUM: {t}".format(t = np.sum(trx_rd_swi["Nominal"])),
              fontsize = 20, 
              xy = (0.95,0.9), xycoords = "axes fraction",
              horizontalalignment = "right",
              bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

for x in range(len(trx_swi_general_gb["Dialihkan ke Produk"])):
    y = trx_swi_general_gb["Dialihkan ke Produk"]
    plt.annotate("{t}\n({p}%)".format(t = trx_swi_general_gb.query("`Dialihkan ke Produk` == @y[@x]")["Nominal"].iloc[0],
                              p = (trx_swi_general_gb.query("`Dialihkan ke Produk` == @y[@x]")["Nominal"].iloc[0]/np.sum(trx_rd_swi["Nominal"])*100).round(2)),                                     
                 fontsize = 12, 
                 xy = (x,
                       trx_swi_general_gb.query("`Dialihkan ke Produk` == @y[@x]")["Nominal"].iloc[0]-20), xycoords = "data",
                 horizontalalignment = "center",
                 bbox = dict(boxstyle = "square, pad=0.3", fc = "white"))

