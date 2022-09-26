import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from google.colab import auth
import gspread
from google.auth import default

#Authorize access to Google Drive
#Memberi izin untuk mengakses Google Drive
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

#Open the Google Sheet itself, and then obtain the values from the "Data" worksheet
#IF YOU RENAME THE FILE OR ANY OF ITS WORKSHEETS, UPDATE THE LINE BELOW

#Membuka Google Sheetnya dan mengambil nilai-nilai dalam worksheet "Data"
#JIKA MENGGANTI NAMA FILE ATAU WORKSHEET DI DALAMNYA, UBAH NAMANYA PADA BARIS DI BAWAH INI
worksheet = gc.open('Produk-produk').worksheet("Data")
rows = worksheet.get_all_values()

#Convert the extracted values into a data frame. Clean the table a bit by setting
#the column names, subsetting the columns we want, and ensuring attributes are of the 
#correct data type

#Ubah nilai-nilai yang telah diambil di atas menjadi data frame. Lalu merapihkan tabelnya
#dengan mendefinisikan nama-nama kolomnya, lalu memilih atribut yang kita inginkan, kemudian
#memastikan bahwa jenis data atributnya benar
prod_perf = pd.DataFrame.from_records(rows)
prod_perf = prod_perf.rename(columns=prod_perf.iloc[0]).drop(prod_perf.index[0])
prod_perf = prod_perf[["Tanggal (End of Month)", "product_name", "aum_total", "user_total"]]
for x in list(prod_perf.columns)[2:len(list(prod_perf.columns))]:
  prod_perf = prod_perf.astype({x : "int64"})
prod_perf["Tanggal (End of Month)"] = [dt.datetime.strptime(x, "%m/%d/%Y") for x in prod_perf["Tanggal (End of Month)"]]


var = vars() #This allows us to convert strings to variables later on #Ini memampukan kita untuk mengubah string menjadi variable nanti
no_months = 6 #Setting the no. of months to forecast for later on #Menentukan jumlah bulan untuk meramal

#list(set(...)) creates a list of unique product names
#Then we replace any spaces with underscores
#For this loop, x represents the product name

