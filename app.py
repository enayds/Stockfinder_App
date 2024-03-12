import hmac
import streamlit as st
# importing dependencies
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')


def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


# ----------------------------------------------------------main code-----------------------------------------------------------------------



# loading and caching the df to save memory
@st.cache_data()
def load_data():
    df = pd.read_parquet('C:/Users/DELL/Stockfinder App/Stock Data/merged_data.parquet', engine='fastparquet')
    df_fund = pd.read_parquet('C:/Users/DELL/Stockfinder App/Stock Data/df_fundamentals.parquet', engine='fastparquet')
    
    # merge both data to have a full data
    df_merged =  pd.merge(df, df_fund, on="instrument_id")
    return df_merged

df = load_data()



# Placeholder functions for each feature. Implement these based on the final selection of features.
def instrument_insights_dashboard():
    st.header("Instrument Insights Dashboard")

    # Dropdown for selecting an instrument
    selected_instrument = st.selectbox("Select an Instrument", df['name_x'].unique())

    # Filtering data for the selected instrument
    instrument_data = df[df['name_x'] == selected_instrument]

    # Display key metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="PE Ratio", value=instrument_data['pe'].iloc[0])
    with col2:
        st.metric(label="PS Ratio", value=instrument_data['ps'].iloc[0])
    with col3:
        st.metric(label="EPS", value=instrument_data['eps'].iloc[0])
    with col4:
        st.metric(label="PB Ratio", value=instrument_data['pb'].iloc[0])
    with col5:
        st.metric(label="Dividend Yield", value=f"{instrument_data['dividend_yield'].iloc[0]}%")
    st.subheader("Financial Performance Over Time")

    annual_data = instrument_data.groupby('year').agg({
    'totalRevenue': 'sum',
    'netIncome': 'sum',
    'debtToEquityRatio': 'mean',
    'cashFlowOperating': 'sum'
}).reset_index()

    # Create subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))
    fig.suptitle('Financial Metrics Trend Over Years')

    # Total Revenue
    axes[0, 0].plot(annual_data['year'], annual_data['totalRevenue'], marker='o')
    axes[0, 0].set_title('Total Revenue')
    axes[0, 0].set_ylabel('Revenue')
    axes[0, 0].grid()

    # Net Income
    axes[0, 1].plot(annual_data['year'], annual_data['netIncome'], marker='o', color='green')
    axes[0, 1].set_title('Net Income')
    axes[0, 1].set_ylabel('Income')
    axes[0, 1].grid()

    # Debt to Equity Ratio
    axes[1, 0].plot(annual_data['year'], annual_data['debtToEquityRatio'], marker='o', color='red')
    axes[1, 0].set_title('Debt to Equity Ratio')
    axes[1, 0].set_ylabel('Ratio')
    axes[1, 0].grid()

    # Cash Flow from Operating Activities
    axes[1,1].plot(annual_data['year'], annual_data['cashFlowOperating'], marker='o', color='purple')
    axes[1, 1].set_title('Cash Flow from Operating Activities')
    axes[1, 1].set_ylabel('Cash Flow')
    axes[1, 1].grid()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    st.pyplot(fig)

    instrument_details = df[df['name_x'] == selected_instrument].iloc[0]
    current_price = instrument_details['price']
    currency = instrument_details['currency_x']
    exchange_country = instrument_details['exchange_country']


    st.markdown(f"""
        ### Current Price and Exchange Information
        - **Current Price**: **{current_price} {currency}**
        - **Exchange Country**: *{exchange_country}*

        This presents the most recent trading price for *{selected_instrument}* and the primary country where it is traded. Understanding the current price in relation to historical trends can offer insights into potential market movements and the intrinsic value of the instrument.
    """, unsafe_allow_html=True)



