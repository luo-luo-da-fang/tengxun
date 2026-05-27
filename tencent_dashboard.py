import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import qrcode
from PIL import Image
from io import BytesIO

# 页面基础配置
st.set_page_config(page_title="腾讯控股年报综合分析看板", layout="wide", page_icon="🐧")
st.title("📊 腾讯控股(00700)年度财报综合数据分析看板")
st.divider()

# 2021-2024腾讯年报基础数据 单位：亿元
tencent_data = pd.DataFrame({
    "年份": [2021, 2022, 2023, 2024],
    "营业收入": [5601.18, 5545.52, 6090.15, 6602.57],
    "营业成本": [2120.55, 2089.36, 2267.82, 2456.31],
    "归母净利润": [2248.22, 1882.43, 1152.16, 1940.73],
    "总资产": [16123.64, 15781.31, 15772.46, 17809.95],
    "总负债": [7356.71, 7952.71, 7035.65, 7270.99],
    "股东权益": [8766.93, 7828.60, 8736.81, 10538.96],
    "经营现金流净额": [1751.86, 1460.91, 2219.62, 2585.21],
    "增值服务营收": [2916.71, 2875.59, 2876.44, 3252.08],
    "金融科技及企业服务营收": [1722.00, 1771.52, 2170.39, 2378.52],
    "营销服务营收": [886.69, 827.75, 958.62, 1015.26],
    "中国大陆营收": [4929.04, 4879.10, 5361.33, 5815.36],
    "海外营收": [672.14, 666.42, 728.82, 787.21],
})

# 侧边筛选面板
with st.sidebar:
    st.header("🔍 财报筛选控制面板")
    upload_file = st.file_uploader("上传本地年报CSV数据", type="csv")
    if upload_file:
        tencent_data = pd.read_csv(upload_file)
    year_list = tencent_data["年份"].tolist()
    select_year = st.select_slider("选择查看年份", options=year_list, value=max(year_list))

# ====================== 批量计算扩充财务分析指数 ======================
# 盈利类指数
tencent_data["毛利率%"] = round((tencent_data["营业收入"] - tencent_data["营业成本"]) / tencent_data["营业收入"] * 100, 2)
tencent_data["净利润率%"] = round(tencent_data["归母净利润"] / tencent_data["营业收入"] * 100, 2)
tencent_data["净资产收益率%"] = round(tencent_data["归母净利润"] / tencent_data["股东权益"] * 100, 2)

# 成长类指数
tencent_data["营收同比增速%"] = round(tencent_data["营业收入"].pct_change() * 100, 2)
tencent_data["净利润同比增速%"] = round(tencent_data["归母净利润"].pct_change() * 100, 2)

# 偿债类指数
tencent_data["资产负债率%"] = round(tencent_data["总负债"] / tencent_data["总资产"] * 100, 2)
tencent_data["负债权益比%"] = round(tencent_data["总负债"] / tencent_data["股东权益"] * 100, 2)

# 运营类指数
tencent_data["资产周转率"] = round(tencent_data["营业收入"] / tencent_data["总资产"], 3)

# 筛选当前选中年份数据
year_detail = tencent_data[tencent_data["年份"] == select_year].iloc[0]
china_total = year_detail["中国大陆营收"]

