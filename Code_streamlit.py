
# 정답 코드를 작성해주세요

import streamlit as st
import pandas as pd
import plotly.express as px
import time

from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# 데이터 로드 함수
@st.cache_data

def get_crawling():

    # Selenium으로 HTML 가져오기
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url = 'https://www.saramin.co.kr/'
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    # 검색창 클릭
    search_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="btn_search"]')))
    search_button.click()
    
    # 데이터분석 입력
    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ipt_keyword_recruit')))
    search_box.send_keys('데이터분석') 

    # # 검색 버튼 클릭
    search_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="btn_search_recruit"]')))
    search_button.click()
    time.sleep(2)

    # 채용 정보 추출
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='item_recruit')

    saramin_data = []

    for item in items:  
        try:
            # 회사 추출
            corp_element = item.find('strong', class_='corp_name')
            company = corp_element.get_text().strip() if corp_element else ''

            # 제목 추출
            title_element = item.find('h2', class_='job_tit')
            title = title_element.get_text().strip() if title_element else ''

            # detail 추출
            condition_element = item.find('div', class_='job_condition')
            conditions = condition_element.find_all('span')
            detail = []
            for condition in conditions:
                detail.append(condition.get_text().strip())
            
            # url 추출
            link_element = item.find('a', target='_blank')
            url = link_element.get('href') if link_element else ''     


            # 데이터 저장
            saramin_data.append({
                'Site': 'Saramin',
                'Col_Company': company,
                'Col_Recuit': title,
                'Col_detail': detail,
                'Col_url': "https://www.saramin.co.kr" + url
            })
            
        except Exception as e:
            print(f"데이터 추출 중 오류 발생: {e}")
            continue

    # # 종료
    # driver.quit()

    # 데이터프레임 생성
    saramin_df = pd.DataFrame(saramin_data)


    # # Selenium으로 HTML 가져오기
    # service = Service(executable_path=ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service)

    url2 = 'https://www.jobkorea.co.kr/'
    driver.get(url2)
    wait = WebDriverWait(driver, 10)

    # 데이터분석 입력
    search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#stext')))
    search_box.send_keys('데이터분석') 

    search_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="common_search_btn"]')))
    search_button.click()
    time.sleep(2)
    
    # 채용 정보 추출
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='Flex_display_flex__i0l0hl2 Flex_gap_space28__i0l0hl2a styles_p_space28__dk46ts8d')

    jobkorea_data = []

    for item in items:  
        try:
            # 회사 추출
            corp_element = item.find('div', class_='Flex_display_flex__i0l0hl2 Flex_align_center__i0l0hl8 Flex_justify_space-between__i0l0hlf styles_mb_space4__dk46ts23')
            company = corp_element.get_text().strip() if corp_element else ''

            # 제목 추출
            title_element = item.find('span', class_='Typography_variant_size18__344nw25 Typography_weight_medium__344nw2d Typography_color_gray900__344nw2l')
            title = title_element.get_text().strip() if title_element else ''

            # detail 추출
            condition_element = item.find('div', class_='Flex_display_flex__i0l0hl2 Flex_gap_space16__i0l0hlj Flex_direction_row__i0l0hl3')
            conditions = condition_element.find_all('span')
            detail = []
            for condition in conditions:
                detail.append(condition.get_text().strip())
                
            # url 추출
            link_element = item.find('a', class_='sn28bt0')
            url = link_element.get('href') if link_element else ''

            # 데이터 저장
            jobkorea_data.append({
                'Site': 'Job_Korea',
                'Col_Company': company,
                'Col_Recuit': title,
                'Col_detail': detail,
                'Col_url': url
            })
            
        except Exception as e:
            print(f"데이터 추출 중 오류 발생: {e}")
            continue

    # 종료
    driver.quit()

    # 데이터프레임 생성
    jobkorea_df = pd.DataFrame(jobkorea_data)

    # 두 데이터프레임 합치기
    df_combined = pd.concat([jobkorea_df, saramin_df], ignore_index=True)

    return df_combined


def grouped_df(df, group_col):
    grouped = df.groupby(group_col).size().reset_index(name='Count')
    grouped['Ratio'] = (grouped['Count'] / grouped['Count'].sum() * 100).round(2)
    
    return grouped
    

def pie_chart(df, values_col, names_col):
    fig = px.pie(df, 
                 values=values_col, 
                 names=names_col 
                 )  
    return fig

# ----------------------- 메인 함수----------------------------
if __name__ == "__main__":

    st.title('Title')   #큰글씨

    with st.form('news_form', clear_on_submit=True):     # form : 박스(영역) 만들기
        submitted = st.form_submit_button('Recruit Searching')   # 버튼을 추가합니다.

        if submitted:  # 클릭했을때
            df1 = get_crawling()
            df2 = grouped_df(df1, 'Site')
            fig = pie_chart(df2, 'Ratio', 'Site')

            st.dataframe(df1)

            col1, col2, col3 = st.columns(3)
            with col1:  
                st.dataframe(df2)

            st.write('Recruitment Ratio')    #작은 글씨    
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
