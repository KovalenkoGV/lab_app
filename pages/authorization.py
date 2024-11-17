import streamlit as st


def styled_text(text):
    st.markdown(
        f'<p style="background-color: LightBlue; padding: 10px; border-radius: 5px; color: black;">{text}</p>',
        unsafe_allow_html=True
    )


st.title("Страница авторизации")


# Создание боковой панели
# st.sidebar.title("Страница авторизиции")

# Функция проеряет полноту введенных личных данных 
def verification_name(surname, name, patronymic, group):
    if all([surname, name, patronymic, group]):
        return True
    else:
        return False


# Авторизация пользователя в системе
def autorisation_on(surname, name, patronymic, group):
    if verification_name(surname, name, patronymic, group):
        st.session_state.session_state['surname'] = surname
        st.session_state.session_state['name'] = name
        st.session_state.session_state['patronymic'] = patronymic
        st.session_state.session_state['group'] = group

        st.session_state.logged_in = True
        return True
    else:
        return False


# Выход пользователя из учетной записи
def autorisation_off():
    st.session_state.session_state['surname'] = ''
    st.session_state.session_state['name'] = ''
    st.session_state.session_state['patronymic'] = ''
    st.session_state.session_state['group'] = ''

    st.session_state.logged_in = False


# Проверка состояния авторизации
if not st.session_state.logged_in:

    # Ввод личных данных
    col1, col2 = st.columns([2, 2])
    with col1:
        surname = st.text_input("Фамилия:")
        name = st.text_input("Имя:")
        patronymic = st.text_input("Отчество:")
    with col2:
        group = st.text_input("Группа:")

    # Добавление кнопки авторизации
    if st.sidebar.button("Авторизоваться"):
        if autorisation_on(surname, name, patronymic, group):
            st.rerun()
else:
    # Выод личных данных
    col1, col2 = st.columns([2, 2])
    with col1:
        st.write("Фамилия:")
        styled_text(st.session_state.session_state['surname'])
        st.write("Имя:")
        styled_text(st.session_state.session_state['name'])
        st.write("Отчество:")
        styled_text(st.session_state.session_state['patronymic'])
    with col2:
        st.write("Группа:")
        styled_text(st.session_state.session_state['group'])
    st.write("Авторизация выполнена")

    # Добавление кнопки выхода из учетной записи 
    if st.sidebar.button("Выйти из учетной записи"):
        autorisation_off()
        st.rerun()

with st.form("signin_form", border=True):
    st.subheader("Sign in")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.form_submit_button("Sign in", type='primary'):
        pass