# ====================== 核心升级：中国34个省级行政区数据（含经纬度） ======================
province_full_data = pd.DataFrame({
    "省份": [
        "北京市", "天津市", "河北省", "山西省", "内蒙古自治区",
        "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省",
        "浙江省", "安徽省", "福建省", "江西省", "山东省",
        "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区",
        "海南省", "重庆市", "四川省", "贵州省", "云南省",
        "西藏自治区", "陕西省", "甘肃省", "青海省", "宁夏回族自治区",
        "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区", "台湾省"
    ],
    "纬度": [
        39.9042, 39.0842, 38.0428, 37.8706, 40.8263,
        41.8045, 43.8868, 45.7366, 31.2304, 32.0603,
        30.2741, 31.8612, 26.0745, 28.6756, 36.6758,
        34.7466, 30.5928, 28.2282, 23.1291, 22.8152,
        20.0440, 29.4316, 30.6572, 26.6470, 25.0406,
        29.6456, 34.2648, 36.0611, 36.6235, 38.4872,
        43.8256, 22.3193, 22.1987, 23.6978
    ],
    "经度": [
        116.4074, 117.2009, 114.5149, 112.5489, 111.7659,
        123.4327, 125.3245, 126.6617, 121.4737, 118.7626,
        120.1551, 117.2830, 119.3062, 115.8921, 117.0009,
        113.6254, 114.3055, 112.9388, 113.2644, 108.3275,
        110.1987, 106.9123, 104.0658, 106.6342, 102.7123,
        91.1175, 108.9542, 103.8343, 101.7782, 106.2309,
        87.6168, 114.1694, 113.5439, 120.9605
    ],
    "占比%": [
        7.8, 2.1, 4.5, 1.8, 1.2,
        2.5, 1.1, 1.0, 8.3, 14.8,
        12.7, 2.3, 4.3, 1.9, 9.3,
        5.2, 4.8, 3.1, 21.2, 1.7,
        0.8, 2.4, 6.3, 1.0, 1.5,
        0.1, 2.9, 0.7, 0.2, 0.3,
        0.9, 3.5, 0.5, 2.0
    ]
})
# 计算各省份具体营收
province_full_data["营收(亿元)"] = province_full_data["占比%"] / 100 * china_total

# 海外大区数据（保持原逻辑）
overseas_data = pd.DataFrame({
    "地区名称": ["东南亚", "欧美", "其他海外地区"],
    "营收(亿元)": [300, 350, year_detail["海外营收"] - 300 - 350],
    "纬度": [1.3521, 37.0902, 55.3781],
    "经度": [103.8198, -95.7129, -3.4360]
})

# ====================== 核心综合指数卡片展示 ======================
st.subheader("📈 当期八大核心分析指数")
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

with col1:
    st.metric("营业收入", f"¥{year_detail['营业收入']:,.2f}亿元")
with col2:
    st.metric("净利润率", f"{year_detail['净利润率%']}%")
with col3:
    st.metric("毛利率", f"{year_detail['毛利率%']}%")
with col4:
    st.metric("净资产收益率", f"{year_detail['净资产收益率%']}%")

with col5:
    st.metric("营收增速", f"{year_detail['营收同比增速%']}%")
with col6:
    st.metric("净利润增速", f"{year_detail['净利润同比增速%']}%")
with col7:
    st.metric("资产负债率", f"{year_detail['资产负债率%']}%")
with col8:
    st.metric("资产周转率", f"{year_detail['资产周转率']}")

st.divider()

# ====================== 第一部分：经营规模趋势图表 ======================
st.subheader("📉 营收与净利润历年变化趋势")
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=tencent_data["年份"], y=tencent_data["营业收入"], 
                         name="营业收入(亿元)", line=dict(color="#1E88E5", width=3), marker=dict(size=8)))
fig_trend.add_trace(go.Scatter(x=tencent_data["年份"], y=tencent_data["归母净利润"], 
                         name="归母净利润(亿元)", yaxis="y2", line=dict(color="#FFA000", width=3), marker=dict(size=8)))
fig_trend.update_layout(
    yaxis=dict(title="营业收入", title_font=dict(color="#1E88E5")),
    yaxis2=dict(title="归母净利润", title_font=dict(color="#FFA000"), overlaying="y", side="right"),
    title_text="整体经营规模走势",
    height=450
)
st.plotly_chart(fig_trend, use_container_width=True)

# ====================== 第二部分：业务板块可视化图表 ======================
st.subheader("📊 各业务板块营收分析")
c1, c2 = st.columns(2)

# 历年业务营收对比柱状图
business_trend = tencent_data.melt(
    id_vars="年份",
    value_vars=["增值服务营收","金融科技及企业服务营收","营销服务营收"],
    var_name="业务板块", value_name="营收"
)
with c1:
    fig_bar = px.bar(business_trend, x="年份", y="营收", color="业务板块", barmode="group",
                     title="2021-2024年板块营收对比",
                     color_discrete_map={"增值服务营收":"#E53935","金融科技及企业服务营收":"#43A047","营销服务营收":"#1E88E5"})
    st.plotly_chart(fig_bar, use_container_width=True)

