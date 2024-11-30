from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import TeleBot
from telebot.handler_backends import State, StatesGroup
from telebot.custom_filters import StateFilter

class KeyboardsState(StatesGroup):
    button_count = State()
    keyboard_text_and_callback = State()
    send_keyboard = State()

bot = TeleBot("7685230401:AAFWV20raacAwgL_Z71lI8C_21ZzAUgGUJk")

def gen_markup(buttons_info):
    keyboard = InlineKeyboardMarkup()

    for text_keyboard, callback_keyboard in buttons_info.items():
        button = InlineKeyboardButton(text=text_keyboard, callback_data=callback_keyboard)
        keyboard.add(button)
        return keyboard


@bot.message_handler(commands=["create_markup"])
def handle_start_message(message):
    bot.set_state(message.from_user.id, KeyboardsState.button_count, message.chat.id)
    bot.send_message(message.from_user.id, "Привет, я помогу тебе сформировать инлайн клавиатуру\n"
                                           "Введи количество кнопок для клавиатуры")

@bot.message_handler(state=KeyboardsState.button_count)
def handle_buttons_count(message):
    if message.text.isdigit():
        bot.set_state(message.from_user.id, KeyboardsState.keyboard_text_and_callback, message.chat.id)


        with bot.retrieve_data(message.from_user.id) as data:
            data["button_count"] = int(message.text)
            data["buttons"] = {}
            data["temp_keyboard_data"] = []
        bot.send_message(message.from_user.id, "Отлично! Теперь введи текст для кнопки")
    else:
        bot.send_message(message.from_user.id, "Количество кнопок должно быть указано числом!")

@bot.message_handler(state=KeyboardsState.keyboard_text_and_callback)
def handle_keyboard_text_and_callback(message):
    with bot.retrieve_data(message.from_user.id) as data:
        temp_keyboard_data = data["temp_keyboard_data"]

        if not temp_keyboard_data:
            temp_keyboard_data.append(message.text)
            bot.send_message(message.from_user.id, f"Укажи callback для кнопки {message.text}")
        elif len(temp_keyboard_data) == 1:
            temp_keyboard_data.append(message.text)

            key, value = temp_keyboard_data
            data["buttons"][key] = value
            temp_keyboard_data.clear()
            data["button_count"] -= 1


            if data["button_count"]:
                bot.send_message(message.from_user.id, "Данные  сохранены! Введи текст для следующей кнопки")
            else:
                bot.set_state(message.from_user.id, KeyboardsState.send_keyboard)
                bot.send_message(message.from_user.id, "Кнопки, которые ты хотел создать",
                      reply_markup=gen_markup(data["buttons"]))

@bot.callback_query_handler(func=None, state=KeyboardsState.send_keyboard)
def handle_buttons(callback_query):
    with bot.retrieve_data(callback_query.from_user.id) as data:
        pressed_button_name = None
        for key, value in data["buttons"].items():
            if callback_query.data == value:
                bot.answer_callback_query(callback_query.id,
                                          f"Поймал нажатие на кнопку {key}",
                                          show_alert=True)
                pressed_button_name = key

        data["buttons"].pop(pressed_button_name, None)
        bot.edit_message_reply_markup(callback_query.from_user.id,
                                      callback_query.message.message.id,
                                      reply_markup=gen_markup(data["buttons"]))
    if not data["buttons"]:
        bot.send_message(callback_query.from_user.id, "Все кнопки были нажаты!")
        bot.delete_state(callback_query.from_user.id)

if __name__ == "__main__":
    bot.add_custom_filter(StateFilter(bot))
    bot.infinity_polling()


