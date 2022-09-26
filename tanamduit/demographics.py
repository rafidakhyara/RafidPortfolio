#Import required packages
import numpy as np
import pandas as pd
import math as mt
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

#Import the data
data = pd.read_excel('Data AUM RD dan SBN as of balance 30 Apr 2022.xlsx')
#%%msh nasabah
#Remove erroneous customer ids
data = data[data.customer_id > 0]
#Take only individual customers
data = data[data.customer_type == "individual"]
#Remove erroneous rows where kyc_date is NA
data = data[pd.notnull(data.kyc_date)].reset_index(drop = True)

demographics = data.copy()
#Remove people who haven't transacted
demographics = demographics[pd.notnull(demographics.first_trx_date)]
#Fill NAs with zero
demographics.iloc[:,13:39] = demographics.iloc[:,13:39].fillna(0)
demographics = demographics.reset_index(drop = True)

#Sum up all the jlh for SBN
jlh_sbn = demographics.loc[:,"jlh_sbr"] + demographics.loc[:,"jlh_ori"] + demographics.loc[:,"jlh_st"] + demographics.loc[:,"jlh_sr"]
jlh_sbn = pd.DataFrame(jlh_sbn)
jlh_sbn.columns = ["jlh_sbn"]
#Sum up all the jlh for emas
jlh_emas = demographics.loc[:,"jlh_beli_masduit"] + demographics.loc[:,"jlh_beli_cetak_masduit"] + demographics.loc[:,"jlh_beli_tamasia"]
jlh_emas = pd.DataFrame(jlh_emas)
jlh_emas.columns = ["jlh_emas"]
demographics = pd.concat([demographics, jlh_sbn], axis=1)
demographics = pd.concat([demographics, jlh_emas], axis=1)

#If jlh > 0, return 1, meaning they've invested in that type of investment beforehand
for x in ["jlh_bl","jlh_sbn","jlh_emas"]:
    temp = pd.DataFrame([1 if y > 0 else 0 for y in demographics.loc[:,x]])
    temp.columns = [x + "_binary"]
    demographics = pd.concat([demographics,temp], axis = 1)

#Split age into age brackets
age = [dt.datetime(2022, 4, 30) - x for x in demographics.date_of_birth]
age = [mt.floor(x.days/365.25) for x in age]
age_bracket = ["19 ke bawah" if x >= 16 and x <= 19 else "20-29" if x >= 20 and x <= 29 else "30-39" if x >= 30 and x <= 39 else "40-49" if x >= 40 and x <= 49 else "50-59" if x >= 50 and x <= 59 else "60-69" if x >= 60 and x <= 69 else "70 ke atas" for x in age]
age_bracket = pd.DataFrame(age_bracket)
age_bracket.columns = ["age_bracket"]
age = pd.DataFrame(age)
age.columns = ["age"]
demographics = pd.concat([demographics, age_bracket], axis = 1)
demographics = pd.concat([demographics, age], axis = 1)

#Sum up the AUM of emas
aum_emas = pd.DataFrame(demographics.aum_masduit + demographics.aum_tamasia).round(decimals = 5)
aum_emas.columns = ["aum_emas"]
demographics = pd.concat([demographics, aum_emas], axis = 1)

#Save an unfiltered copy of demographics
demographics_total = demographics.copy()

#Keep only people who have AUM more than zero (indicating they are still customers)
demographics_outliers_rd = demographics[demographics.aum_rd > 0]
demographics_outliers_sbn = demographics[demographics.aum_sbn > 0]
demographics_outliers_emas = demographics[demographics.aum_emas > 0]
outliers_aumrd = demographics_outliers_rd
outliers_aumsbn = demographics_outliers_sbn
outliers_aumemas = demographics_outliers_emas
demographics = outliers_aumrd.merge(outliers_aumsbn, how = "outer")
demographics = demographics.merge(outliers_aumemas, how = "outer")