# 当年业务占比饼图
business_now = pd.DataFrame({
    "业务板块":["增值服务","金融科技及企业服务","营销服务"],
    "营收":[year_detail["增值服务营收"],year_detail["金融科技及企业服务营收"],year_detail["营销服务营收"]]
})
with c2:
    fig_pie_biz = px.pie(business_now, values="营收", names="业务板块", title=f"{select_year}年业务营收占比")
    st.plotly_chart(fig_pie_biz, use_container_width=True)

# ====================== 第三部分：中国全省份+海外大区双地图 ======================
st.subheader("🌍 全球营收分布可视化（中国全省份+海外大区）")
map_col1, map_col2 = st.columns(2)

# 3.1 中国34省营收分布地图（经纬度散点图）
with map_col1:
    st.subheader("🇨🇳 中国34省营收分布地图")
    fig_china_scatter = px.scatter_geo(
        province_full_data,
        lat="纬度",
        lon="经度",
        size="营收(亿元)",
        color="营收(亿元)",
        hover_name="省份",
        hover_data={"营收(亿元)": ":,.2f", "占比%": ":,.1f"},
        projection="natural earth",
        title=f"{select_year}年腾讯中国全省份营收分布",
        color_continuous_scale=px.colors.sequential.Reds,
        size_max=60
    )
    # 聚焦中国区域
    fig_china_scatter.update_geos(
        scope="asia",
        center={"lat": 35, "lon": 105},
        projection_scale=5,
        showland=True,
        landcolor="rgb(240,240,240)",
        countrycolor="rgb(200,200,200)"
    )
    fig_china_scatter.update_layout(height=500, margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig_china_scatter, use_container_width=True)

# 3.2 海外大区散点图（保持原逻辑）
with map_col2:
    st.subheader("🌐 海外市场营收分布")
    fig_overseas = px.scatter_geo(
        overseas_data,
        lat="纬度",
        lon="经度",
        size="营收(亿元)",
        hover_name="地区名称",
        hover_data={"营收(亿元)": ":,.2f"},
        projection="natural earth",
        title=f"{select_year}年腾讯海外大区营收分布",
        color="地区名称",
        color_discrete_map={"东南亚": "#3498db", "欧美": "#e74c3c", "其他海外地区": "#2ecc71"},
        size_max=60
    )
    fig_overseas.update_layout(height=500, margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig_overseas, use_container_width=True)

# 3.3 省份营收TOP10排行榜
st.subheader("🏆 国内营收TOP10省份排行")
top10_province = province_full_data.sort_values("营收(亿元)", ascending=False).head(10)
fig_top10 = px.bar(
    top10_province,
    x="省份",
    y="营收(亿元)",
    color="占比%",
    title=f"{select_year}年国内营收最高的10个省份",
    color_continuous_scale=px.colors.sequential.Viridis
)
st.plotly_chart(fig_top10, use_container_width=True)

# ====================== 第四部分：新增财务指数专项图表 ======================
st.subheader("📊 多项财务指数走势对比")
fig_index = px.line(
    tencent_data, x="年份",
    y=["毛利率%","净利润率%","资产负债率%","净资产收益率%"],
    title="盈利、偿债能力指数历年波动",
    markers=True,
    color_discrete_map={
        "毛利率%":"#F44336",
        "净利润率%":"#2196F3",
        "资产负债率%":"#9C27B0",
        "净资产收益率%":"#4CAF50"
    }
)
st.plotly_chart(fig_index, use_container_width=True)

# 历年增长速度对比柱状图
st.subheader("🚀 营收&净利润增速变化")
grow_data = tencent_data[["年份","营收同比增速%","净利润同比增速%"]].melt(
    id_vars="年份", var_name="增长类型", value_name="增速(%)"
)
fig_grow = px.bar(grow_data, x="年份", y="增速(%)", color="增长类型", barmode="group",
                  title="年度业绩增长幅度对比")
st.plotly_chart(fig_grow, use_container_width=True)

