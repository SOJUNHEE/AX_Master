# 인코딩 자동 감지 + 한글 폰트 막대 그래프
# 여러 인코딩("uft-8-sig","cp949","euc-kr") 순서대로 시도
# 내가 쓸 폰트 같은 경로에 있어야 함
# 막대그래프 생성 후 그림으로 저장 (chart.png)
# 실행 streamlit run 2026.09.07_test_3.py

import os
import matplotlib.pyplot as plt  #matplotlib 차트
import pandas as pd
import streamlit as st
from matplotlib import font_manager

st.title("📊인코딩 자동 감지+한글 폰트 막대 그래프(Titanic 연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실등급별 생존율을 그래프로 표현")

# 📌 14번 라인 수정: itanic_cleaned.csv -> titanic_cleaned.csv (t 추가)
csv_path = os.path.join(os.path.dirname(__file__),"titanic_cleaned.csv")
font_path = os.path.join(os.path.dirname(__file__),"NanumGothicBold.otf")

# 여러 인코딩("uft-8-sig","cp949","euc-kr") 순서대로(함수로만듬)
# 제미나이 사용
def load_data_with_encodings(file_path):           
    
    """
    여러 한글 인코딩 방식을 순차적으로 시도하여 데이터프레임을 읽어오는 함수
    """
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    
    for enc in encodings:
        try:
            # 해당 인코딩으로 파일 읽기 시도
            df = pd.read_csv(file_path, encoding=enc)
            st.success(f"✅ 인코딩 감지 성공: `{enc}`")
            return df, enc
        except UnicodeDecodeError:
            # 인코딩이 맞지 않아 글자가 깨질 경우 다음 인코딩으로 넘어감
            continue
        except Exception as e:
            # 파일 없음 등의 다른 오류는 즉시 중단하고 알림
            st.error(f"❌ 파일 읽기 중 오류 발생: {e}")
            return None, None
            
    # 3가지 인코딩이 모두 실패했을 경우
    st.error("❌ 지원하는 인코딩(utf-8-sig, cp949, euc-kr)으로 파일을 열 수 없습니다.")
    return None, None


# 인코딩 자동 감지로 CSV읽기
st.subheader("1) 인코딩 자동 감지")

df, used_enc = load_data_with_encodings(csv_path)

st.markdown('---')

# 📌 54번 라인 이후: 데이터(df)가 정상적으로 존재할 때만 아래 코드가 실행되도록 안전장치 추가
if df is not None:
    # 객실등급(Pclass)별 생존율 집계
    # Survived 사망 = 0 , 생존 = 1 로 등급별 평균을 내면 그대로가 등급의 생존 비율이 된다.
    # 1은 1끼리, 2는 2끼리 -> 1끼리의 그룹 통계
    survival_summary = (df.groupby("Pclass")["Survived"].mean() * 100).round(1).rename("생존율(%)")
    st.dataframe(survival_summary, use_container_width=True)

    # 차트그리기
    st.markdown('---')
    st.subheader("2) 객실 등급별 생존율 막대그래프")

    try : 
        # 폰트 파일이 없으면 FileNotFoundError가 발생
        font_prop = font_manager.FontProperties(fname=font_path)
        # matplotlib font_manager에 폰트를 등록
        font_manager.fontManager.addfont(font_path)
        # 등록한 폰트를 기본 폰트로 설정하는 코드
        plt.rc('font', family=font_prop.get_name()) 
        
        st.write('NanumGothicBold 폰트를 적용했습니다.')

    except FileNotFoundError :
        st.warning('폰트파일을 찾을 수가 없습니다.')

    fig, ax = plt.subplots(figsize=(8,5))

    # pclass_survival_rate 대신 위에서 만든 survival_summary 사용 및 rot=0 적용
    survival_summary.plot(kind='bar', color='blue', ax=ax, rot=0) 

    ax.set_title('객실 등급별 생존율')
    ax.set_xlabel('객실등급(Pclass)')
    ax.set_ylabel('생존율(%)')

    st.pyplot(fig)

    output_png = os.path.join(os.path.dirname(__file__),"chart.png")
    fig.savefig(output_png)
    st.success("그림파일 다운이 완료 되었습니다.")

else:
    st.info("데이터를 불러오지 못해 차트와 표를 생성할 수 없습니다.")