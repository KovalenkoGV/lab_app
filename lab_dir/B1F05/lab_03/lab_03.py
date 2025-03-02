import os

import streamlit as st
# import numpy as np
import matplotlib.pyplot as plt

# from array import array
from lab_dir.B1F05.lab_03.stabilizerSDPV import StepDownPulseVoltageStabilizer


def on_change_init_param(stabilizer: StepDownPulseVoltageStabilizer):
    stabilizer.U_in = st.session_state.last_U_in
    stabilizer.U_out = st.session_state.last_U_out
    stabilizer.delta_U_out = st.session_state.last_delta_U_out
    stabilizer.I_n = st.session_state.last_I_n
    stabilizer.LIR = st.session_state.last_LIR
    stabilizer.F = st.session_state.last_F
    if st.session_state.auto_calc_param:
        stabilizer.calc_param()
    stabilizer.clear_arr()
    stabilizer.modeling()


def on_change_calc_param(stabilizer: StepDownPulseVoltageStabilizer):
    stabilizer.F = st.session_state.last_F
    stabilizer.L = st.session_state.last_L
    stabilizer.C = st.session_state.last_C
    stabilizer.R = st.session_state.last_R
    stabilizer.t_i = st.session_state.last_t_i
    stabilizer.t_p = st.session_state.last_t_p
    stabilizer.clear_arr()
    stabilizer.modeling()
    st.session_state.auto_calc_param = False


def on_change_auto_calc_param(stabilizer: StepDownPulseVoltageStabilizer):
    if st.session_state.auto_calc_param:
        stabilizer.calc_param()
        stabilizer.clear_arr()
        stabilizer.modeling()

def on_change_t_sim(stabilizer: StepDownPulseVoltageStabilizer):
    stabilizer.t_sim = st.session_state.last_t_sim
    stabilizer.clear_arr()
    stabilizer.modeling()


def on_change_integration_method(stabilizer: StepDownPulseVoltageStabilizer):
    stabilizer.integration_method = st.session_state.integration_method
    stabilizer.clear_arr()
    stabilizer.modeling()

