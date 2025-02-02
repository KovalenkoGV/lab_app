import os

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from array import array


class StepDownPulseVoltageStabilizer:
    """ Класс описывающий работу схемы понижающего импульсного стабилизатора """

    # Исходные параметры схемы 
    U_in = 12.0  # Входное напряжение (В)
    U_out = 9.0  # Выходное напряжение (В)
    delta_U_out = 0.05  # Размах пульсаций выходного напряжения
    I_n = 1  # Ток нагрузки (А)

    # Расчетные параметры
    L = 0.0015  # Индуктивность (Гн)
    C = 7.5e-05  # Емкость (Ф)
    R = 5  # Сопротивление нагрузки (Ом)
    t_i = 8.3e-05  # Время импульса
    t_p = 1.7e-05  # Время интервала
    T = t_i + t_p  # Период переключения (с)

    t_sim = 0.002  # Время моделирования (с)
    t = array('f')  # Временная ось

    # Начальные условия
    I_L = 0.0  # Начальный ток через катушку (А)
    U_C = 0.0  # Начальное напряжение на конденсаторе (В)
    U_CE = U_in  # Начальное напряжение коллектор-эмиттер (В)
    U_D = 0.0  # Начальное напряжение на диоде (В)
    I_in = 0.0  # Начальный входной ток (А)
    I_D = 0.0  # Начальный ток через диод (А)

    # Массивы для хранения результатов
    I_L_arr = []
    U_C_arr = []
    U_CE_arr = []
    U_D_arr = []
    I_in_arr = []
    I_D_arr = []

    def __init__(self):
        self.calc_param()

    def clear_arr(self):
        """ Сброс начальных условий переходных процессов схемы 
        и очистка массивов хранения результатов """

        self.I_L = 0.0
        self.U_C = 0.0
        self.U_CE = self.U_in
        self.U_D = 0.0
        self.I_in = 0.0
        self.I_D = 0.0

        self.I_L_arr.clear()
        self.U_C_arr.clear()
        self.U_CE_arr.clear()
        self.U_D_arr.clear()
        self.I_in_arr.clear()
        self.I_D_arr.clear()
        self.t = array('f')

    def set_default_param(self):
        # Исходные параметры схемы
        self.U_in = 12.0  # Входное напряжение (В)
        self.U_out = 9.0  # Выходное напряжение (В)
        self.delta_U_out = 0.05  # Размах пульсаций выходного напряжения
        self.I_n = 1  # Ток нагрузки (А)

        # Расчетные параметры
        self.L = 0.0015  # Индуктивность (Гн)
        self.C = 7.5e-05  # Емкость (Ф)
        self.R = 5  # Сопротивление нагрузки (Ом)
        self.t_i = 8.3e-05  # Время импульса
        self.t_p = 1.7e-05  # Время интервала
        self.T = self.t_i + self.t_p  # Период переключения (с)

        self.t_sim = 0.002  # Время моделирования (с)

    def calc_param(self):
        """ Расчет параметров схемы понижающего импульсного стабилизатора """

        # Расчет временных параметров
        dt = self.T / 1000  # Шаг по времени (с)
        t = np.arange(0, self.t_sim, dt)  # Временная ось

        self.t = array('f', t)

        # Моделирование переходных процессов в схеме
        for i in range(len(t)):
            # Определение состояния ключа (включен/выключен)
            if (t[i] % self.T) < self.t_i:
                # Ключ включен
                dI_L_dt = (self.U_in - self.U_C) / self.L
                dU_C_dt = (self.I_L - self.U_C / self.R) / self.C
                self.U_CE = 0.0  # Напряжение коллектор-эмиттер близко к нулю
                self.U_D = self.U_in  # Напряжение на диоде равно входному напряжению
                self.I_in = self.I_L  # Входной ток равен току через катушку
                self.I_D = 0.0  # Ток через диод равен нулю
            else:
                # Ключ выключен
                dI_L_dt = -self.U_C / self.L
                dU_C_dt = (self.I_L - self.U_C / self.R) / self.C
                self.U_CE = self.U_in  # Напряжение коллектор-эмиттер равно входному напряжению
                self.U_D = 0.0  # Напряжение на диоде близко к нулю
                self.I_in = 0.0  # Входной ток равен нулю
                self.I_D = self.I_L  # Ток через диод равен току через катушку

            # Интегрирование (метод Эйлера)
            self.I_L += dI_L_dt * dt
            self.U_C += dU_C_dt * dt

            # Сохранение результатов
            self.I_L_arr.append(self.I_L)
            self.U_C_arr.append(self.U_C)
            self.U_CE_arr.append(self.U_CE)
            self.U_D_arr.append(self.U_D)
            self.I_in_arr.append(self.I_in)
            self.I_D_arr.append(self.I_D)


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

        # Ввод параметров схемы через боковую панель
        st.sidebar.header("Параметры схемы")
        stabilizer.U_in = st.sidebar.number_input("Входное напряжение (Uin), В", value=stabilizer.U_in)
        stabilizer.U_out = st.sidebar.number_input("Выходное напряжение (Uout), В", value=stabilizer.U_out)
        stabilizer.L = st.sidebar.number_input("Индуктивность (L), Гн", value=stabilizer.L, format="%0.6f")
        stabilizer.C = st.sidebar.number_input("Емкость (C), Ф", value=stabilizer.C, format="%0.6f")
        stabilizer.R = st.sidebar.number_input("Сопротивление нагрузки (R), Ом", value=stabilizer.R)
        stabilizer.t_i = st.sidebar.number_input("Время импульса (t_i), с", value=stabilizer.t_i,
                                                 format="%0.6f")  # Время импульса
        stabilizer.t_p = st.sidebar.number_input("Время интервала (t_p), с", value=stabilizer.t_p,
                                                 format="%0.6f")  # Время интервала
        stabilizer.t_sim = st.sidebar.number_input("Время моделирования (t_sim), с", value=stabilizer.t_sim,
                                                   format="%0.6f")

        stabilizer.clear_arr()
        stabilizer.calc_param()

        st.header("Исследование импульсного стабилизатора напряжения понижающего типа")
        st.image(image_file)

        # Добавляем слайдер с сопротивлением нагрузки
        # r_min, r_max, r_nom = stabilizer.calc_min_max_nom_Rload(0.1, 3.00)
        # r_load = st.slider("Сопротивление нагрузки Rн, Ом", r_min, r_max, r_nom)

        # вычисляем и выводим значения тока и напряжения для заданной нагрузки
        # i_u_load = np.array([stabilizer.calc_u_i_on_load(r_load)], dtype=stabilizer.dtype)

        st.subheader("Результаты измерений")

        # Построение графиков
        st.markdown("**Ток через катушку, входной ток и ток через диод**")

        # График тока через катушку
        fig1, ax1 = plt.subplots(figsize=(12, 3))

        ax1.plot(stabilizer.t, stabilizer.I_L_arr, label='Ток через катушку (I_L)', color='blue')
        ax1.plot(stabilizer.t, stabilizer.I_in_arr, label='Входной ток (I_in)', color='green', linestyle='--')
        ax1.plot(stabilizer.t, stabilizer.I_D_arr, label='Ток через диод (I_D)', color='red', linestyle='-.')

        ax1.set_ylabel('Время (с)')
        ax1.set_xlabel('Ток (А)')
        ax1.set_title('Ток через катушку индуктивности')
        # Добавляем сетку
        ax1.grid(True)
        ax1.legend()
        # Отображаем график
        st.pyplot(fig1)

        # График напряжения на нагрузке
        st.markdown("**Напряжение на нагрузке, напряжение коллектор-эмиттер и напряжение на диоде**")
        fig2, ax2 = plt.subplots(figsize=(12, 4))

        ax2.plot(stabilizer.t, stabilizer.U_C_arr, label='Напряжение на нагрузке (U_C)', color='blue')
        ax2.plot(stabilizer.t, stabilizer.U_CE_arr, label='Напряжение коллектор-эмиттер (U_CE)', color='green',
                 linestyle='--')
        # ax2.plot(stabilizer.t, stabilizer.U_D_arr, label='Напряжение на диоде (V_D)', color='red', linestyle='-.')

        ax2.set_ylabel('Время (с)')
        ax2.set_xlabel('Напряжение (В)')
        ax2.set_title('Напряжение на нагрузке')
        # Добавляем сетку
        ax2.grid(True)
        ax2.legend()
        # Отображаем график
        st.pyplot(fig2)

        # if st.button("Вернуть параметры по умолчанию"):
        #    stabilizer.set_default_param()
        #    stabilizer.clear_arr()  
        #    stabilizer.calc_param()
        #    st.rerun()
    else:
        st.title("Контрольные вопросы")