#list(set(...)) membuat sebuah list yang mengandung nama unik produk
#Lalu kami menggantikan spasi dengan garis bawah
#Untuk loop ini, x merepresentasikan nama produk 
for x in [x.replace(" ", "_") for x in list(set(prod_perf.product_name))]:
    var["prod_perf_" + x] = prod_perf[prod_perf.product_name ==  x.replace("_", " ")] #Subset rows according to each product. Here we remove the underscores as in the table, the product names do not have underscores
    #Use the preceeding variable as a base for the forecast
    #Gunakan variable sebelumnya sebagai dasar untuk ramalannya
    var["prod_perf_" + x + "_forecast"] = var["prod_perf_" + x]
    #Concatenate the existing data with its forecast
    #Gabungkan tabel data dengan ramalannya
    var["prod_perf_" + x + "_forecast"] = pd.concat([var["prod_perf_" + x + "_forecast"],
                                                     #Here we turn a list of (inner) lists into a data frame. Each inner list and hence each row, consists of the z-month forecasts 
                                                     #for each attribute, 'y'. An inner list here is the sum of two lists.
                                                     #"["_{}M".format(z + 1), x]" gives the values for the first two columns "Tanggal..." and "product_name". "_{}M".format(z + 1) 
                                                     #indicates how many months ahead we are forecasting by (e.g. returns _2M for the two month forecast).
                                                     #The second part of the list subsets the z-month forecasts of each attribute. Then the additional preceeding for-loop ensures
                                                     #any negative values get turned to zero.
                                                        pd.DataFrame([["_{}M".format(z + 1), x] + [0 if a < 0 else a for a in [ExponentialSmoothing(np.array(var["prod_perf_" + x + "_forecast"][y]), trend = "add").fit().forecast(no_months)[z] for y in list(prod_perf.columns)[2:len(list(prod_perf.columns))]]] for z in range(no_months)],
                                                        columns = list(prod_perf.columns))],
                                                        axis = 0)
    var["prod_perf_" + x + "_forecast"] = var["prod_perf_" + x + "_forecast"].reset_index(drop = True)
    #Rounding the forecast values
    #Membulatkan nilai ramalan
    for y in list(prod_perf.columns)[2:len(list(prod_perf.columns))]:
        var["prod_perf_" + x + "_forecast"][y] = round(var["prod_perf_" + x + "_forecast"][y])
    #Selecting only the 3- and 6-month forecasts
    #Memilih hanya ramalan 3- dan 6-bulan
    var["prod_perf_" + x + "_forecast"] = pd.concat([var["prod_perf_" + x],
                                                    pd.DataFrame([var["prod_perf_" + x + "_forecast"].iloc[len(var["prod_perf_" + x])+2,:]]),
                                                    pd.DataFrame([var["prod_perf_" + x + "_forecast"].iloc[len(var["prod_perf_" + x])+5,:]])],
                                                  axis = 0)
    var["prod_perf_" + x + "_forecast"] = var["prod_perf_" + x + "_forecast"].reset_index(drop = True)
    #Extract the 3- and 6- month forecast for each attribute 'y' and arrange them horizontally
    #Mengekstrak ramalan 3- dan 6-bulan untuk setiap atribut 'y' dan menyusunkannya secara horizontal
    var["prod_perf_" + x + "_forecast"] = pd.DataFrame([[x] + [var["prod_perf_" + x + "_forecast"][y][z] for y in list(prod_perf.columns)[2:len(list(prod_perf.columns))] for z in range(len(var["prod_perf_" + x + "_forecast"])-2,len(var["prod_perf_" + x + "_forecast"]))]],
                                                       #Sets the column names as "product_name" followed by "attribute + _{}M" for all attributes 'y' and at _3M and _6M
                                                       #Menamai kolom-kolom sebagai "product_name" lalu diikuti oleh "atribut + _{}M" untuk semua atribut 'y' pada _3M dan _6M
                                                       columns = ["product_name"] + [y + var["prod_perf_" + x + "_forecast"]["Tanggal (End of Month)"][z] for y in list(prod_perf.columns)[2:len(list(prod_perf.columns))] for z in range(len(var["prod_perf_" + x + "_forecast"])-2,len(var["prod_perf_" + x + "_forecast"]))])

#Concatenate forecasts of each individual product into one table   
#Gabungkan ramalan dari setiap produk ke satu tabel
prod_perf_forecast = pd.concat([var["prod_perf_" + x + "_forecast"] for x in [x.replace(" ", "_") for x in list(set(prod_perf.product_name))]], axis = 0)
prod_perf_forecast = prod_perf_forecast.sort_values("product_name").reset_index(drop = True)

#Export the output to the Google Sheet from where it came
#IF YOU RENAME THE FILE OR ANY OF ITS WORKSHEETS, UPDATE THE LINE BELOW

#Ekspor tabel ramalan ke Google Sheet asalnya
#JIKA MENGGANTI NAMA FILE ATAU WORKSHEET DI DALAMNYA, UBAH NAMANYA PADA BARIS DI BAWAH INI
prod_perf_output = gc.open('Produk-produk').worksheet("Output") #Opens the same Google Sheet as above, but accesses the "Output" worksheet #Membuka Google Sheet yang sama seperti di atas, teteapi membuka worksheet "Output"
prod_perf_output.clear() #Clears the worksheet #Mengosongkan worksheetnya
prod_perf_output.update([prod_perf_forecast.columns.values.tolist()] + prod_perf_forecast.values.tolist()) #Fills the cells with values from the data frame #Mengisi sel-sel dengan nilai dari tabel output

prod_perf_A

