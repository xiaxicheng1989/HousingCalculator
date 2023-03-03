import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
def monthPay0(r_m, n_m, P):
    return r_m*(1+r_m)**n_m*P/((1+r_m)**n_m-1)

def monthPay(r, n, P):
    r_m = r/12
    n_m = n *12
    return monthPay0(r_m, n_m, P)
def debt(initValue, repay_y, rateMort, years):
    def new_debt(value, repay, rate):
        return (value -repay)*(1+rate)
    
    value = initValue
    for year in range(0,years+1):
        if year == 0:
            value = initValue
        else:
            value = new_debt(value, repay_y, rateMort)
    if value< 0:
        return 0
    else:
        return value

def buying(housePX,deposit, repay_y, years, inflR, rateMort, scvCharge_y):
    repayPV = np.sum([repay_y/(1+inflR)**year if year>0 else 0 for year in range(0,years+1)])
    rest_debt_PV = debt(housePX-deposit, repay_y, rateMort, years)/((1+inflR)**years)
    return -repayPV+housePX-rest_debt_PV-scvCharge_y*years

def invest_rent(years,deposit, marketR, repay):
    investment = deposit*((1+marketR)**years)/((1+inflR)**years)
    rent = repay*years
    return investment-rent

def shared_owner(housePX,deposit, years,scvCharge_y):
    rent = (housePX-deposit)*0.03
    repayPV = rent*years
    return -repayPV+deposit-scvCharge_y*years
    



st.title('Property calculator')
st.markdown("""**Objective:**

Comparing the cost of living over time to determine if purchasing a property is a wise decision given an economic condition. Cases to be compared are:  
- Buying a property X with deposit Y and resell it at the end of the period
- Invest the deposit into the market and continue paying rent
- Buying a property under shared ownership and paying reduced rent until the end of the period and resell the share. 
- Cash in the bank at saving interest rate and paying rent

Cost of living is measured in total amount of money spent or gained within a timeframe in present value (income is positive, expenses (rent, mortgate, fees) are negative).

**Assumptions:** 
1. Property can be sold at the same value as purchased
2. Property price, rents and service charge increase with the inflation rate
3. Deposit used to buy shares of ownership, rent determined by the 3% of the remaining shares plus service charge
4. All rates are fixed
5. Transaction fees (lawyer fees ignored)

--------------------------------------------------------------------
""")


personal_tab, property_tab, mortgage_tab, economy_tab = st.columns(4)
with personal_tab:
    st.markdown("""**Personal finance:**""")
    deposit = st.number_input('Insert deposit',min_value =0, value = 100000)
with property_tab:
    st.markdown("""**Property information:**""")
    housePX = st.number_input('Insert a property price',min_value =0, value = 350000)
    scvCharge_y = st.number_input('Insert annual service charge',min_value =0, value = 2000)
    rent_flat_market = st.number_input('Assumed normal renting price per month',min_value =0, value = 1600)
with mortgage_tab:
    st.markdown("""**Mortgage condition:**""")
    morgageR = st.number_input('Annual mortgage rate [%]',min_value =0.0,max_value = 100.0,value = 6.0,format="%.1f")/100
    mort_Years = st.number_input('Repayment term',min_value =0,max_value = 100,value = 25)
with economy_tab:
    st.markdown("""**Economy condition:**""")
    marketR = st.number_input('Assumed market return [%] for investment',min_value =0.0,max_value = 100.0,value = 10.0,format="%.1f")/100
    inflR = st.number_input('Inflation [%]',min_value =0.0,max_value = 100.0,value = 7.0,format="%.1f")/100
    savingR = st.number_input('Saving interest [%]',min_value =0.0,max_value = 100.0,value = 3.0,format="%.1f")/100

st.markdown("-------------------------------")    
month_repay = monthPay(morgageR, mort_Years, housePX-deposit)
st.write(f'<p style="font-size: 40px;">Monthly mortgage repayment: £{round(month_repay,0)}</p>', unsafe_allow_html=True)

repay_y = 12*monthPay(morgageR, mort_Years, housePX-deposit)

df = pd.DataFrame(data={
    'Buying + Mortgate + Service charge':[buying(housePX,deposit, repay_y, year, inflR, morgageR, scvCharge_y) for year in range(26)],
    'Invested + full rent': [invest_rent(year,deposit, marketR, rent_flat_market*12) for year in range(26)],
    'Shared + adj. rent + Service charge' : [shared_owner(housePX,deposit, year, scvCharge_y) for year in range(26)],
    'Cash + full rent' : [deposit*(1+savingR)**year/((1+inflR)**year)-rent_flat_market*12*year for year in range(26)],
    'Years' : range(26)
})
df = df.set_index('Years')


fig = px.line(df)

st.plotly_chart(fig)