import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Title of the app
st.title('Which channel is this MQL coming from?')

# Create an empty DataFrame with the required columns
df = pd.DataFrame(columns=[
    'Recent Conversion Date',
    'Doctor/Facility - UTM medium [Forms] [NEW]',
    'Doctor/Facility - UTM source [Forms] [NEW]',
    "Doctor/Facility - UTM campaign [Forms]",
    'Doctor/Facility - Last Page Seen Freeze when MQL [WF]',
    'Doctor/Facility - Source [SO]',
    'Doctor/Facility - Last source [SO]',
    'Latest Source',
    'Latest Source Drill-Down 1'
])

# Function to manually input data using Streamlit widgets
def input_contact():
    contact = {}
    contact['Recent Conversion Date'] = st.date_input("Enter Recent Conversion Date", value=datetime.now())
    contact['Doctor/Facility - UTM medium [Forms] [NEW]'] = st.text_input("Enter UTM medium")
    contact['Doctor/Facility - UTM source [Forms] [NEW]'] = st.text_input("Enter UTM source")
    contact["Doctor/Facility - UTM campaign [Forms]"] = st.text_input("Enter UTM campaign")
    contact['Doctor/Facility - Last Page Seen Freeze when MQL [WF]'] = st.text_input("Enter Last Page Seen")
    contact['Doctor/Facility - Source [SO]'] = st.text_input("Enter Source [SO]")
    contact['Doctor/Facility - Last source [SO]'] = st.text_input("Enter Last Source [SO]")
    contact['Latest Source'] = st.text_input("Enter Latest Source")
    contact['Latest Source Drill-Down 1'] = st.text_input("Enter Latest Source Drill-Down 1")

    return contact

# Insert contact manually into the dataframe
new_contact = input_contact()
# Convert the dictionary to a DataFrame with one row
new_contact_df = pd.DataFrame([new_contact])
# Concatenate the DataFrames
df = pd.concat([df, new_contact_df], ignore_index=True)