#
age_bracket_prop = pd.DataFrame(demographics.groupby(by = "age_bracket").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
age_bracket_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
age_bracket_n = pd.DataFrame(demographics.groupby(by = "age_bracket").count()["jlh_bl_binary"])
age_bracket_n.columns = ["n"]
age_bracket_pref = pd.concat([age_bracket_prop, age_bracket_n], axis = 1)

gender_prop = pd.DataFrame(demographics.groupby(by = "gender").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
gender_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
gender_n = pd.DataFrame(demographics.groupby(by = "gender").count()["jlh_bl_binary"])
gender_n.columns = ["n"]
gender_pref = pd.concat([gender_prop, gender_n], axis = 1)

education_prop = pd.DataFrame(demographics.groupby(by = "education").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
education_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
education_n = pd.DataFrame(demographics.groupby(by = "education").count()["jlh_bl_binary"])
education_n.columns = ["n"]
education_pref = pd.concat([education_prop, education_n], axis = 1)

occupation_prop = pd.DataFrame(demographics.groupby(by = "occupation").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
occupation_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
occupation_n = pd.DataFrame(demographics.groupby(by = "occupation").count()["jlh_bl_binary"])
occupation_n.columns = ["n"]
occupation_pref = pd.concat([occupation_prop, occupation_n], axis = 1)

gross_income_prop = pd.DataFrame(demographics.groupby(by = "gross_income").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
gross_income_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
gross_income_n = pd.DataFrame(demographics.groupby(by = "gross_income").count()["jlh_bl_binary"])
gross_income_n.columns = ["n"]
gross_income_pref = pd.concat([gross_income_prop, gross_income_n], axis = 1)

marital_status_prop = pd.DataFrame(demographics.groupby(by = "marital_status").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
marital_status_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
marital_status_n = pd.DataFrame(demographics.groupby(by = "marital_status").count()["jlh_bl_binary"])
marital_status_n.columns = ["n"]
marital_status_pref = pd.concat([marital_status_prop, marital_status_n], axis = 1)

propinsi_prop = pd.DataFrame(demographics.groupby(by = "propinsi").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
propinsi_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
propinsi_n = pd.DataFrame(demographics.groupby(by = "propinsi").count()["jlh_bl_binary"])
propinsi_n.columns = ["n"]
propinsi_pref = pd.concat([propinsi_prop, propinsi_n], axis = 1)

age_bracket_risk = demographics.groupby(by = "age_bracket").sum().loc[:,["jlh_bl","beli_mm","beli_fi","beli_bl","beli_eq"]]
age_bracket_risk = pd.concat([age_bracket_risk, age_bracket_risk.beli_mm/age_bracket_risk.jlh_bl,
                              age_bracket_risk.beli_fi/age_bracket_risk.jlh_bl,
                              age_bracket_risk.beli_bl/age_bracket_risk.jlh_bl,
                              age_bracket_risk.beli_eq/age_bracket_risk.jlh_bl], axis = 1)
age_bracket_risk.columns = list(age_bracket_risk.columns)[0:5] + ["mm_prop", "fi_prop", "bl_prop", "eq_prop"]

gender_risk = demographics.groupby(by = "gender").sum().loc[:,["jlh_bl","beli_mm","beli_fi","beli_bl","beli_eq"]]
gender_risk = pd.concat([gender_risk, gender_risk.beli_mm/gender_risk.jlh_bl,
                              gender_risk.beli_fi/gender_risk.jlh_bl,
                              gender_risk.beli_bl/gender_risk.jlh_bl,
                              gender_risk.beli_eq/gender_risk.jlh_bl], axis = 1)
gender_risk.columns = list(gender_risk.columns)[0:5] + ["mm_prop", "fi_prop", "bl_prop", "eq_prop"]

education_risk = demographics.groupby(by = "education").sum().loc[:,["jlh_bl","beli_mm","beli_fi","beli_bl","beli_eq"]]
education_risk = pd.concat([education_risk, education_risk.beli_mm/education_risk.jlh_bl,
                              education_risk.beli_fi/education_risk.jlh_bl,
                              education_risk.beli_bl/education_risk.jlh_bl,
                              education_risk.beli_eq/education_risk.jlh_bl], axis = 1)
education_risk.columns = list(education_risk.columns)[0:5] + ["mm_prop", "fi_prop", "bl_prop", "eq_prop"]

occupation_risk = demographics.groupby(by = "occupation").sum().loc[:,["jlh_bl","beli_mm","beli_fi","beli_bl","beli_eq"]]
occupation_risk = pd.concat([occupation_risk, occupation_risk.beli_mm/occupation_risk.jlh_bl,
                              occupation_risk.beli_fi/occupation_risk.jlh_bl,
                              occupation_risk.beli_bl/occupation_risk.jlh_bl,
                              occupation_risk.beli_eq/occupation_risk.jlh_bl], axis = 1)
occupation_risk.columns = list(occupation_risk.columns)[0:5] + ["mm_prop", "fi_prop", "bl_prop", "eq_prop"]

gross_income_risk = demographics.groupby(by = "gross_income").sum().loc[:,["jlh_bl","beli_mm","beli_fi","beli_bl","beli_eq"]]
gross_income_risk = pd.concat([gross_income_risk, gross_income_risk.beli_mm/gross_income_risk.jlh_bl,
                              gross_income_risk.beli_fi/gross_income_risk.jlh_bl,
                              gross_income_risk.beli_bl/gross_income_risk.jlh_bl,
                              gross_income_risk.beli_eq/gross_income_risk.jlh_bl], axis = 1)
gross_income_risk.columns = list(gross_income_risk.columns)[0:5] + ["mm_prop", "fi_prop", "bl_prop", "eq_prop"]

marital_status_risk = demographics.groupby(by = "marital_status").sum().loc[:,["jlh_bl","beli_mm","beli_fi","beli_bl","beli_eq"]]
marital_status_risk = pd.concat([marital_status_risk, marital_status_risk.beli_mm/marital_status_risk.jlh_bl,
                              marital_status_risk.beli_fi/marital_status_risk.jlh_bl,
                              marital_status_risk.beli_bl/marital_status_risk.jlh_bl,
                              marital_status_risk.beli_eq/marital_status_risk.jlh_bl], axis = 1)
marital_status_risk.columns = list(marital_status_risk.columns)[0:5] + ["mm_prop", "fi_prop", "bl_prop", "eq_prop"]

propinsi_risk = demographics.groupby(by = "propinsi").sum().loc[:,["jlh_bl","beli_mm","beli_fi","beli_bl","beli_eq"]]
propinsi_risk = pd.concat([propinsi_risk, propinsi_risk.beli_mm/propinsi_risk.jlh_bl,
                              propinsi_risk.beli_fi/propinsi_risk.jlh_bl,
                              propinsi_risk.beli_bl/propinsi_risk.jlh_bl,
                              propinsi_risk.beli_eq/propinsi_risk.jlh_bl], axis = 1)
propinsi_risk.columns = list(propinsi_risk.columns)[0:5] + ["mm_prop", "fi_prop", "bl_prop", "eq_prop"]

age_bracket_amount = demographics.groupby(by = "age_bracket").median().loc[:,["jlh_bl","jlh_sbn","jlh_emas"]]
gender_amount = demographics.groupby(by = "gender").median().loc[:,["jlh_bl","jlh_sbn","jlh_emas"]]
education_amount = demographics.groupby(by = "education").median().loc[:,["jlh_bl","jlh_sbn","jlh_emas"]]
occupation_amount = demographics.groupby(by = "occupation").median().loc[:,["jlh_bl","jlh_sbn","jlh_emas"]]
gross_income_amount = demographics.groupby(by = "gross_income").median().loc[:,["jlh_bl","jlh_sbn","jlh_emas"]]
marital_status_amount = demographics.groupby(by = "marital_status").median().loc[:,["jlh_bl","jlh_sbn","jlh_emas"]]
propinsi_amount = demographics.groupby(by = "propinsi").median().loc[:,["jlh_bl","jlh_sbn","jlh_emas"]]

for x in ["aum_mm","aum_fi","aum_bl","aum_eq"]:
    temp = pd.DataFrame(demographics.loc[:,x]/demographics.loc[:,"aum_rd"])
    temp.columns = [x + "_prop"]
    demographics = pd.concat([demographics,temp], axis = 1)
demographics.iloc[:,48:52] = demographics.iloc[:,48:52].fillna(0)

#Count the days from first transaction
days_from_first_trx = [dt.datetime(2022, 4, 30) - x for x in demographics.first_trx_date]
days_from_first_trx = [x.days for x in days_from_first_trx]
days_from_first_trx = pd.DataFrame(days_from_first_trx)
days_from_first_trx.columns = ["days_from_first_trx"]
demographics = pd.concat([demographics, days_from_first_trx], axis = 1)

#Count the sum of AUM for each characteristic
age_bracket_aumsum = demographics.groupby(by = "age_bracket").sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
gender_aumsum = demographics.groupby(by = "gender").sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
education_aumsum = demographics.groupby(by = "education").sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
occupation_aumsum = demographics.groupby(by = "occupation").sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
gross_income_aumsum = demographics.groupby(by = "gross_income").sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
marital_status_aumsum = demographics.groupby(by = "marital_status").sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
propinsi_aumsum = demographics.groupby(by = "propinsi").sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
all_aumsum = demographics.groupby(by = ["age_bracket", "gender", "education", "occupation", "gross_income", "marital_status", "propinsi"]).sum().loc[:,["aum_rd","aum_sbn","aum_emas"]]
#%%msh nasabah, trx rutin, outliers
#Remove erroneous customer ids
data = data[data.customer_id > 0]
#Take only individual customers
data = data[data.customer_type == "individual"]
#Remove erroneous rows where kyc_date is NA
data = data[pd.notnull(data.kyc_date)].reset_index(drop = True)

demographics = data.copy()
#Remove people who haven't transacted
demographics = demographics[pd.notnull(demographics.first_trx_date)]
#Fill NAs with zero
demographics.iloc[:,13:39] = demographics.iloc[:,13:39].fillna(0)
demographics = demographics.reset_index(drop = True)

#Sum up the AUM of emas
aum_emas = pd.DataFrame(demographics.aum_masduit + demographics.aum_tamasia).round(decimals = 5)
aum_emas.columns = ["aum_emas"]
demographics = pd.concat([demographics, aum_emas], axis = 1)

#Count the days from first transaction
days_from_first_trx = [dt.datetime(2022, 4, 30) - x for x in demographics.first_trx_date]
days_from_first_trx = [x.days for x in days_from_first_trx]
days_from_first_trx = pd.DataFrame(days_from_first_trx)
days_from_first_trx.columns = ["days_from_first_trx"]
demographics = pd.concat([demographics, days_from_first_trx], axis = 1)

#Keep only people who are outliers
demographics_outliers_rd = demographics[demographics.aum_rd > 11000]
demographics_outliers_sbn = demographics[demographics.aum_sbn >= 0]
demographics_outliers_emas = demographics[demographics.aum_emas >= 0]
outliers_aumrd = demographics_outliers_rd[demographics_outliers_rd.aum_rd > np.quantile(demographics_outliers_rd.aum_rd, 0.75)+(1.5*(np.quantile(demographics_outliers_rd.aum_rd, [0.25,0.75])[1]-np.quantile(demographics_outliers_rd.aum_rd, [0.25,0.75])[0]))]
outliers_aumsbn = demographics_outliers_sbn
outliers_aumemas = demographics_outliers_emas
demographics = outliers_aumrd.copy()

#Save a copy of all outliers
demographics_totals_outliers = demographics.copy()

#Keep only those who transact routinely
demographics = demographics[(demographics.jlh_bl/demographics.days_from_first_trx)*30 > 1]

#Plot the proportion of outliers who routinely transact 
demographics_outliers_plot = pd.DataFrame([demographics.count()["customer_id"]/demographics_totals_outliers.count()["customer_id"]*100])
demographics_outliers_plot = pd.concat([demographics_outliers_plot, pd.DataFrame([100-(demographics.count()["customer_id"]/demographics_totals_outliers.count()["customer_id"])*100])], axis = 1)
demographics_outliers_plot.columns = ["outlier", "normal"]
demographics_outliers_plot = pd.melt(demographics_outliers_plot, value_vars = ["normal","outlier"])

fig, ax = plt.subplots(figsize = (10,25))

sns.histplot(data = demographics_outliers_plot, x = ["Rutin Transaksi","Rutin Transaksi"], weights = "value", hue = "variable", multiple = 'stack', ax = ax, shrink = 0.7, palette = ["tab:cyan", "tab:purple"])
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi Orang yang Rutin Transaksi dari yang Outlier", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.annotate("{c}\ndari\n{b}".format(b = demographics_totals_outliers.count()["customer_id"], c = demographics.count()["customer_id"]), (0,50), fontsize = 20, ha = "center")
#%%msh nasabah, outliers
#Remove erroneous customer ids
data = data[data.customer_id > 0]
#Take only individual customers
data = data[data.customer_type == "individual"]
#Remove erroneous rows where kyc_date is NA
data = data[pd.notnull(data.kyc_date)].reset_index(drop = True)

demographics = data.copy()
#Remove people who haven't transacted
demographics = demographics[pd.notnull(demographics.first_trx_date)]
#Fill NAs with zero
demographics.iloc[:,13:39] = demographics.iloc[:,13:39].fillna(0)
demographics = demographics.reset_index(drop = True)

#Split age into age brackets
age = [dt.datetime(2022, 4, 30) - x for x in demographics.date_of_birth]
age = [mt.floor(x.days/365.25) for x in age]
age_bracket = ["19 ke bawah" if x >= 16 and x <= 19 else "20-29" if x >= 20 and x <= 29 else "30-39" if x >= 30 and x <= 39 else "40-49" if x >= 40 and x <= 49 else "50-59" if x >= 50 and x <= 59 else "60-69" if x >= 60 and x <= 69 else "70 ke atas" for x in age]
age_bracket = pd.DataFrame(age_bracket)
age_bracket.columns = ["age_bracket"]
age = pd.DataFrame(age)
age.columns = ["age"]
demographics = pd.concat([demographics, age_bracket], axis = 1)
demographics = pd.concat([demographics, age], axis = 1)
aum_emas = pd.DataFrame(demographics.aum_masduit + demographics.aum_tamasia).round(decimals = 5)
aum_emas.columns = ["aum_emas"]
demographics = pd.concat([demographics, aum_emas], axis = 1)

#Keep only people who have AUM more than zero (indicating they are still customers)
demographics_total = demographics.copy()
demographics_total_outliers_rd = demographics_total[demographics_total.aum_rd > 0]
demographics_total_outliers_sbn = demographics_total[demographics_total.aum_sbn > 0]
demographics_total_outliers_emas = demographics_total[demographics_total.aum_emas > 0]
demographics_total = demographics_total_outliers_rd.merge(demographics_total_outliers_sbn, how = "outer")
demographics_total = demographics_total.merge(demographics_total_outliers_emas, how = "outer")

#Keep those who are outliers
demographics_outliers_rd = demographics[demographics.aum_rd > 11000]
demographics_outliers_sbn = demographics[demographics.aum_sbn > 0]
demographics_outliers_emas = demographics[demographics.aum_emas > 0]
outliers_aumrd = demographics_outliers_rd[demographics_outliers_rd.aum_rd > np.quantile(demographics_outliers_rd.aum_rd, 0.75)+(1.5*(np.quantile(demographics_outliers_rd.aum_rd, [0.25,0.75])[1]-np.quantile(demographics_outliers_rd.aum_rd, [0.25,0.75])[0]))]
outliers_aumsbn = demographics_outliers_sbn[demographics_outliers_sbn.aum_sbn > np.quantile(demographics_outliers_sbn.aum_sbn, 0.75)+(1.5*(np.quantile(demographics_outliers_sbn.aum_sbn, [0.25,0.75])[1]-np.quantile(demographics_outliers_sbn.aum_sbn, [0.25,0.75])[0]))]
outliers_aumemas = demographics_outliers_emas[demographics_outliers_emas.aum_emas > np.quantile(demographics_outliers_emas.aum_emas, 0.75)+(1.5*(np.quantile(demographics_outliers_emas.aum_emas, [0.25,0.75])[1]-np.quantile(demographics_outliers_emas.aum_emas, [0.25,0.75])[0]))]
demographics = outliers_aumrd.merge(outliers_aumsbn, how = "outer")
demographics = demographics.merge(outliers_aumemas, how = "outer")

#Count the proportion of customers who are outliers for each age bracket
age_bracket_outliers = pd.concat([demographics.groupby(by = "age_bracket").count().loc[:,"customer_id"], demographics_total.groupby(by = "age_bracket").count().loc[:,"customer_id"]], axis = 1)
age_bracket_outliers = pd.concat([age_bracket_outliers, pd.DataFrame([(age_bracket_outliers.iloc[x,0]/age_bracket_outliers.iloc[x,1])*100 for x in range(0,7)], index = age_bracket_outliers.index)], axis = 1)
age_bracket_outliers.columns = ["n_outliers", "n", "prop"]

#Count the proportion of customers who are outliers for each gender
gender_outliers = pd.concat([demographics.groupby(by = "gender").count().loc[:,"customer_id"], demographics_total.groupby(by = "gender").count().loc[:,"customer_id"]], axis = 1)
gender_outliers = pd.concat([gender_outliers, pd.DataFrame([(gender_outliers.iloc[x,0]/gender_outliers.iloc[x,1])*100 for x in range(0,2)], index = gender_outliers.index)], axis = 1)
gender_outliers.columns = ["n_outliers", "n", "prop"]

#Count the proportion of customers who are outliers for each level of education
education_outliers = pd.concat([demographics.groupby(by = "education").count().loc[:,"customer_id"], demographics_total.groupby(by = "education").count().loc[:,"customer_id"]], axis = 1)
education_outliers = pd.concat([education_outliers, pd.DataFrame([(education_outliers.iloc[x,0]/education_outliers.iloc[x,1])*100 for x in range(0,8)], index = education_outliers.index)], axis = 1)
education_outliers.columns = ["n_outliers", "n", "prop"]

#Count the proportion of customers who are outliers for each level of income
gross_income_outliers = pd.concat([demographics.groupby(by = "gross_income").count().loc[:,"customer_id"], demographics_total.groupby(by = "gross_income").count().loc[:,"customer_id"]], axis = 1)
gross_income_outliers = pd.concat([gross_income_outliers, pd.DataFrame([(gross_income_outliers.iloc[x,0]/gross_income_outliers.iloc[x,1])*100 for x in range(0,6)], index = gross_income_outliers.index)], axis = 1)
gross_income_outliers.columns = ["n_outliers", "n", "prop"]

#Make a boxplot of RD AUM to visualize the cutoff point for being an outlier
fig, ax = plt.subplots(figsize = (10,25))

sns.boxplot(data = demographics_outliers_rd, y = "aum_rd", ax = ax, color = "tab:olive")
plt.ylim(0, 10000000)
plt.yticks(fontsize = 15)
plt.annotate("~6.8 juta", (500, 935), fontsize = 15, xycoords = 'figure points', ha = "center")

#Make a boxplot of SBN AUM to visualize the cutoff point for being an outlier
fig, ax = plt.subplots(figsize = (10,25))

sns.boxplot(data = demographics_outliers_sbn, y = "aum_sbn", ax = ax, color = "tab:olive")
plt.ylim(0, 100000000)
plt.yticks(fontsize = 15)
plt.annotate("7.8 juta", (500, 1071), fontsize = 15, xycoords = 'figure points', ha = "center")

#Make a boxplot of Emas AUM to visualize the cutoff point for being an outlier
fig, ax = plt.subplots(figsize = (10,25))

sns.boxplot(data = demographics_outliers_emas, y = "aum_emas", ax = ax, color = "tab:olive")
plt.ylim(0, 5)
plt.yticks(fontsize = 15)
plt.annotate("1.20", (500, 335), fontsize = 15, xycoords = 'figure points', ha = "center")

#Determine general percentage of cusomters who are outliers
demographics_outliers_plot = pd.DataFrame([demographics.count()["customer_id"]/demographics_total.count()["customer_id"]*100])
demographics_outliers_plot = pd.concat([demographics_outliers_plot, pd.DataFrame([100-(demographics.count()["customer_id"]/demographics_total.count()["customer_id"])*100])], axis = 1)
demographics_outliers_plot.columns = ["outlier", "normal"]
demographics_outliers_plot = pd.melt(demographics_outliers_plot, value_vars = ["normal","outlier"])

fig, ax = plt.subplots(figsize = (10,25))

sns.histplot(data = demographics_outliers_plot, x = ["Nasabah","Nasabah"], weights = "value", hue = "variable", multiple = 'stack', ax = ax, shrink = 0.7, palette = ["tab:olive", "tab:orange"])
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi Orang yang Outlier", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.annotate("{c}\ndari\n{b}".format(b = demographics_total.count()["customer_id"], c = demographics.count()["customer_id"]), (0,40), fontsize = 20, ha = "center")

#Plot the proportion of customers who are outliers for each age bracket
age_bracket_outliers_plot = age_bracket_outliers.reset_index().iloc[:,0:4]
age_bracket_outliers_plot = pd.concat([age_bracket_outliers_plot, pd.DataFrame([100-x for x in age_bracket_outliers_plot.prop])], axis = 1)
age_bracket_outliers_plot["age_bracket"] = pd.Categorical(age_bracket_outliers_plot["age_bracket"])
age_bracket_outliers_plot = age_bracket_outliers_plot.sort_values("age_bracket")
age_bracket_outliers_plot.columns = ["age_bracket", "n_outliers", "n", "outlier", "normal"]
age_bracket_outliers_plot = pd.melt(age_bracket_outliers_plot, id_vars = ["age_bracket", "n", "n_outliers"], value_vars = ["normal", "outlier"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = age_bracket_outliers_plot, x = "age_bracket", weights = "value", hue = "variable", multiple = 'stack', ax = ax, shrink = 0.7, palette = ["tab:olive", "tab:orange"])
plt.xlabel("Kelompok Usia", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Kelompok Usia yang Outlier", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(age_bracket_outliers_plot)/2)):
  plt.annotate("{c}\ndari\n{b}".format(b = age_bracket_outliers_plot.loc[x, "n"], c = age_bracket_outliers_plot.loc[x, "n_outliers"]), (x,40), fontsize = 15, ha = "center")

#Plot the proportion of customers who are outliers for each gender
gender_outliers_plot = gender_outliers.sort_values(by = "prop", ascending = True).reset_index().iloc[:,0:4]
gender_outliers_plot = pd.concat([gender_outliers_plot, pd.DataFrame([100-x for x in gender_outliers_plot.prop])], axis = 1)
gender_outliers_plot.columns = ["gender", "n_outliers", "n", "outlier", "normal"]
gender_outliers_plot = pd.melt(gender_outliers_plot, id_vars = ["gender", "n", "n_outliers"], value_vars = ["normal", "outlier"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = gender_outliers_plot, x = "gender", weights = "value", hue = "variable", multiple = 'stack', ax = ax, shrink = 0.7, palette = ["tab:olive", "tab:orange"])
plt.xlabel("Jenis Kelamin", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Jenis Kelamin yang Outlier", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(gender_outliers_plot)/2)):
  plt.annotate("{c}\ndari\n{b}".format(b = gender_outliers_plot.loc[x, "n"], c = gender_outliers_plot.loc[x, "n_outliers"]), (x,40), fontsize = 15, ha = "center")

#Plot the proportion of customers who are outliers for each level of education
education_outliers_plot = education_outliers.reset_index().iloc[:,0:4]
education_outliers_plot = pd.concat([education_outliers_plot, pd.DataFrame([100-x for x in education_outliers_plot.prop])], axis = 1)
education_outliers_plot["education"] = pd.Categorical(education_outliers_plot["education"],["SD","SMP","SMA","D3","S1","S2","S3","Lainnya"])
education_outliers_plot = education_outliers_plot.sort_values("education")
education_outliers_plot.columns = ["education", "n_outliers", "n", "outlier", "normal"]
education_outliers_plot = pd.melt(education_outliers_plot, id_vars = ["education", "n", "n_outliers"], value_vars = ["normal", "outlier"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = education_outliers_plot, x = "education", weights = "value", hue = "variable", multiple = 'stack', ax = ax, shrink = 0.7, palette = ["tab:olive", "tab:orange"])
plt.xlabel("Tingkat Pendidikan", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Tingkat Pendidikan yang Outlier", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(education_outliers_plot)/2)):
  plt.annotate("{c}\ndari\n{b}".format(b = education_outliers_plot.loc[x, "n"], c = education_outliers_plot.loc[x, "n_outliers"]), (x,40), fontsize = 15, ha = "center")

#Plot the proportion of customers who are outliers for each level of income  
gross_income_outliers_plot = gross_income_outliers.sort_values(by = "prop", ascending = True).reset_index().iloc[:,0:4]
gross_income_outliers_plot = pd.concat([gross_income_outliers_plot, pd.DataFrame([100-x for x in gross_income_outliers_plot.prop])], axis = 1)
gross_income_outliers_plot.columns = ["gross_income", "n_outliers", "n", "outlier", "normal"]
gross_income_outliers_plot = pd.melt(gross_income_outliers_plot, id_vars = ["gross_income", "n", "n_outliers"], value_vars = ["normal", "outlier"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = gross_income_outliers_plot, x = "gross_income", weights = "value", hue = "variable", multiple = 'stack', ax = ax, shrink = 0.7, palette = ["tab:olive", "tab:orange"])
plt.xlabel("Tingkat Pendapatan", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Tingkat Pendapatan yang Outlier", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(gross_income_outliers_plot)/2)):
  plt.annotate("{c}\ndari\n{b}".format(b = gross_income_outliers_plot.loc[x, "n"], c = gross_income_outliers_plot.loc[x, "n_outliers"]), (x,50), fontsize = 15, ha = "center")    
#%%msh nasabah, trx rutin
#Remove erroneous customer ids
data = data[data.customer_id > 0]
#Take only individual customers
data = data[data.customer_type == "individual"]
#Remove erroneous rows where kyc_date is NA
data = data[pd.notnull(data.kyc_date)].reset_index(drop = True)

demographics = data.copy()
#Remove people who haven't transacted
demographics = demographics[pd.notnull(demographics.first_trx_date)]
#Fill NAs with zero
demographics.iloc[:,13:39] = demographics.iloc[:,13:39].fillna(0)
demographics = demographics.reset_index(drop = True)

#Split age into age brackets
age = [dt.datetime(2022, 4, 30) - x for x in demographics.date_of_birth]
age = [mt.floor(x.days/365.25) for x in age]
age_bracket = ["19 ke bawah" if x >= 16 and x <= 19 else "20-29" if x >= 20 and x <= 29 else "30-39" if x >= 30 and x <= 39 else "40-49" if x >= 40 and x <= 49 else "50-59" if x >= 50 and x <= 59 else "60-69" if x >= 60 and x <= 69 else "70 ke atas" for x in age]
age_bracket = pd.DataFrame(age_bracket)
age_bracket.columns = ["age_bracket"]
age = pd.DataFrame(age)
age.columns = ["age"]
demographics = pd.concat([demographics, age_bracket], axis = 1)
demographics = pd.concat([demographics, age], axis = 1)
aum_emas = pd.DataFrame(demographics.aum_masduit + demographics.aum_tamasia).round(decimals = 5)
aum_emas.columns = ["aum_emas"]
demographics = pd.concat([demographics, aum_emas], axis = 1)

#Count the days from first transaction
days_from_first_trx = [dt.datetime(2022, 4, 30) - x for x in demographics.first_trx_date]
days_from_first_trx = [x.days for x in days_from_first_trx]
days_from_first_trx = pd.DataFrame(days_from_first_trx)
days_from_first_trx.columns = ["days_from_first_trx"]
demographics = pd.concat([demographics, days_from_first_trx], axis = 1)

demographics_total = demographics.copy()

#Keep only people who have AUM more than zero (indicating they are still customers)
demographics_outliers_rd = demographics[demographics.aum_rd > 0]
demographics_outliers_sbn = demographics[demographics.aum_sbn > 0]
demographics_outliers_emas = demographics[demographics.aum_emas > 0]
outliers_aumrd = demographics_outliers_rd
outliers_aumsbn = demographics_outliers_sbn
outliers_aumemas = demographics_outliers_emas
demographics = outliers_aumrd.merge(outliers_aumsbn, how = "outer")
demographics = demographics.merge(outliers_aumemas, how = "outer")

#Save a copy of customers
demographics_totals_rutin_rd = demographics.copy()

#Keep only people who have transacted routinely
demographics = demographics[(demographics.jlh_bl/demographics.days_from_first_trx)*30 > 1]

#Count the proportion of customers who are routine for each age bracket 
age_bracket_rutin = pd.concat([demographics.groupby(by = "age_bracket").count().loc[:,"customer_id"], demographics_total.groupby(by = "age_bracket").count().loc[:,"customer_id"]], axis = 1)
age_bracket_rutin = pd.concat([age_bracket_rutin, pd.DataFrame([(age_bracket_rutin.iloc[x,0]/age_bracket_rutin.iloc[x,1])*100 for x in range(0,7)], index = age_bracket_rutin.index)], axis = 1)
age_bracket_rutin.columns = ["n_rutin", "n", "prop"]

#Count the proportion of customers who are routine for each gender
gender_rutin = pd.concat([demographics.groupby(by = "gender").count().loc[:,"customer_id"], demographics_total.groupby(by = "gender").count().loc[:,"customer_id"]], axis = 1)
gender_rutin = pd.concat([gender_rutin, pd.DataFrame([(gender_rutin.iloc[x,0]/gender_rutin.iloc[x,1])*100 for x in range(0,2)], index = gender_rutin.index)], axis = 1)
gender_rutin.columns = ["n_rutin", "n", "prop"]

#Count the proportion of customers who are routine for each level of education
education_rutin = pd.concat([demographics.groupby(by = "education").count().loc[:,"customer_id"], demographics_total.groupby(by = "education").count().loc[:,"customer_id"]], axis = 1)
education_rutin = pd.concat([education_rutin, pd.DataFrame([(education_rutin.iloc[x,0]/education_rutin.iloc[x,1])*100 for x in range(0,8)], index = education_rutin.index)], axis = 1)
education_rutin.columns = ["n_rutin", "n", "prop"]

#Count the proportion of customers who are routine for each level of income
gross_income_rutin = pd.concat([demographics.groupby(by = "gross_income").count().loc[:,"customer_id"], demographics_total.groupby(by = "gross_income").count().loc[:,"customer_id"]], axis = 1)
gross_income_rutin = pd.concat([gross_income_rutin, pd.DataFrame([(gross_income_rutin.iloc[x,0]/gross_income_rutin.iloc[x,1])*100 for x in range(0,6)], index = gross_income_rutin.index)], axis = 1)
gross_income_rutin.columns = ["n_rutin", "n", "prop"]

#Boxplot of transaction frequency
fig, ax = plt.subplots(figsize = (10,25))
sns.boxplot(y = (demographics.jlh_bl/demographics.days_from_first_trx)*30, data = demographics, ax = ax)
plt.ylim(0,10)
plt.title("Distribusi Frekuensi Transaksi Reksa Dana\ndari Nasabah yang Rutin Transaksi", fontsize = 20)
plt.ylabel("Frekuensi Transaksi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.annotate("{b}\ndari\n{c}".format(b = len(demographics), c = len(demographics_totals_rutin_rd)), (600, 1308), fontsize = 15, xycoords = 'figure points', ha = "right")
plt.annotate("(Orang yang\nmasih nasabah)".format(b = len(demographics), c = len(demographics_totals_rutin_rd)), (600, 1280), fontsize = 12, xycoords = 'figure points', ha = "right")

#Plot the proportion of customers who are routine for each age bracket
age_bracket_rutin_plot = pd.concat([demographics.groupby(by = "age_bracket").count()["customer_id"], demographics_totals_rutin_rd.groupby(by = "age_bracket").count()["customer_id"]], axis = 1).reset_index()
age_bracket_rutin_plot = pd.concat([age_bracket_rutin_plot, pd.DataFrame((age_bracket_rutin_plot.iloc[:,1]/age_bracket_rutin_plot.iloc[:,2])*100)], axis = 1)
age_bracket_rutin_plot = pd.concat([age_bracket_rutin_plot, pd.DataFrame([100-x for x in age_bracket_rutin_plot.iloc[:,3]])], axis = 1)
age_bracket_rutin_plot.columns = ["age_bracket", "n_rutin", "n", "rutin", "normal"]
age_bracket_rutin_plot = pd.melt(age_bracket_rutin_plot, id_vars = ["age_bracket", "n", "n_rutin"], value_vars = ["normal", "rutin"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = age_bracket_rutin_plot, x = "age_bracket", weights = "value", hue = "variable", multiple = "stack", ax = ax, shrink = 0.7, palette = ["tab:blue", "tab:red"])
plt.xlabel("Kelompok Usia", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Kelompok Usia yang Rutin Transaksi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(age_bracket_rutin_plot)/2)):
    plt.annotate("{c} rutin\n{b} tidak\nrutin".format(b = age_bracket_rutin_plot.loc[x, "n"], c = age_bracket_rutin_plot.loc[x, "n_rutin"]), (x,50), fontsize = 15, ha = "center")
    
#Plot the proportion of customers who are routine for each gender
gender_rutin_plot = pd.concat([demographics.groupby(by = "gender").count()["customer_id"], demographics_totals_rutin_rd.groupby(by = "gender").count()["customer_id"]], axis = 1).reset_index()
gender_rutin_plot = pd.concat([gender_rutin_plot, pd.DataFrame((gender_rutin_plot.iloc[:,1]/gender_rutin_plot.iloc[:,2])*100)], axis = 1)
gender_rutin_plot = pd.concat([gender_rutin_plot, pd.DataFrame([100-x for x in gender_rutin_plot.iloc[:,3]])], axis = 1)
gender_rutin_plot.columns = ["gender", "n_rutin", "n", "rutin", "normal"]
gender_rutin_plot = pd.melt(gender_rutin_plot, id_vars = ["gender", "n", "n_rutin"], value_vars = ["normal", "rutin"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = gender_rutin_plot, x = "gender", weights = "value", hue = "variable", multiple = "stack", ax = ax, shrink = 0.7, palette = ["tab:blue", "tab:red"])
plt.xlabel("Jenis Kelamin", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Jenis Kelamin yang Rutin Transaksi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(gender_rutin_plot)/2)):
    plt.annotate("{c} rutin\n{b} tidak\nrutin".format(b = gender_rutin_plot.loc[x, "n"], c = gender_rutin_plot.loc[x, "n_rutin"]), (x,50), fontsize = 15, ha = "center")

#Plot the proportion of customers who are routine for each level of income    
education_rutin_plot = pd.concat([demographics.groupby(by = "education").count()["customer_id"], demographics_totals_rutin_rd.groupby(by = "education").count()["customer_id"]], axis = 1).reset_index()
education_rutin_plot = pd.concat([education_rutin_plot, pd.DataFrame((education_rutin_plot.iloc[:,1]/education_rutin_plot.iloc[:,2])*100)], axis = 1)
education_rutin_plot = pd.concat([education_rutin_plot, pd.DataFrame([100-x for x in education_rutin_plot.iloc[:,3]])], axis = 1)
education_rutin_plot.columns = ["education", "n_rutin", "n", "rutin", "normal"]
education_rutin_plot["education"] = pd.Categorical(education_rutin_plot["education"],["SD", "SMP", "SMA", "D3", "S1", "S2", "S3", "Lainnya"])
education_rutin_plot = education_rutin_plot.sort_values("education").reset_index(drop = True)
education_rutin_plot = pd.melt(education_rutin_plot, id_vars = ["education", "n", "n_rutin"], value_vars = ["normal", "rutin"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = education_rutin_plot, x = "education", weights = "value", hue = "variable", multiple = "stack", ax = ax, shrink = 0.7, palette = ["tab:blue", "tab:red"])
plt.xlabel("Tingkat Pendidikan", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Tingkat Pendidikan yang Rutin Transaksi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(education_rutin_plot)/2)):
    plt.annotate("{c} rutin\n{b} tidak\nrutin".format(b = education_rutin_plot.loc[x, "n"], c = education_rutin_plot.loc[x, "n_rutin"]), (x,50), fontsize = 15, ha = "center")

#Plot the proportion of customers who are routine for each level of income
gross_income_rutin_plot = pd.concat([demographics.groupby(by = "gross_income").count()["customer_id"], demographics_totals_rutin_rd.groupby(by = "gross_income").count()["customer_id"]], axis = 1).reset_index()
gross_income_rutin_plot = pd.concat([gross_income_rutin_plot, pd.DataFrame((gross_income_rutin_plot.iloc[:,1]/gross_income_rutin_plot.iloc[:,2])*100)], axis = 1)
gross_income_rutin_plot = pd.concat([gross_income_rutin_plot, pd.DataFrame([100-x for x in gross_income_rutin_plot.iloc[:,3]])], axis = 1)
gross_income_rutin_plot.columns = ["gross_income", "n_rutin", "n", "rutin", "normal"]
gross_income_rutin_plot["gross_income"] = pd.Categorical(gross_income_rutin_plot["gross_income"],['< 10 juta / tahun','> 10 – 50 juta / tahun','> 50 – 100 juta / tahun','> 100 – 500 juta / tahun','> 500 juta – 1 milyar / tahun','> 1 milyar / tahun'])
gross_income_rutin_plot = gross_income_rutin_plot.sort_values("gross_income").reset_index(drop = True)
gross_income_rutin_plot = pd.melt(gross_income_rutin_plot, id_vars = ["gross_income", "n", "n_rutin"], value_vars = ["normal", "rutin"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.histplot(data = gross_income_rutin_plot, x = "gross_income", weights = "value", hue = "variable", multiple = "stack", ax = ax, shrink = 0.7, palette = ["tab:blue", "tab:red"])
plt.xlabel("Tingkat Pendapatan", fontsize = 20)
plt.ylabel("Proporsi(%)", fontsize = 20)
plt.title("Proporsi per Tingkat Pendapatan yang Rutin Transaksi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
for x in range(int(len(gross_income_rutin_plot)/2)):
    plt.annotate("{c} rutin\n{b} tidak\nrutin".format(b = gross_income_rutin_plot.loc[x, "n"], c = gross_income_rutin_plot.loc[x, "n_rutin"]), (x,50), fontsize = 15, ha = "center")    
#%%pernah trx
#Remove erroneous customer ids
data = data[data.customer_id > 0]
#Take only individual customers
data = data[data.customer_type == "individual"]
#Remove erroneous rows where kyc_date is NA
data = data[pd.notnull(data.kyc_date)].reset_index(drop = True)

demographics = data.copy()
#Remove people who haven't transacted
demographics = demographics[pd.notnull(demographics.first_trx_date)]
#Fill NAs with zero
demographics.iloc[:,13:39] = demographics.iloc[:,13:39].fillna(0)
demographics = demographics.reset_index(drop = True)

#Sum up all the jlh for SBN
jlh_sbn = demographics.loc[:,"jlh_sbr"] + demographics.loc[:,"jlh_ori"] + demographics.loc[:,"jlh_st"] + demographics.loc[:,"jlh_sr"]
jlh_sbn = pd.DataFrame(jlh_sbn)
jlh_sbn.columns = ["jlh_sbn"]
#Sum up all the jlh for emas
jlh_emas = demographics.loc[:,"jlh_beli_masduit"] + demographics.loc[:,"jlh_beli_cetak_masduit"] + demographics.loc[:,"jlh_beli_tamasia"]
jlh_emas = pd.DataFrame(jlh_emas)
jlh_emas.columns = ["jlh_emas"]
demographics = pd.concat([demographics, jlh_sbn], axis=1)
demographics = pd.concat([demographics, jlh_emas], axis=1)

#If jlh > 0, return 1, meaning they've invested in that type of investment beforehand
for x in ["jlh_bl","jlh_sbn","jlh_emas"]:
    temp = pd.DataFrame([1 if y > 0 else 0 for y in demographics.loc[:,x]])
    temp.columns = [x + "_binary"]
    demographics = pd.concat([demographics,temp], axis = 1)

#Split age into age brackets
age = [dt.datetime(2022, 4, 30) - x for x in demographics.date_of_birth]
age = [mt.floor(x.days/365.25) for x in age]
age_bracket = ["19 ke bawah" if x >= 16 and x <= 19 else "20-29" if x >= 20 and x <= 29 else "30-39" if x >= 30 and x <= 39 else "40-49" if x >= 40 and x <= 49 else "50-59" if x >= 50 and x <= 59 else "60-69" if x >= 60 and x <= 69 else "70 ke atas" for x in age]
age_bracket = pd.DataFrame(age_bracket)
age_bracket.columns = ["age_bracket"]
age = pd.DataFrame(age)
age.columns = ["age"]
demographics = pd.concat([demographics, age_bracket], axis = 1)
demographics = pd.concat([demographics, age], axis = 1)

#Sum up the AUM of emas
aum_emas = pd.DataFrame(demographics.aum_masduit + demographics.aum_tamasia).round(decimals = 5)
aum_emas.columns = ["aum_emas"]
demographics = pd.concat([demographics, aum_emas], axis = 1)

#Save an unfiltered copy of demographics
demographics_total = demographics.copy()

#Determine the proportion of customers who have invested in RD, SBN and Emas for each age bracket
age_bracket_prop = pd.DataFrame(demographics.groupby(by = "age_bracket").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
age_bracket_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
age_bracket_n = pd.DataFrame(demographics.groupby(by = "age_bracket").count()["jlh_bl_binary"])
age_bracket_n.columns = ["n"]
age_bracket_pref = pd.concat([age_bracket_prop, age_bracket_n], axis = 1)

#Determine the proportion of customers who have invested in RD, SBN and Emas for each gender
gender_prop = pd.DataFrame(demographics.groupby(by = "gender").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
gender_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
gender_n = pd.DataFrame(demographics.groupby(by = "gender").count()["jlh_bl_binary"])
gender_n.columns = ["n"]
gender_pref = pd.concat([gender_prop, gender_n], axis = 1)

#Determine the proportion of customers who have invested in RD, SBN and Emas for each level of education
education_prop = pd.DataFrame(demographics.groupby(by = "education").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
education_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
education_n = pd.DataFrame(demographics.groupby(by = "education").count()["jlh_bl_binary"])
education_n.columns = ["n"]
education_pref = pd.concat([education_prop, education_n], axis = 1)

#Determine the proportion of customers who have invested in RD, SBN and Emas for each level of income
gross_income_prop = pd.DataFrame(demographics.groupby(by = "gross_income").mean().loc[:,["jlh_bl_binary","jlh_sbn_binary","jlh_emas_binary"]])
gross_income_prop.columns = ["rd_prop", "sbn_prop", "emas_prop"]
gross_income_n = pd.DataFrame(demographics.groupby(by = "gross_income").count()["jlh_bl_binary"])
gross_income_n.columns = ["n"]
gross_income_pref = pd.concat([gross_income_prop, gross_income_n], axis = 1)

#Plot the proportion of customers who have invested in RD, SBN and Emas for each age bracket
age_bracket_pref_plot = age_bracket_pref.reset_index().iloc[:,0:4]
age_bracket_pref_plot = age_bracket_pref_plot.melt(id_vars = ["age_bracket"], value_vars = ["rd_prop", "sbn_prop", "emas_prop"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.barplot(data = age_bracket_pref_plot, x = "variable", y = "value", hue = "age_bracket", ax = ax)
plt.xlabel("Jenis Investasi", fontsize = 20)
plt.ylabel("Proporsi", fontsize = 20)
plt.title("Proporsi dari Tiap Kelompok Usia yang Pernah Investasi di Tiap Jenis Investasi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.axhline(y = np.mean(demographics.jlh_bl_binary), xmin = 0.0225, xmax = 0.31, color = "black")
plt.axhline(y = np.mean(demographics.jlh_sbn_binary), xmin = 0.355, xmax = 0.6425, color = "black")
plt.axhline(y = np.mean(demographics.jlh_emas_binary), xmin = 0.6875, xmax = 0.9775, color = "black")

#Plot the proportion of customers who have invested in RD, SBN and Emas for each gender
gender_pref_plot = gender_pref.reset_index().iloc[:,0:4]
gender_pref_plot = gender_pref_plot.melt(id_vars = ["gender"], value_vars = ["rd_prop", "sbn_prop", "emas_prop"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.barplot(data = gender_pref_plot, x = "variable", y = "value", hue = "gender", ax = ax, palette = ["tab:blue", "tab:pink"])
plt.xlabel("Jenis Investasi", fontsize = 20)
plt.ylabel("Proporsi", fontsize = 20)
plt.title("Proporsi dari Tiap Jenis Kelamin yang Pernah Investasi di Tiap Jenis Investasi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.axhline(y = np.mean(demographics.jlh_bl_binary), xmin = 0.0225, xmax = 0.31, color = "black")
plt.axhline(y = np.mean(demographics.jlh_sbn_binary), xmin = 0.355, xmax = 0.6425, color = "black")
plt.axhline(y = np.mean(demographics.jlh_emas_binary), xmin = 0.6875, xmax = 0.9775, color = "black")

#Plot the proportion of customers who have invested in RD, SBN and Emas for each level of education
education_pref_plot = education_pref.reset_index().iloc[:,0:4]
education_pref_plot["education"] = pd.Categorical(education_pref_plot["education"],["SD", "SMP", "SMA", "D3", "S1", "S2", "S3", "Lainnya"])
education_pref_plot = education_pref_plot.sort_values("education").reset_index(drop = True)
education_pref_plot = education_pref_plot.melt(id_vars = ["education"], value_vars = ["rd_prop", "sbn_prop", "emas_prop"])


fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.barplot(data = education_pref_plot, x = "variable", y = "value", hue = "education", ax = ax)
plt.xlabel("Jenis Investasi", fontsize = 20)
plt.ylabel("Proporsi", fontsize = 20)
plt.title("Proporsi dari Tiap Tingkat Pendidikan yang Pernah Investasi di Tiap Jenis Investasi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.axhline(y = np.mean(demographics.jlh_bl_binary), xmin = 0.0225, xmax = 0.31, color = "black")
plt.axhline(y = np.mean(demographics.jlh_sbn_binary), xmin = 0.355, xmax = 0.6425, color = "black")
plt.axhline(y = np.mean(demographics.jlh_emas_binary), xmin = 0.6875, xmax = 0.9775, color = "black")

#Plot the proportion of customers who have invested in RD, SBN and Emas for each level of income
gross_income_pref_plot = gross_income_pref.reset_index().iloc[:,0:4]
gross_income_pref_plot["gross_income"] = pd.Categorical(gross_income_pref_plot["gross_income"],['< 10 juta / tahun','> 10 – 50 juta / tahun','> 50 – 100 juta / tahun','> 100 – 500 juta / tahun','> 500 juta – 1 milyar / tahun','> 1 milyar / tahun'])
gross_income_pref_plot = gross_income_pref_plot.sort_values("gross_income").reset_index(drop = True)
gross_income_pref_plot = gross_income_pref_plot.melt(id_vars = ["gross_income"], value_vars = ["rd_prop", "sbn_prop", "emas_prop"])

fig, ax = plt.subplots(figsize = (20.625,13.75))

sns.barplot(data = gross_income_pref_plot, x = "variable", y = "value", hue = "gross_income", ax = ax)
plt.xlabel("Jenis Investasi", fontsize = 20)
plt.ylabel("Proporsi", fontsize = 20)
plt.title("Proporsi dari Tiap Tingkat Pendapatan yang Pernah Investasi di Tiap Jenis Investasi", fontsize = 20)
plt.xticks(fontsize = 15)
plt.yticks(fontsize = 15)
plt.axhline(y = np.mean(demographics.jlh_bl_binary), xmin = 0.0225, xmax = 0.31, color = "black")
plt.axhline(y = np.mean(demographics.jlh_sbn_binary), xmin = 0.355, xmax = 0.6425, color = "black")
plt.axhline(y = np.mean(demographics.jlh_emas_binary), xmin = 0.6875, xmax = 0.9775, color = "black")