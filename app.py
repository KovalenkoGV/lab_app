import os

import streamlit as st

if "session_state" not in st.session_state:
    st.session_state.session_state = {'surname': '', 'name': '', 'patronymic': '', 'group': ''}

# Инициализация состояния авторизации
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Инициализация кода дисциплины и имени ЛР
if 'current_lab_info' not in st.session_state:
    st.session_state.current_lab_info = []

# Инициализация названия лабораторной работы
if 'current_lab_name' not in st.session_state:
    st.session_state.current_lab_name = ''

# Инициализация перехода к лабораторной работе
if 'go_to_current_lab' not in st.session_state:
    st.session_state.go_to_current_lab = False

# sep = os.sep
pages_dir = f'pages{os.sep}'

# Инициализация пустого списка страниц
pages = {}

if st.session_state.logged_in:
    pages.update({
        "Ваш аккаунт": [
            st.Page(f'{pages_dir}authorization.py', title=st.session_state.session_state['name']),
        ],
    })

else:
    pages.update({
        "Ваш аккаунт": [
            st.Page(f'{pages_dir}authorization.py', title="Авторизация"),
        ],
    })

if st.session_state.current_lab_info:
    current_lab_name = st.session_state.current_lab_info[1]
    pages.update({
        "Лабораторные работы": [
            st.Page(f'{pages_dir}lab_select.py', title="Показать список"),
        ],

        "Текущая лабораторная работа": [
            st.Page(f'{pages_dir}lab_visual.py', title=current_lab_name),
        ],
    })
else:
    pages.update({
        "Лабораторные работы": [
            st.Page(f'{pages_dir}lab_select.py', title="Показать список"),
        ],
    })

pg = st.navigation(pages)
pg.run()

# Проверяем была ли нажата кнопка "Приступить к работе"
# и если Да, то переходим на страницу лабораторной работы
if st.session_state.go_to_current_lab:
    st.session_state.go_to_current_lab = False
    st.switch_page(f'{pages_dir}lab_visual.py')