def run_lab():
    info_file = os.path.join(os.getcwd(), 'lab_dir', 'B1F05', 'lab_03', 'about_lab_03.txt')
    image_file = os.path.join(os.getcwd(), 'lab_dir', 'B1F05', 'lab_03', 'lab_03.png')
    # st.write("Дисциплина:")

    with open(info_file, 'r', encoding='utf-8') as file:
        content = file.read()  # Читаем весь файл

    # Добавляем радио-кнопки на боковую панель
    option = st.sidebar.radio(
        "",
        ("Теоретические сведения", "Выполнение работы", "Контрольные вопросы")
    )

    # Проверяем выбранную опцию и выводим соответствующий контент
    if option == "Теоретические сведения":
        st.write(content)  # Выводим содержимое файла
    elif option == "Выполнение работы":
        # создаем экземпляр класса Выпрямитель и инициализируем его в сессионном состоянии
        if 'stabilizer' not in st.session_state:
            st.session_state.stabilizer = StepDownPulseVoltageStabilizer()

        stabilizer = st.session_state.stabilizer

        # Инициализация параметров в сессионном состоянии
        if (('last_U_in', 'last_U_out', 'last_delta_U_out', 'last_I_n', 'last_LIR', 'last_F', 'last_L',
             'last_C', 'last_R', 'last_t_i', 'last_t_p', 'last_t_start', 'last_t_stop', 'last_t_sim',
             'integration_method',)
                not in st.session_state):
            st.session_state.last_U_in = stabilizer.U_in
            st.session_state.last_U_out = stabilizer.U_out
            st.session_state.last_delta_U_out = stabilizer.delta_U_out
            st.session_state.last_I_n = stabilizer.I_n
            st.session_state.last_LIR = stabilizer.LIR
            st.session_state.last_F = stabilizer.F
            st.session_state.last_L = stabilizer.L
            st.session_state.last_C = stabilizer.C
            st.session_state.last_R = stabilizer.R
            st.session_state.last_t_i = stabilizer.t_i
            st.session_state.last_t_p = stabilizer.t_p
            st.session_state.last_t_start = stabilizer.t_start
            st.session_state.last_t_stop = stabilizer.t_stop
            st.session_state.last_t_sim = stabilizer.t_sim
            st.session_state.integration_method = stabilizer.integration_method

        if 'auto_calc_param' not in st.session_state:
            st.session_state.auto_calc_param = True

        if 'only_on_load' not in st.session_state:
            st.session_state.only_on_load = True

        # Ввод параметров схемы через боковую панель
        with st.sidebar.expander("Исходные номинальные характеристики схемы:", expanded=True):
            stabilizer.U_in = st.number_input("Входное напряжение (Uвх), В", key='last_U_in',
                                              on_change=on_change_init_param, args=(stabilizer,))
            if st.session_state.auto_calc_param:
                stabilizer.U_out = st.number_input("Выходное напряжение (Uвых), В", key='last_U_out',
                                                   min_value=stabilizer.min_value_U_out(),
                                                   max_value=stabilizer.max_value_U_out(),
                                                   on_change=on_change_init_param, args=(stabilizer,))
                stabilizer.delta_U_out = st.number_input("Размах пульсаций выходного напряжения, В",
                                                         key='last_delta_U_out',
                                                         min_value=0.01, max_value=1.0,
                                                         on_change=on_change_init_param,
                                                         args=(stabilizer,))
                stabilizer.I_n = st.number_input("Ток нагрузки (Iн), A", key='last_I_n',
                                                 min_value=0.01, max_value=100.0,
                                                 on_change=on_change_init_param, args=(stabilizer,))
                stabilizer.LIR = st.number_input("Коэффициент тока дросселя", key='last_LIR',
                                                 min_value=0.01, max_value=1.0,
                                                 on_change=on_change_init_param, args=(stabilizer,))
                stabilizer.F = st.number_input("Частота преобразования (fпр), Гц", key='last_F',
                                               min_value=1000.0, max_value=100000.0,
                                               on_change=on_change_init_param, args=(stabilizer,))

            st.checkbox("Автоматически рассчитывать параметры схемы", key='auto_calc_param',
                        on_change=on_change_auto_calc_param, args=(stabilizer,))

            if st.button("Вернуть значения по умолчанию"):
                stabilizer.set_default_param()
                stabilizer.calc_param()
                stabilizer.clear_arr()
                stabilizer.modeling()
                st.rerun()

        st.sidebar.selectbox("Метод интегрирования", stabilizer.integration_methods,
                             key='integration_method', on_change=on_change_integration_method, args=(stabilizer,))

        with st.sidebar.expander("Расчетные параметры схемы:", expanded=False):
            st.write("Параметры элементов схемы")
            stabilizer.L = st.number_input("Индуктивность (L), Гн", key='last_L', format="%0.6f",
                                           on_change=on_change_calc_param, args=(stabilizer,))
            stabilizer.C = st.number_input("Емкость (C), Ф", key='last_C', format="%0.9f",
                                           on_change=on_change_calc_param, args=(stabilizer,))
            stabilizer.R = st.number_input("Сопротивление нагрузки (R), Ом", key='last_R', format="%0.2f",
                                           on_change=on_change_calc_param, args=(stabilizer,))

            with st.container():
                st.write("Параметры управляющих импульсов")
                # st.checkbox("Не изменять период", key='auto_calc_param',
                #            on_change=on_change_auto_calc_param, args=(stabilizer,))
                stabilizer.t_i = st.number_input("Время импульса (t_i), с", key='last_t_i', format="%0.6f",
                                                 on_change=on_change_calc_param, args=(stabilizer,))
                stabilizer.t_p = st.number_input("Время интервала (t_p), с", key='last_t_p', format="%0.6f",
                                                 on_change=on_change_calc_param, args=(stabilizer,))

            if st.button("Пересчитать по исходным характеристикам"):
                stabilizer.calc_param()
                stabilizer.clear_arr()
                stabilizer.modeling()
                st.rerun()

        stabilizer.t_sim = st.sidebar.number_input("Время моделирования (t_sim), с", key='last_t_sim', format="%0.6f",
                                                   on_change=on_change_t_sim, args=(stabilizer,))

        st.header("Исследование импульсного стабилизатора напряжения понижающего типа")
        st.image(image_file)

        st.subheader("Результаты моделирования работы схемы")

        # График тока через катушку
        st.markdown("**Ток через катушку индуктивности**")
        fig1, ax1 = plt.subplots(figsize=(12, 3))

        ax1.plot(stabilizer.t, stabilizer.I_L_arr, label='Ток через катушку (I_L)', color='blue')
        # if not st.session_state.only_on_load:
        #    ax1.plot(stabilizer.t, stabilizer.I_in_arr, label='Входной ток (I_in)', color='green', linestyle='--')
        #    ax1.plot(stabilizer.t, stabilizer.I_D_arr, label='Ток через диод (I_D)', color='red', linestyle='-.')

        ax1.set_xlabel('Время (с)')
        ax1.set_ylabel('Ток (А)')
        # ax1.set_title('Ток через катушку индуктивности')
        # Добавляем сетку
        ax1.grid(True)
        ax1.legend()
        # Отображаем график
        st.pyplot(fig1)

        # График напряжения на нагрузке
        st.markdown("**Напряжение на нагрузке**")
        fig3, ax3 = plt.subplots(figsize=(12, 4))

        ax3.plot(stabilizer.t, stabilizer.U_C_arr, label='Напряжение на нагрузке (U_C)', color='blue')
        if not st.session_state.only_on_load:
            ax3.plot(stabilizer.t, stabilizer.U_D_arr, label='Напряжение диоде U_VD', color='red', linestyle='-.')

        ax3.set_xlabel('Время (с)')
        ax3.set_ylabel('Напряжение (В)')
        #ax3.set_title('Напряжение на нагрузке')
        # Добавляем сетку
        ax3.grid(True)
        ax3.legend()
        # Отображаем график
        st.pyplot(fig3)

        st.checkbox("Только значения на нагрузке", key='only_on_load')

        st.write(f"метод интегрирования: {stabilizer.integration_method}")

        delta_I_L, delta_U_out, f_c = stabilizer.check_ripples()
        st.write(f"Пульсации тока через индуктивность: {delta_I_L:.6f} А")
        st.write(f"Пульсации напряжения на нагрузке: {delta_U_out:.6f} В")
        st.write(f"Частота среза LC-фильтра: {f_c:.6f} Гц")

        # st.write(f"Время завершения переходных процессов: {stabilizer.get_settling_time():.6f} с")
        # st.write(f"Время завершения переходных процессов: {stabilizer.get_settling_time_1():.6f} с")
        # st.write(f"Время завершения переходных процессов: {stabilizer.get_settling_time_2():.6f} с")
        # st.write(f"частота колебаний: {stabilizer.get_settling_time_3():.6f} с")

        with st.expander("Нажмите, чтобы просмотреть фрагмент графиков в заданном интервале времени"):
            count_T = st.slider("Количество отображаемых тактов:", 1, 10, 3)
            time_start = st.slider("Начальное время:",
                                   min_value=0.0,
                                   max_value=stabilizer.t_sim - (stabilizer.T * count_T),
                                   value=stabilizer.t_sim - (stabilizer.T * count_T),
                                   step=stabilizer.T,
                                   format="%0.6f")
            #st.markdown("**Данный функционал находится в разработке**")

    else:
        st.title("Контрольные вопросы")
