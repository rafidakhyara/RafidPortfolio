import pandas as pd
import re
from decimal import Decimal
from openpyxl import load_workbook
from openpyxl import Workbook
import xlsxwriter
import numpy as np
import math
import matplotlib.pyplot as plt
import datetime as dt

#Importing data. Using for loops as there are a lot of CSVs
var = vars()

for t in [("januari", "Januari.csv"), ("februari", "Februari.csv"), ("maret", "Maret.csv"), ("april", "April.csv"),\
          ("mei", "Mei.csv"), ("juni", "Juni.csv")]:
    for x, y in [t]:
        var["newuser_" + x] = pd.read_csv(y, header=0)
        
transaksi_januari = pd.read_csv("Januari Transaksi.csv", header=0).rename(columns={"No HP": "NO HP"})
transaksi_januari = transaksi_januari[:-1]

for t in [("februari", "Februari Transaksi.csv"), ("maret", "Maret Transaksi.csv"),\
          ("april", "April Transaksi.csv"), ("mei", "Mei Transaksi.csv"), ("juni", "Juni Transaksi.csv")]:
    for x, y in [t]:
        var["transaksi_" + x] = pd.read_csv(y, header=0).rename(columns={"USER NAME": "NO HP"})
        var["transaksi_" + x] = var["transaksi_" + x][:-1]
        #var["transaksi_" + x] = var["transaksi_" + x]


        
#Row binding the data together into one Data Frame
bulan = ["januari", "februari", "maret", "april", "mei", "juni"]

newuser_bulanan = newuser_januari

for b in bulan[1:]:
    newuser_bulanan = pd.concat([newuser_bulanan, var["newuser_" + b]], axis=0)
    
transaksi_bulanan = transaksi_januari

for b in bulan[1:]:
    transaksi_bulanan = pd.concat([transaksi_bulanan, var["transaksi_" + b]], axis=0)
    
newuser_bulanan = newuser_bulanan.astype({"NO HP":"str"})        

#Reformatting phone numbers so that it is in a consistent format
newuser_bulanan["NO HP"] = ["0" + re.match("^62(\d+)", x).group(1) if type(re.match("^62(\d+)", x)) == re.Match else "0" + x \
                            for x in newuser_bulanan["NO HP"]]
                            


#New User Belom Transaksi
#Finding new users that have done a transaction
newuser_sdh_trx = transaksi_bulanan.groupby(["NO HP", "NAMA"]).count().reset_index()[["NO HP", "NAMA"]]\
                  .merge(newuser_bulanan, on = "NO HP", how="inner")[["NO HP", "NAMA_x", "EMAIL", "TGL DAFTAR"]]\
                  .rename({"NAMA_x":"NAMA"})
                  


#Finding new users that have not done a transaction
newuser_blm_trx = transaksi_bulanan.groupby(["NO HP", "NAMA"]).count().reset_index()[["NO HP", "NAMA"]]\
                  .merge(newuser_bulanan, on = "NO HP", how="right")

newuser_blm_trx = newuser_blm_trx[newuser_blm_trx["NAMA_x"].isna()][["NO HP", "NAMA_y", "EMAIL", "TGL DAFTAR"]]\
                  .rename({"NAMA_y":"NAMA"})                  



#Export newuser_blm_trx table to CSV
newuser_blm_trx["NO HP"] = ["'" + x + "'" for x in newuser_blm_trx["NO HP"]]
newuser_blm_trx.to_csv("New User Fello Belom Transaksi Januari-Juni 2023.csv", index=False)

#Top 10 sering transaksi dan banyak spending; user loyal

#Create an empty data frame with multiple index levels
multiindex = pd.MultiIndex.from_product([["Januari", "Februari", "Maret", "April", "Mei", "Juni"], ["Paling Sering Transaksi", "Paling Banyak Spending"], \
                                         ["Nama", "No HP", "Email", "Jumlah Trx"]])

monthly_trx_insight = pd.DataFrame(columns=multiindex)



