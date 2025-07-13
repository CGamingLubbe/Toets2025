import requests
import pandas as pd
import time
import os
from googlesearch import search
import re
import datetime
import streamlit as st

COUNTRY_CODE_MAP = {
    '+1': 'USA',
    '+27': 'South Africa',
    '+44': 'UK',
    '+91': 'India',
    '+61': 'Australia',
    '+49': 'Germany',
    '+33': 'France',
    '+258': 'Mozambique',
    '+255': 'Tanzania',
    '+254': 'Kenya',
    '+261': 'Madagascar',
    '+230': 'Mauritius',
    '+248': 'Seychelles'
    # Add more codes as needed
}

TLD_MAP = {
    "South Africa": ".co.za",
    "Kenya": ".co.ke",
    "USA": ".com",
    "UK": ".co.uk",
    "India": ".in",
    "Germany": ".de",
    "France": ".fr",
    "Australia": ".com.au",
    "Mozambique": ".mz",
    "Tanzania": ".co.tz",
    "Madagascar": ".mg",
    "Mauritius": ".mu",
    "Seychelles": ".sc"
}

# Function to extract data from website
def get_company_details(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            page_content = response.text
            phone = "N/A"
            email = "N/A"
            name = "N/A"
            address = "N/A"
            country_from_code = ""

            # Try to get title as name
            title_match = re.search(r'<title>(.*?)</title>', page_content, re.IGNORECASE)
            if title_match:
                name = title_match.group(1).strip()

            phone_match = re.findall(r'(\+\d{1,4}[\s-]?(\(?\d{1,4}\)?)[\s-]?\d{3,4}[\s-]?\d{3,4})', page_content)
            if phone_match:
                phone = phone_match[0][0]
                for code, country in COUNTRY_CODE_MAP.items():
                    if phone.startswith(code):
                        country_from_code = country
                        break

            email_match = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_content)
            if email_match:
                email = email_match[0]

            address_match = re.search(r'(\d{1,5}\s+\w+\s+(Street|St|Avenue|Ave|Rd|Road|Blvd|Boulevard|Lane|Ln|Drive|Dr)\b.*?)<', page_content, re.IGNORECASE)
            if address_match:
                address = address_match.group(1).strip()
            elif country_from_code:
                address = country_from_code

            return name, address, phone, email, country_from_code
    except:
        return "N/A", "N/A", "N/A", "N/A"
    return "N/A", "N/A", "N/A", "N/A"

# The main scraping function
def run_scraper(max_duration_minutes, stop_flag):
    timer_placeholder = st.empty()

    keywords = ["Stainless steel", "Roof Sheeting", "Glass", "extrusion film", "sandwich panels"]
    countries = ["Mosambique", "Tanzania", "Kenya", "Madagascar", "Seychelles", "Mauritius"]
    output_file = os.path.join(os.getcwd(), "companies.xlsx")


    if os.path.exists(output_file):
        df_existing = pd.read_excel(output_file, engine="openpyxl")
        existing_urls = set(df_existing["Company Website"].tolist())
    else:
        existing_urls = set()

    data = []
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(minutes=max_duration_minutes)

    keep_running = True
    while datetime.datetime.now() < end_time and keep_running:
# ⏳ Live updating countdown
        remaining = end_time - datetime.datetime.now()
        if remaining.total_seconds() > 0:
            hrs, rem = divmod(int(remaining.total_seconds()), 3600)
            mins, secs = divmod(rem, 60)
            timer_placeholder.info(f"⏳ Time remaining: {hrs:02}:{mins:02}:{secs:02}")


        for keyword in keywords:
            for country in countries:
                if datetime.datetime.now() >= end_time:
                    break
                query = f"{keyword} in {country} contact details"
                st.write(f"🔍 Searching: {query}")
                try:
                    results = search(query, num_results=50)


                    for url in results:
                        if datetime.datetime.now() >= end_time:
                            break
                        if url not in existing_urls and not any(skip in url for skip in ["maps.google.", "facebook.com", "linkedin.com", "instagram.com", "youtube.com", "twitter.com", "yelp.com"]):
                            expected_tld = TLD_MAP.get(country, "").lower()
                            if expected_tld and expected_tld not in url.lower():
                                continue  # ❌ Skip if the URL doesn’t match the expected country domain

                            time.sleep(2)
                            name, address, phone, email, detected_country = get_company_details(url)
                            # ✅ Final check — does the detected country match the one we're searching for?
                            if detected_country.lower() != country.lower():
                                continue
                            # ✅ Only save if at least one field is not N/A
                            if any(field != "N/A" for field in [name, phone, email, address]):
                                data.append([name, url, phone, email, address, keyword])
                                existing_urls.add(url)


                            
                        #    df = pd.DataFrame(data, columns=["Company Name", "Company Website", "Contact Number", "Email Address", "Address", "Keyword"])
                        #    df.to_excel(output_file, index=False, engine="openpyxl")
                        #    st.write(f"✅ Saved {len(data)} new records.")
                        #    data.clear()

                    if stop_flag():
                        keep_running = False
                        break

                except Exception as e:
                    st.write(f"⚠️ Error searching for {query}: {e}")
                    st.write("📁 Current working directory:", os.getcwd())
                    st.write("💾 Output file will be saved to:", output_file)


    st.success("✅ Scraping session complete.")
    timer_placeholder.empty()




# Save all collected data after scraping session ends
    if data:
        st.write(f"📝 Total collected: {len(data)}")  # Debug print

        output_file = "companies.xlsx"

        if os.path.exists(output_file):
            df_existing = pd.read_excel(output_file, engine="openpyxl")
            df_new = pd.DataFrame(data, columns=["Company Name", "Company Website", "Contact Number", "Email Address", "Address", "Keyword"])
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = pd.DataFrame(data, columns=["Company Name", "Company Website", "Contact Number", "Email Address", "Address", "Keyword"])

        try:
            df_combined.to_excel(output_file, index=False, engine="openpyxl")
            st.success(f"✅ {len(df_combined)} total records saved to {output_file}")
        except PermissionError:
            st.error("❌ Could not write to Excel. Please close the file first.")


# Try to open the Excel file at the end
if st.button("📂 Open Excel Results"):
    try:
        os.startfile("companies.xlsx")  # ✅ Only opens if user clicks button
    except Exception as e:
        st.warning(f"⚠️ Could not open the file: {e}")

    

# Streamlit user interface
def main():
    st.title("🕸️ Company Web Scraper")

    duration = st.number_input("How long should it run? (minutes)", min_value=1, max_value=180, value=30)
    stop_flag = st.checkbox("Stop after current run")
    if st.button("Start Scraping"):
        run_scraper(duration, lambda: stop_flag)
        
    if st.button("🗑️ Clear All Saved Results"):
        output_file = "companies.xlsx"
        empty_df = pd.DataFrame(columns=["Company Name", "Company Website", "Contact Number", "Email Address", "Address", "Keyword"])
        try:
            empty_df.to_excel(output_file, index=False, engine="openpyxl")
            st.success("✅ All results cleared successfully.")
        except Exception as e:
            st.error(f"❌ Could not clear the file: {e}")


if __name__ == "__main__":
    main()
