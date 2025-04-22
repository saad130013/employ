
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="تحليل التصنيف حسب الجنسية أو الموقع")
st.title("📊 تصنيف الحضور حسب الجنسية أو الموقع")

@st.cache_data
def load_data():
    df = pd.read_excel("Book2.xlsx")
    df.fillna("", inplace=True)
    
    days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    for day in days:
        df[day] = df[day].apply(lambda x: 1 if str(x).strip() in ['1', 'V'] else 0)

    df['أيام الحضور'] = df[days].sum(axis=1)

    bins = [0, 2, 4, 6, 7]
    labels = ['ضعيف', 'متوسط', 'جيد', 'ممتاز']
    df['التصنيف'] = pd.cut(df['أيام الحضور'], bins=bins, labels=labels, include_lowest=True)

    return df

df = load_data()

mode = st.radio("اختر طريقة التحليل:", ["حسب الجنسية", "حسب الموقع"])

if mode == "حسب الجنسية":
    option = st.selectbox("اختر الجنسية", df['NATIONALITY'].unique())
    filtered = df[df['NATIONALITY'] == option]
    group_col = "NATIONALITY"
else:
    option = st.selectbox("اختر الموقع", df['LOCATION'].unique())
    filtered = df[df['LOCATION'] == option]
    group_col = "LOCATION"

if not filtered.empty:
    count_df = filtered['التصنيف'].value_counts().reset_index()
    count_df.columns = ['التصنيف', 'عدد الموظفين']
    total = count_df['عدد الموظفين'].sum()
    count_df['النسبة المئوية'] = round((count_df['عدد الموظفين'] / total) * 100, 2)

    st.dataframe(count_df, use_container_width=True)

    fig = px.pie(count_df, names='التصنيف', values='عدد الموظفين',
                 title=f"نسبة التصنيفات - {option}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("لا توجد بيانات مطابقة.")
