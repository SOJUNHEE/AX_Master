# 3단계 : 공식 멀티페이지 기능으로 파일 나누기
- 사이드바에 있는 메뉴창이 네비게이션 역할을 한다.

##
-st.page('파일경로', 'title', icon=...., default=True)
-st.navigation([...]) + pg.run()
폴더구조 : app.py 는 조립만 하고 실제 화면 내용은 view\파일이 담당

##
"""
bash
cd..
cd step03
streamlit run app.py

