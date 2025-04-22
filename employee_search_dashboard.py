
import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(layout="wide", page_title="نظام البحث عن معلومات الموظف")
st.image("logo.jpeg", width=100)
st.title("🔍 نظام البحث عن معلومات الموظف")

@st.cache_data
def load_data():
    df = pd.read_excel("Book2.xlsx")
    df.fillna("", inplace=True)
    
    # تحويل أيام الحضور إلى قيم رقمية
    days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    for day in days:
        df[day] = df[day].apply(lambda x: 1 if str(x).strip() in ['1', 'V'] else 0)
    
    # حساب إجمالي أيام الحضور
    df['أيام الحضور'] = df[days].sum(axis=1)
    return df

df = load_data()

# تبويبات رئيسية
tab1, tab2 = st.tabs(["🔎 البحث الأساسي", "📊 التحليلات الذكية"])

with tab1:
    query = st.text_input("أدخل اسم الموظف أو الهوية أو أي معلومة أخرى", key="search_tab1")
    
    if query.strip():
        results = df[df.astype(str).apply(lambda row: row.str.contains(query, case=False, na=False)).any(axis=1)]
        if not results.empty:
            st.success(f"تم العثور على {len(results)} نتيجة مطابقة ✅")
            st.dataframe(results, use_container_width=True)
            towrite = io.BytesIO()
            results.to_excel(towrite, index=False)
            st.download_button("💾 تحميل Excel", data=towrite.getvalue(), file_name="search_results.xlsx")
        else:
            st.warning("⚠️ لا توجد نتائج مطابقة")

with tab2:
    st.header("📈 لوحة التحليلات الذكية")

    subtab1, subtab2, subtab3, subtab4, subtab5, subtab6, subtab7, subtab8 = st.tabs([
        "🗓️ غياب دائم بنفس اليوم", "🌍 الحضور حسب الجنسية", "🏢 الحضور حسب القسم", 
        "🔻 أقل 10 حضورًا", "📅 حضروا يومًا فقط", "📆 توزيع الحضور", 
        "🕌 حضروا في العطلات", "📊 تصنيف حسب أيام الحضور"
    ])

    with subtab1:
        st.subheader("الموظفون الغائبون دائمًا في نفس اليوم")
        for day in ['SUN', 'MON', 'TUE', 'WED', 'THU']:
            absentees = df[df[day] == 0]
            st.write(f"🔴 الغياب الدائم يوم {day} - عددهم: {len(absentees)}")
            st.dataframe(absentees[['NAME (ENG)', 'ID#', day]])

    with subtab2:
        st.subheader("نسبة الحضور حسب الجنسية")
        nationality_att = df.groupby('NATIONALITY')['أيام الحضور'].mean().reset_index()
        fig = px.pie(nationality_att, names='NATIONALITY', values='أيام الحضور', title='توزيع الحضور حسب الجنسية')
        st.plotly_chart(fig, use_container_width=True)

    with subtab3:
        st.subheader("نسبة الحضور حسب القسم")
        dept_att = df.groupby('COMPANY')['أيام الحضور'].mean().reset_index()
        fig = px.bar(dept_att, x='COMPANY', y='أيام الحضور', title='متوسط أيام الحضور لكل قسم')
        st.plotly_chart(fig, use_container_width=True)

    with subtab4:
        st.subheader("أقل 10 موظفين حضورًا")
        least_att = df.nsmallest(10, 'أيام الحضور')[['NAME (ENG)', 'ID#', 'NATIONALITY', 'أيام الحضور']]
        st.dataframe(least_att, use_container_width=True)

    with subtab5:
        st.subheader("الموظفون الذين حضروا يومًا واحدًا فقط")
        one_day_att = df[df['أيام الحضور'] == 1][['NAME (ENG)', 'ID#', 'NATIONALITY', 'أيام الحضور']]
        st.dataframe(one_day_att, use_container_width=True)

    with subtab6:
        st.subheader("توزيع الحضور اليومي")
        day_dist = df[['SUN', 'MON', 'TUE', 'WED', 'THU']].mean().reset_index()
        day_dist.columns = ['اليوم', 'نسبة الحضور']
        fig = px.line(day_dist, x='اليوم', y='نسبة الحضور', title='نسبة الحضور خلال أيام الأسبوع')
        st.plotly_chart(fig, use_container_width=True)

    with subtab7:
        st.subheader("الموظفون الذين حضروا في أيام العطلات")
        weekend_att = df[(df['FRI'] == 1) | (df['SAT'] == 1)]
        st.dataframe(weekend_att[['NAME (ENG)', 'FRI', 'SAT']], use_container_width=True)

    with subtab8:
        st.subheader("تصنيف الموظفين حسب عدد أيام الحضور")
        att_bins = [0, 2, 4, 6, 7]
        labels = ['ضعيف', 'متوسط', 'جيد', 'ممتاز']
        df['التصنيف'] = pd.cut(df['أيام الحضور'], bins=att_bins, labels=labels)
        rating_dist = df['التصنيف'].value_counts().reset_index()
        fig = px.pie(rating_dist, names='index', values='التصنيف', title='توزيع التصنيف')
        st.plotly_chart(fig, use_container_width=True)

# الشريط الجانبي
with st.sidebar:
    st.subheader("📘 دليل الاستخدام")
    st.markdown("اختر تبويب البحث أو التحليلات لرؤية بيانات الموظفين.")
