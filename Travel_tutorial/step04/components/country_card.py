import streamlit as st

def render_country_page(flag: str, country_name: str, country_description: str, country_url: str):    
    st.title(f'{flag} {country_name}')
    st.header(country_name)
    st.write(country_description)
    st.link_button(
        label=f'{country_name} 공식 관광청 방문',
        url=country_url
    )