# Function to assign 'mql_channel' based on the provided rules and track the rule block
def assign_mql_channel(row):
    rule_block = 'Unknown'

    if pd.notna(row['Recent Conversion Date']):
        recent_conversion_date = pd.to_datetime(row['Recent Conversion Date'], errors='coerce')
        if recent_conversion_date and recent_conversion_date >= datetime.now() - timedelta(days=5):
            if pd.notna(row['Doctor/Facility - UTM medium [Forms] [NEW]']) and pd.notna(
                    row['Doctor/Facility - UTM source [Forms] [NEW]']):
                utm_medium = row['Doctor/Facility - UTM medium [Forms] [NEW]'].lower()
                utm_source = row['Doctor/Facility - UTM source [Forms] [NEW]'].lower()
                utm_campaign = row.get("Doctor/Facility - UTM campaign [Forms]", '').lower()

                if utm_medium == 'paid-social' and ('facebook' in utm_source or 'fb' in utm_source) and 'mal' not in utm_campaign:
                    return 'Paid Social [Facebook]', 'UTM'
                if utm_medium == 'paid-social' and utm_source == 'linkedin' and 'mal' not in utm_campaign:
                    return 'Paid Social [LinkedIn]', 'UTM'
                if utm_medium == 'ppc' and utm_source == 'google' and 'mal' not in utm_campaign:
                    return 'Paid Search [Google]', 'UTM'
                if 'paid' in utm_medium and 'bing' in utm_source:
                    return 'Paid Search [Bing]', 'UTM'
                if utm_medium == 'display' and 'google' in utm_source and 'mal' not in utm_campaign:
                    return 'Display [Google]', 'UTM'
                if utm_medium == 'display' and 'criteo' in utm_source and 'mal' not in utm_campaign:
                    return 'Display [Criteo]', 'UTM'
                if utm_source == 'hs_email' or (utm_medium == 'email' and utm_source == 'hubspot'):
                    return 'Email [HS]', 'UTM'
                if utm_source == 'softdoit':
                    return 'Referral [Softdoit]', 'UTM'
                if utm_medium == 'sms':
                    return 'Message Tool [SMS]', 'UTM'
                if utm_medium == 'whatsapp' or utm_source == 'whatsapp':
                    return 'Message Tool [WhatsApp]', 'UTM'
                if 'event' in utm_medium:
                    return 'Event', 'UTM'
                if utm_source == 'beamer' or 'beamer' in utm_campaign:
                    return 'Beamer', 'UTM'
                if utm_source == 'marketplace' or 'mkpl' in utm_medium:
                    return 'Banner [MKTPL]', 'UTM'
                if 'popup' in utm_campaign or 'pop-up' in utm_campaign:
                    return 'Pop-up [Pro Zone]', 'UTM'
                if utm_medium in ['organic-social', 'social'] and 'facebook' in utm_source:
                    return 'Organic Social [Facebook]', 'UTM'
                if 'socialmedia_organic' in utm_campaign or 'instagram' in utm_source:
                    return 'Organic Social [Instagram]', 'UTM'
                if utm_medium in ['organic-social', 'social'] and 'linkedin' in utm_source:
                    return 'Organic Social [LinkedIn]', 'UTM'

    last_page = row['Doctor/Facility - Last Page Seen Freeze when MQL [WF]']
    if pd.notna(last_page):
        if 'utm_source=hs_email' in last_page or ('medium=email' in last_page and last_page.endswith('S')):
            return 'Email [HS one-shot]', 'Last Page Seen'
        if 'utm_source=hs_automation' in last_page or ('medium=email' in last_page and 'AUTO' in last_page):
            return 'Email [HS nurturing]', 'Last Page Seen'
        if 'medium=email' in last_page:
            return 'Email [HS]', 'Last Page Seen'
        if 'utm_medium=paid-social' in last_page and 'utm_source=facebook' in last_page:
            return 'Paid Social [Facebook]', 'Last Page Seen'
        if ('utm_medium=ppc' in last_page and 'utm_source=google' in last_page) or (
                'utm_medium=cpc' in last_page and 'utm_source=google' in last_page):
            return 'Paid Search [Google]', 'Last Page Seen'
        if 'utm_source=criteo' in last_page and 'utm_medium=display' in last_page:
            return 'Display [Criteo]', 'Last Page Seen'
        if ('utm_source=MKTP' in last_page and 'utm_campaign=banner' in last_page) or (
                'utm_source=marketplace' in last_page and 'utm_medium=edit_bar' in last_page):
            return 'Banner [MKTPL]', 'Last Page Seen'
        if 'utm_source=whatsapp' in last_page:
            return 'Message Tool [WhatsApp]', 'Last Page Seen'

    source_so = row['Doctor/Facility - Source [SO]']
    last_source_so = row['Doctor/Facility - Last source [SO]']
    if source_so == 'Event' or last_source_so == 'Event':
        return 'Event', 'Source/Last Source'
    if source_so == 'Sales demo ordered [Callcenter]':
        return 'CallCenter', 'Source/Last Source'
    if source_so == 'Internal reference' or last_source_so == 'Customer reference':
        return 'Offline reference', 'Source/Last Source'
    if source_so == 'Offline gift':
        return 'Offline campaign', 'Source/Last Source'
    if 'Direct email' in [source_so, last_source_so]:
        return 'Email [HS]', 'Source/Last Source'

    latest_source = row['Latest Source']
    latest_source_dd1 = row['Latest Source Drill-Down 1']
    if latest_source == 'Paid Social' and latest_source_dd1 == 'Facebook':
        return 'Paid Social [Facebook]', 'Latest Source'
    if latest_source == 'Paid Social' and latest_source_dd1 == 'Linkedin':
        return 'Paid Social [LinkedIn]', 'Latest Source'
    if latest_source == 'Paid Search':
        return 'Paid Search [Google]', 'Latest Source'
    if latest_source == 'Direct Traffic':
        return 'Direct Traffic', 'Latest Source'
    if latest_source == 'Organic Social' and latest_source_dd1 == 'Facebook':
        return 'Organic Social [Facebook]', 'Latest Source'
    if latest_source == 'Organic Social' and latest_source_dd1 == 'Instagram':
        return 'Organic Social [Instagram]', 'Latest Source'
    if latest_source == 'Organic Social' and latest_source_dd1 == 'LinkedIn':
        return 'Organic Social [LinkedIn]', 'Latest Source'

    return 'Unknown', 'Unknown'

# Apply the function to the new row
df[['mql_channel', 'rule_block']] = df.apply(assign_mql_channel, axis=1, result_type='expand')

# Display the final result using Streamlit
st.write(df)
