import os

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


class SinglePhaseBridgeRectifier:
    """ Класс описывающий работу однофазной мостовой схемы выпрямителя """
    # заданные параметры
    U_in = 220  # Напряжение первичной обмотки трансформатора, В
    f = 50  # частота питающей сети, Гц
    E0 = 12  # Выпрямленное напряжение, В
    I0 = 10  # Среднее значение выпрямленного тока, А
    dEv = 0.7  # Падение напряжения на вентиле (диоде), В
    i_diode_max = 10  # Допустимый ток через диод, А
    u_reverse_diode_max = 50  # Допустимое обратное напряжение на диоде, В

    # расчетные параметры
    E0_h = 0  # выпрямленное напряжение при холостом ходе
    Rv = 0  # внутреннее сопротивление выпрямителя
    i_u_array = np.array([])  # список расчетных напряжений и токов при изменяющейся нагрузке

    # описание шаблона типа данных таблицы нагрузочной характеристики
    dtype = np.dtype([
        ('Iн, A', 'float16'),
        ('Uн, V', 'float16')
    ])

    def __init__(self):
        self.calc_param()
        self.i_u_array = np.array([(0.0, self.E0_h)], dtype=self.dtype)

    def calc_param(self):
        # Расчет параметров мостовой схемы выпрямителя без фильтра

        # Определение габаритной мощности трансформатора:
        P_gab = 1.23 * 1.1 * self.E0 * self.I0
        # из табл. 1.2 определяем максимальную
        # индукцию в сердечнике трансформатора
        B_m = 1.55

        # Находим сопротивление обмоток трансформатора, Ом
        s = 2  # для стержневого трансформатора
        r_tr = (5.2 * (self.E0 / (self.I0 * self.f * B_m)) *
                pow(s * self.f * B_m / (self.E0 * self.I0), 1 / 4))

        # Определяем индуктивность рассеяния обмоток,
        # приведенную к фазе вторичной обмотки, гн
        Ls = (6.4e-3 * s * (self.E0 / (self.I0 * self.f * B_m)) *
              1 / pow(2 * self.f * B_m / (self.E0 * self.I0), 1 / 4))

        # Находим падение напряжения на активном сопротивлении трансформатора
        dEr = self.I0 * r_tr

        # Находим падение напряжения на реактивном сопротивлении трансформатора
        dE_h = 2 * self.I0 * self.f * Ls

        # Определяем падение напряжения на вентилях в схеме
        dEv_sh = 2 * self.dEv

        # Находим выпрямленное напряжение при холостом ходе
        self.E0_h = self.E0 + dEr + dE_h + dEv_sh

        # Расчет параметров мостовой схемы выпрямителя без фильтра
        I0v = self.I0 / 2
        # значение обратного напряжения на вентиле
        U_obr = 1.57 * self.E0_h

        # Вычисляем ЭДС фазы вторичной обмотки
        U2h = 1.11 * self.E0_h

        # Определяем эффективное значение тока в фазе вторичной обмотки
        I2 = 1.11 * self.I0

        # Определяем внутреннее сопротивление выпрямителя
        dE0 = self.E0_h - self.E0
        self.Rv = dE0 / self.I0

    def calc_u_i_on_load(self, r_load):
        i_load = self.E0_h / (self.Rv + r_load)
        u_load = self.E0_h - i_load * self.Rv
        i_u_load = (i_load, u_load)
        return i_u_load

    def calc_min_max_nom_Rload(self, k_Rmin: float, k_Rmax: float):
        # k_Rmin < 1 - коэффициент для расчета минимального значения Rн
        # k_Rmax > 1 - коэффициент для расчета максимального значения Rн
        Rnom = self.E0 / self.I0
        Rmin = Rnom * k_Rmin
        Rmax = Rnom * k_Rmax
        return Rmin, Rmax, Rnom

    def check_overcurrent(self, i_load: float):
        """ Проверка перегрузки по допустимому току через диод"""
        if i_load / 2 > self.i_diode_max:
            return False
        else:
            return True

def run_lab():
    info_file = os.path.join(os.getcwd(), 'lab_dir', 'B1F05', 'lab_02', 'about_lab_02.txt')
    image_file = os.path.join(os.getcwd(), 'lab_dir', 'B1F05', 'lab_02', 'lab_02.png')
    # st.write("Дисциплина:")

    with open(info_file, 'r', encoding='utf-8') as file:
        content = file.read()  # Читаем весь файл

    # Добавляем радио-кнопки на боковую панель
    option = st.sidebar.radio(
        "",
        ("Теоретические сведения", "Исследование нагрузочной характеристики", "Контрольные вопросы")
    )

    # Проверяем выбранную опцию и выводим соответствующий контент
    if option == "Теоретические сведения":
        st.write(content)  # Выводим содержимое файла
    elif option == "Исследование нагрузочной характеристики":
        # создаем экземпляр класса Выпрямитель и инициализируем его в сессионном состоянии
        if 'rectifier' not in st.session_state:
            st.session_state.rectifier = SinglePhaseBridgeRectifier()

        rectifier = st.session_state.rectifier

        st.header("Исследование нагрузочной характеристики мостовой схемы выпрямителя без фильтра")
        st.image(image_file)

        # Добавляем слайдер с сопротивлением нагрузки
        r_min, r_max, r_nom = rectifier.calc_min_max_nom_Rload(0.1, 3.00)
        r_load = st.slider("Сопротивление нагрузки Rн, Ом", r_min, r_max, r_nom)
        # вычисляем и выводим значения тока и напряжения для заданной нагрузки
        i_u_load = np.array([rectifier.calc_u_i_on_load(r_load)], dtype=rectifier.dtype)

        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(i_u_load)
        with col2:
            if rectifier.check_overcurrent(float(i_u_load['Iн, A'])):
                if st.button("Добавить в таблицу измерений"):
                    rectifier.i_u_array = np.append(rectifier.i_u_array, i_u_load, axis=0)
            else:
                st.write("Превышен допустимый ток через диод!")
                st.write("Увеличьте сопротивление нагрузки!")

        st.subheader("Результаты измерений")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(rectifier.i_u_array)
        with col2:
            # if st.button('Построить график'):
                # Строим график
            fig, ax = plt.subplots()
            ax.plot(rectifier.i_u_array['Iн, A'], rectifier.i_u_array['Uн, V'], marker='o')
            ax.set_ylabel('Напряжение на нагрузке')
            ax.set_xlabel('Ток нагрузки')
            ax.set_title('Нагрузочная характеристика')
            # Добавляем сетку
            ax.grid(True)
            # Отображаем график
            st.pyplot(fig)
        if st.button("Очистить данные измерений"):
            rectifier.i_u_array = np.array([(0.0, rectifier.E0_h)], dtype=rectifier.dtype)
            st.rerun()
    else:
        st.title("Контрольные вопросы")