for x in bulan:
    #Count the top 10 paling sering each month
    top10ser = var["transaksi_" + x].groupby(["NAMA", "NO HP"]).sum()[["JUMLAH TRANSAKSI"]]\
    .sort_values("JUMLAH TRANSAKSI", ascending=False).head(10).reset_index()\
    .merge(newuser_bulanan[["NO HP", "EMAIL"]], on = "NO HP", how="left").rename(columns={"NAMA":"Nama", "NO HP":"No HP",
                                                                                         "JUMLAH TRANSAKSI":"Jumlah Trx",
                                                                                         "EMAIL":"Email"})
    top10ser = top10ser[["Nama", "No HP", "Email", "Jumlah Trx"]]
    
    #Count the top 10 paling spending each month
    var["transaksi_" + x]["RUPIAH"] = [float(Decimal(re.sub(r'[^\d.]', '', x))) for x in var["transaksi_" + x]["RUPIAH"]]
    top10spe = var["transaksi_" + x].groupby(["NAMA", "NO HP"]).sum()[["RUPIAH"]].sort_values("RUPIAH", ascending=False).head(10)\
    .reset_index().merge(newuser_bulanan[["NO HP", "EMAIL"]], on = "NO HP", how="left")\
    .rename(columns={"NAMA":"Nama", "NO HP":"No HP", "RUPIAH":"Jumlah Trx", "EMAIL":"Email"})
    
    top10spe = top10spe[["Nama", "No HP", "Email", "Jumlah Trx"]]
    
    #Enter into empty data frame
    monthly_trx_insight[(x.title(), 'Paling Sering Transaksi')] = top10ser
    monthly_trx_insight[(x.title(), 'Paling Banyak Spending')] = top10spe



#Finding loyal users
hp_loyal = []

for x in set(transaksi_bulanan["NO HP"]):
    brp_bln_trx = 0
    for y in bulan:
        if x in list(var["transaksi_" + y]["NO HP"]):
            brp_bln_trx += 1
    if brp_bln_trx == len(bulan):
        hp_loyal.append(x)



#Turn hp_loyal list into a dataframe        
user_loyal = pd.DataFrame(hp_loyal, columns=["NO HP"]).merge(transaksi_bulanan.groupby(["NO HP","NAMA"]).count()\
            .reset_index()[["NO HP", "NAMA"]], on="NO HP", how="left")\
            .merge(newuser_bulanan[["NO HP", "EMAIL"]], on="NO HP", how="left")

multiindex = pd.MultiIndex.from_product([["User Loyal"], ["NO HP", "NAMA", "EMAIL"]])

user_loyal = pd.DataFrame(user_loyal.to_numpy(), columns=multiindex)        
                  
                  
                  
#Write top10ser, top10spe and user_loyal into an Excel file
rows = list(np.arange(0,16*math.floor(len(bulan)/2)+16,16))

writer = pd.ExcelWriter('Insight Monthly Transaction Januari-Juni 2023.xlsx', engine='xlsxwriter')

if (len(bulan)/2).is_integer():
    cols = list(np.arange(0,16*math.floor(len(bulan)/2)+16,16))
    for x in range(math.floor(len(bulan)/2)):
        monthly_trx_insight.iloc[:,cols[x]:cols[x+1]].to_excel(writer, "Summary", startrow=rows[x], startcol=0)
else:
    cols = list(np.arange(0,16*math.floor(len(bulan)/2),16)) + [16*math.floor(len(bulan)/2)-8]
    for x in range(math.floor(len(bulan)/2)):
        monthly_trx_insight.iloc[:,cols[x]:cols[x+1]].to_excel(writer, "Summary", startrow=rows[x], startcol=0)

user_loyal.to_excel(writer, "Summary", startrow=0, startcol=18)

writer.close()

#New users that have done a transaction: 
print(len(newuser_sdh_trx))
#New users that have not done a transaction: 
print(len(newuser_blm_trx))
#Total new users:
print(len(newuser_bulanan))
#Total of all users that have done a transaction from January-June 2023:
print(len(set(transaksi_bulanan["NO HP"])))