def stock_filter():
    # Introduction
    st.header("Stock Filter")
    st.markdown("""
    Use the sliders below to filter stocks based on various financial metrics such as price, P/E ratio, dividend yield, debt-to-equity ratio, and operating income. Adjust the sliders to define your criteria and click the "Search" button to find stocks that match your preferences.
    """)

    # Define minimum and maximum values for each filter
    min_price = df['price'].min()
    max_price = df['price'].max()
    min_pe_ratio = df['pe'].min()
    max_pe_ratio = df['pe'].max()
    min_dividend_yield = df['dividend_yield'].min()
    max_dividend_yield = df['dividend_yield'].max()
    min_debt_to_equity_ratio = df['debtToEquityRatio'].min()
    max_debt_to_equity_ratio = df['debtToEquityRatio'].max()
    min_operating_income = df['operatingIncome'].min()
    max_operating_income = df['operatingIncome'].max()

    # Add filter options with limited range
    selected_filters = {}
     # collecting the sector column
    all_sectors = df['sectorL1'].unique().tolist()
    all_sectors_option = "All"
    selected_sectors = st.multiselect("Select Sector(s)", [all_sectors_option] + all_sectors, default=all_sectors_option)

    selected_filters['Price'] = st.slider("Price", min_price, max_price, (min_price, max_price))
    selected_filters['PE Ratio'] = st.slider("PE Ratio", min_pe_ratio, max_pe_ratio, (min_pe_ratio, max_pe_ratio))
    selected_filters['Dividend Yield'] = st.slider("Dividend Yield", min_dividend_yield, max_dividend_yield, (min_dividend_yield, max_dividend_yield))
    selected_filters['Debt-to-Equity Ratio'] = st.slider("Debt-to-Equity Ratio", min_debt_to_equity_ratio, max_debt_to_equity_ratio, (min_debt_to_equity_ratio, max_debt_to_equity_ratio))
    selected_filters['Operating Income'] = st.slider("Operating Income", min_operating_income, max_operating_income, (min_operating_income, max_operating_income))

    if all_sectors_option in selected_sectors:
            filtered_by_sector_df = df
    else:
        filtered_by_sector_df = df[df['sectorL1'].isin(selected_sectors)]


    # Search button
    if st.button("Search"):
        # Apply filters on the sector-filtered DataFrame
        filtered_df = filtered_by_sector_df[
            (filtered_by_sector_df['price'] >= selected_filters['Price'][0]) & (filtered_by_sector_df['price'] <= selected_filters['Price'][1]) &
            (filtered_by_sector_df['pe'] >= selected_filters['PE Ratio'][0]) & (filtered_by_sector_df['pe'] <= selected_filters['PE Ratio'][1]) &
            (filtered_by_sector_df['dividend_yield'] >= selected_filters['Dividend Yield'][0]) & (filtered_by_sector_df['dividend_yield'] <= selected_filters['Dividend Yield'][1]) &
            (filtered_by_sector_df['debtToEquityRatio'] >= selected_filters['Debt-to-Equity Ratio'][0]) & (filtered_by_sector_df['debtToEquityRatio'] <= selected_filters['Debt-to-Equity Ratio'][1]) &
            (filtered_by_sector_df['operatingIncome'] >= selected_filters['Operating Income'][0]) & (filtered_by_sector_df['operatingIncome'] <= selected_filters['Operating Income'][1])
        ]
        
        # Sentence after fetching results
        if 'All' in selected_sectors:
            st.write("You have selected stocks from all sectors.")
        else:
            selected_sectors_text = ", ".join(selected_sectors)
            st.write(f"You have selected stocks from the following sectors: {selected_sectors_text}.")


        filter_summary = f" With a price range from {selected_filters['Price'][0]} to {selected_filters['Price'][1]}, "
        filter_summary += f"a P/E Ratio from **{selected_filters['PE Ratio'][0]}** to {selected_filters['PE Ratio'][1]}, "
        filter_summary += f"a Dividend Yield from {selected_filters['Dividend Yield'][0]} to {selected_filters['Dividend Yield'][1]}, "
        filter_summary += f"a Debt-to-Equity Ratio from {selected_filters['Debt-to-Equity Ratio'][0]} to {selected_filters['Debt-to-Equity Ratio'][1]}, and "
        filter_summary += f"an Operating Income from {selected_filters['Operating Income'][0]} to {selected_filters['Operating Income'][1]}."
        
        st.write(filter_summary)

        # collect price for only 2023 since we are looking for stocks to invest in presently
        filtered_df = filtered_df.loc[filtered_df.year == 2023]
        # Sort by price column
        filtered_df = filtered_df.sort_values(by='price', ascending=False)

        # Select unique stocks
        unique_stocks = filtered_df['instrument_id'].unique()

        # Initialize a DataFrame to store the top 5 unique stocks
        top_5_unique_stocks = pd.DataFrame(columns=filtered_df.columns)

        # Iterate through unique stocks and select the first occurrence
        for stock in unique_stocks:
            top_5_unique_stocks = pd.concat([top_5_unique_stocks, filtered_df[filtered_df['instrument_id'] == stock].head(1)])
        # Show top 5 results
        st.subheader("Top 5 Results Based on Price")
        if not top_5_unique_stocks.empty:
            st.dataframe(top_5_unique_stocks.head(5))
            # entering the stock naratives here
            count = 1
            for index, row in top_5_unique_stocks.head(5).iterrows():
                introduction = (f"Let's dive into **{row['long_name']}** ({row['symbol']}), "
                                f"a standout in the {row['sectorL1']} sector. With its base in {row['exchange_country']}, "
                                f"{row['long_name']} has been making waves with its innovative approaches. "
                                f"Currently priced at **{row['price']}** **({row['currency_x']})**, it reflects the market's valuation at this snapshot in time. "
                                f"Learn more about this company [here]({row['url']}).")

                financial_performance = (f"As of the latest reporting period ending in {row['year']}, "
                                        f"{row['long_name']} reported a total revenue of **{row['totalRevenue']}**, "
                                        f"with a net income of **{row['netIncome']}**. The operating income stood at **{row['operatingIncome']}**, "
                                        f"highlighting its operational efficiency.")

                valuation = (f"The market has currently valued {row['long_name']} with a P/E ratio of **{row['pe']}**, "
                            f"and a P/B ratio of **{row['pb']}**. The earnings per share (EPS) is noted at **{row['eps']}**, "
                            f"indicating its market perception.")

                investment_considerations = (f"For dividend-seeking investors, {row['long_name']}'s dividend yield is at **{row['dividend_yield']}%** "
                                            f"with a dividend per share of **{row['dividend_per_share']}**. The debt-to-equity ratio stands at "
                                            f"**{row['debtToEquityRatio']}**, which explains the company's financial leverage.")

                introduction = (f"Let's dive into **{row['long_name']}** ({row['symbol']}), "
                f"a standout in the {row['sectorL1']} sector with its base in {row['exchange_country']}. "
                f"Currently priced at **${row['price']}**, it offers a glimpse into the market's valuation of its potential. "
                f"For a deeper understanding, let's explore what makes {row['long_name']} unique.")

                company_description_intro = f"**About {row['long_name']}**: At the heart of [Company Name]'s success is its core business philosophy and strategic initiatives:"
                company_description = row['description']  


                final_thoughts = (f"Considering the growth in its key metrics, {row['long_name']} might be a good addition to your portfolio, "
                                f"particularly if you're looking at the {row['sectorL1']} sector with a risk tolerance perspective.")

                # Combine all the parts to form the final narrative for each stock
                final_narrative = "\n\n".join([introduction, financial_performance, valuation, 
                investment_considerations, final_thoughts, company_description_intro, company_description])
                
                # Use Markdown for better text formatting and wrapping
                st.subheader(f"#{count}: {row['long_name']}")
                st.markdown(final_narrative, unsafe_allow_html=True)
            

                # # Assuming 'date' and 'price' in your DataFrame, and 'symbol' for stock identification
                # # Plot the price trend for the selected stock
                # plt.figure(figsize=(10, 4))
                # sns.lineplot(data=row, x='year', y='price', marker='o', sort=True)  # sort=True ensures the data is sorted by the x-axis (year)
                # plt.title(f"{row['long_name']} Price Trend")
                # plt.xlabel("Year")
                # plt.ylabel("Price ($)")
                # plt.xticks(rotation=45)
                # st.pyplot(plt)

                st.markdown("---")
                count +=1


        else:
            st.write("No stocks found matching the selected criteria.")



def main():
    st.sidebar.title("Stock Finder Features")
    feature = st.sidebar.selectbox("Choose a feature", [
        "Instrument Insights Dashboard", "Stock Filter Analysis"
    ])

    if feature == "Instrument Insights Dashboard":
        instrument_insights_dashboard()
    elif feature == "Stock Filter Analysis":
        stock_filter()
   




# ----------------------------------------------------------main code-----------------------------------------------------------------------


if not check_password():
    st.stop()


if __name__ == "__main__":
    main()
