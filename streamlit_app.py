# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ STREAMLIT
# ============================================================

st.title("⚓ Динамический Планировщик Морской Перевалки")
st.markdown("---")

# БОКОВАЯ ПАНЕЛЬ - ПАРАМЕТРЫ
with st.sidebar:
    st.header("Параметры Симуляции")
    
    st.subheader("Речной Флот")
    river_start = st.date_input(
        "Начало речных рейсов",
        value=datetime(2024, 4, 10),
        key="river_start"
    )
    river_ships = st.slider(
        "Количество речных судов",
        min_value=1,
        max_value=10,
        value=3,
        key="river_ships"
    )
    river_interval = st.slider(
        "Интервал между судами (дни)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        key="river_interval"
    )
    
    st.subheader("Морской Флот")
    sea_start = st.date_input(
        "Начало морских рейсов",
        value=datetime(2024, 11, 20),
        key="sea_start"
    )
    sea_ships = st.slider(
        "Количество морских судов",
        min_value=1,
        max_value=10,
        value=4,
        key="sea_ships"
    )
    sea_interval = st.slider(
        "Интервал между судами (дни)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        key="sea_interval"
    )
    
    st.subheader("Маршруты")
    river_duration = st.slider(
        "Речное плечо A→B (дни в пути)",
        min_value=1,
        max_value=20,
        value=5,
        key="river_duration"
    )
    river_op_time = st.slider(
        "Операция в портe B (дни)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        key="river_op"
    )
    
    sea_duration = st.slider(
        "Морское плечо B→C (дни в пути)",
        min_value=1,
        max_value=30,
        value=10,
        key="sea_duration"
    )
    sea_op_time = st.slider(
        "Операция в порту C (дни)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
        key="sea_op"
    )
    
    st.subheader("Ёмкости")
    river_capacity = st.slider(
        "Грузоподъёмность речного судна (единицы)",
        min_value=10,
        max_value=100,
        value=30,
        step=5,
        key="river_cap"
    )
    sea_capacity = st.slider(
        "Грузоподъёмность морского судна (единицы)",
        min_value=10,
        max_value=100,
        value=25,
        step=5,
        key="sea_cap"
    )
    tank_capacity = st.slider(
        "Максимум буферного танка (единицы)",
        min_value=50,
        max_value=500,
        value=100,
        step=10,
        key="tank_cap"
    )


# СОЗДАНИЕ МАРШРУТОВ И РАСПИСАНИЙ
leg_river = Leg(
    name="Речное_A-B",
    port_from="PortA",
    port_to="PortB",
    duration_days=river_duration,
    operation_days=river_op_time
)

leg_sea = Leg(
    name="Морское_B-C",
    port_from="PortB",
    port_to="PortC",
    duration_days=sea_duration,
    operation_days=sea_op_time
)

route_river = Route(
    name="Речной_маршрут",
    legs=[leg_river],
    ship_capacity=river_capacity
)

route_sea = Route(
    name="Морской_маршрут",
    legs=[leg_sea],
    ship_capacity=sea_capacity
)

river_scheduler = VoyageScheduler(
    route=route_river,
    start_date=datetime.combine(river_start, datetime.min.time()),
    num_ships=river_ships,
    interval_days=river_interval
)

sea_scheduler = VoyageScheduler(
    route=route_sea,
    start_date=datetime.combine(sea_start, datetime.min.time()),
    num_ships=sea_ships,
    interval_days=sea_interval
)

tank_sim = TankSimulation(tank_capacity, river_scheduler, sea_scheduler)

# Создаём графики
fig_gantt = create_gantt_chart(river_scheduler, sea_scheduler)
fig_tank = create_tank_chart(tank_sim)
fig_gantt_detail = create_gantt_detailed(river_scheduler, sea_scheduler)

# КНОПКИ ЭКСПОРТА
st.markdown("### Экспорт Данных")

col1, col2, col3 = st.columns(3)

with col1:
    # Excel экспорт
    excel_file = export_to_excel(river_scheduler, sea_scheduler, tank_sim)
    wb = style_excel(excel_file)
    
    excel_output = BytesIO()
    wb.save(excel_output)
    excel_output.seek(0)
    
    st.download_button(
        label="Скачать Excel",
        data=excel_output,
        file_name=f"fleet_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col2:
    # PDF экспорт
    pdf_file = export_to_pdf(river_scheduler, sea_scheduler, tank_sim, 
                            fig_gantt, fig_tank, fig_gantt_detail)
    
    st.download_button(
        label="Скачать PDF",
        data=pdf_file,
        file_name=f"fleet_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col3:
    # CSV экспорт
    csv_data = river_scheduler.get_schedule_df().to_csv(index=False)
    st.download_button(
        label="Скачать CSV",
        data=csv_data,
        file_name=f"fleet_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")

# ОСНОВНЫЕ ВКЛАДКИ
tabs = st.tabs([
    "📊 Диаграмма Ганта",
    "📈 Динамика Танка",
    "⚙️ Детальное Расписание",
    "📋 Таблицы"
])

with tabs[0]:
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего судов", river_ships + sea_ships)
    with col2:
        total_days = max([(v['arrival_final'] - river_scheduler.voyages[0]['itinerary'][0]['departure']).days 
                         for v in river_scheduler.voyages + sea_scheduler.voyages])
        st.metric("Длительность цикла", f"{total_days} дней")
    with col3:
        st.metric("Танк max/min", f"{max([l['tank_level'] for l in tank_sim.tank_log])}/{min([l['tank_level'] for l in tank_sim.tank_log])}")

with tabs[1]:
    st.plotly_chart(fig_tank, use_container_width=True)
    
    df_tank = tank_sim.get_log_df()
    st.dataframe(df_tank, use_container_width=True)

with tabs[2]:
    st.plotly_chart(fig_gantt_detail, use_container_width=True)

with tabs[3]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Речной Флот")
        st.dataframe(river_scheduler.get_schedule_df(), use_container_width=True)
    
    with col2:
        st.subheader("Морской Флот")
        st.dataframe(sea_scheduler.get_schedule_df(), use_container_width=True)

st.markdown("---")
st.markdown("**Разработано для оптимизации морских перевозок** ⚓")
```

Установи зависимости:

```bash
pip install streamlit plotly pandas numpy openpyxl reportlab kaleido