# 资产负债结构堆叠图
st.subheader("🏦 资产与负债权益结构分析")
asset_data = pd.DataFrame({
    "年份":tencent_data["年份"],
    "负债":tencent_data["总负债"],
    "股东权益":tencent_data["股东权益"]
})
asset_stack = asset_data.melt(id_vars="年份", var_name="构成", value_name="金额")
fig_asset = px.area(asset_stack, x="年份", y="金额", color="构成",
                    title="企业资产结构历年变化")
fig_asset.update_traces(stackgroup='one')
st.plotly_chart(fig_asset, use_container_width=True)

# 财务能力雷达图
st.subheader("🎯 单年度财务综合能力雷达图")
radar_fig = go.Figure()
cate = ["盈利能力","收益水平","偿债安全","增长潜力","运营效率"]
vals = [
    year_detail["毛利率%"]/50*100,
    year_detail["净资产收益率%"]/30*100,
    100-year_detail["资产负债率%"],
    max(year_detail["营收同比增速%"],0),
    year_detail["资产周转率"]*100
]
radar_fig.add_trace(go.Scatterpolar(r=vals, theta=cate, fill="toself", name="综合能力评分"))
radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),title="财务五维能力评估")
st.plotly_chart(radar_fig, use_container_width=True)

# ====================== 原始数据表格 ======================
st.divider()
st.subheader("📋 完整原始财务数据表")
st.dataframe(tencent_data.round(2), use_container_width=True)

# 新增省份完整数据表格
st.subheader("📋 中国34省营收分布详细数据")
st.dataframe(province_full_data.round(2), use_container_width=True)

# ====================== 扫码访问二维码 ======================
st.divider()
st.subheader("📱 手机扫码直接访问应用")
def generate_qr_code(url):
    qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Image.open(buf)

local_url = "http://localhost:8501"
qr_pic = generate_qr_code(local_url)
st.image(qr_pic, caption="扫码进入腾讯财报分析看板", width=200)

# ====================== AI智能问答助手 ======================
st.divider()
st.subheader("🤖 财报智能咨询助手")
if "messages" not in st.session_state:
    st.session_state.messages = []

# 展示聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 问答交互
user_input = st.chat_input("可查询营收、利润、指数、业务、负债、省份分布等相关问题")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    ans = ""
    if "净利润" in user_input:
        ans = f"{select_year}年腾讯归母净利润为{year_detail['归母净利润']:.2f}亿元，净利润率{year_detail['净利润率%']}%。"
    elif "营收" in user_input:
        ans = f"{select_year}年营业收入{year_detail['营业收入']:.2f}亿元，同比增速{year_detail['营收同比增速%']}%。"
    elif "毛利率" in user_input or "盈利" in user_input:
        ans = f"当期毛利率{year_detail['毛利率%']}%，净资产收益率{year_detail['净资产收益率%']}%，盈利水平整体稳定。"
    elif "负债" in user_input or "资产" in user_input:
        ans = f"当期资产负债率{year_detail['资产负债率%']}%，负债规模合理，财务风险处于可控范围。"
    elif "业务板块" in user_input:
        ans = f"增值服务{year_detail['增值服务营收']:.2f}亿元，金融科技业务{year_detail['金融科技及企业服务营收']:.2f}亿元，营销服务{year_detail['营销服务营收']:.2f}亿元。"
    elif "增速" in user_input:
        ans = f"本年度营收增速{year_detail['营收同比增速%']}%，净利润增速{year_detail['净利润同比增速%']}%。"
    elif "省份" in user_input or "分布" in user_input:
        top_province = province_full_data.sort_values("营收(亿元)", ascending=False).iloc[0]
        ans = f"{select_year}年腾讯国内营收最高的省份是{top_province['省份']}，营收{top_province['营收(亿元)']:.2f}亿元，占国内总营收的{top_province['占比%']}%。TOP10省份贡献了约90%的国内营收。"
    elif "海外" in user_input:
        ans = f"{select_year}年腾讯海外营收{year_detail['海外营收']:.2f}亿元，主要来自东南亚（300亿元）和欧美（350亿元）市场。"
    else:
        ans = "你可以询问营收、净利润、毛利率、负债率、业务分布、增长速度、省份营收分布等财报相关问题~"
    
    st.session_state.messages.append({"role":"assistant","content":ans})
    with st.chat_message("assistant"):
        st.markdown(ans)







