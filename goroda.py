import random
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = '8744968969:AAGeRbm7U4_07IzW6MMS_6jMQI4XtVOVNw8'
bot = telebot.TeleBot(TOKEN)


def load_cities_from_txt():
    with open('cities.txt', 'r', encoding='Windows-1251') as file:
            cities = [line.strip() for line in file if line.strip()]

            if not cities:
                print("❌ Файл cities.txt пуст!")
                return get_default_cities()

            print(f"✅ Загружено {len(cities)} городов из cities.txt")
            return [city.upper() for city in cities]


ALL_CITIES = load_cities_from_txt()
games = {}


def get_last_letter(city):
    city = city.strip().upper()
    excluded = ['Ь', 'Ъ', 'Ы', 'Й']

    for i in range(len(city) - 1, -1, -1):
        if city[i] not in excluded:
            return city[i]



def find_city_by_letter(letter, used_cities):
    letter = letter.upper()
    available = []

    for city in ALL_CITIES:
        if city[0] == letter and city not in used_cities:
            available.append(city)

    if available:
        return random.choice(available)
    return None


def count_player_and_bot_cities(used_cities):
    if not used_cities:
        return 0, 0

    bot_cities = (len(used_cities) + 1) // 2
    player_cities = len(used_cities) // 2

    return player_cities, bot_cities


def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("🎮 Новая игра"),
        KeyboardButton("📊 Статистика"),
        KeyboardButton("❓ Правила"),
        KeyboardButton("⏹ Стоп игра"),
        KeyboardButton("📊о Проекте"),
    )
    return keyboard


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎮 *Добро пожаловать в игру 'Города'!*\n\n"
        f"📚 В моей базе *{len(ALL_CITIES)}* городов\n\n"
        "Правила простые:\n"
        "• Я называю город, ты называешь город на последнюю букву\n"
        "• Города не должны повторяться\n"
        "• Можно использовать кнопки для управления\n\n"
        "Нажми *'🎮 Новая игра'* чтобы начать!"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['info'])
@bot.message_handler(func=lambda message: message.text == "📊о Проекте")
def info(message):
    info_text = (
        "*Создатель данного проекта:*\n"
        "__*Дмитрий Самоделкин*__\n\n"
        "*Проект создан: 06.03.2026*\n"
        "Если все прочитал(а) то ты лох\n"


    )
    bot.send_message(
        message.chat.id,
        info_text,
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )


@bot.message_handler(commands=['game'])
@bot.message_handler(func=lambda message: message.text == "🎮 Новая игра")
def new_game(message):
    chat_id = message.chat.id


    if not ALL_CITIES:
        bot.send_message(
            chat_id,
            "❌ Ошибка: список городов пуст! Вы Выиграли!.",
            reply_markup=main_keyboard()
        )
        return

    first_city = random.choice(ALL_CITIES)

    games[chat_id] = {
        'used_cities': [first_city],
        'last_letter': get_last_letter(first_city)
    }

    response = (
        f"🎯 *Игра началась!*\n\n"
        f"🤖 Я называю: *{first_city.capitalize()}*\n"
        f"➡️ Тебе на букву: *{games[chat_id]['last_letter']}*\n\n"
        f"Введи свой город или нажми '⏹ Стоп игра'"
    )
    bot.send_message(chat_id, response, parse_mode='Markdown')


@bot.message_handler(commands=['stop'])
@bot.message_handler(func=lambda message: message.text == "⏹ Стоп игра")
def stop_game(message):
    chat_id = message.chat.id

    if chat_id in games:
        player_cities, bot_cities = count_player_and_bot_cities(games[chat_id]['used_cities'])


        if player_cities > bot_cities:
            result = "🎉 Ты победил!"
        elif player_cities < bot_cities:
            result = "🤖 Победил бот!"
        else:
            result = "🤝 Ничья!"

        del games[chat_id]
        bot.send_message(
            chat_id,
            f"⏹ *Игра завершена!*\n\n"
            f"📊 Итоговый счёт:\n"
            f"🧑 Ты: *{player_cities}*\n"
            f"🤖 Бот: *{bot_cities}*\n\n"
            f"{result}",
            parse_mode='Markdown'
        )
    else:
        bot.send_message(chat_id, "❌ У тебя нет активной игры! Нажми '🎮 Новая игра'")


@bot.message_handler(func=lambda message: message.text == "❓ Правила")
def show_rules(message):
    rules_text = (
        "📖 *Правила игры в города:*\n\n"
        "1️⃣ Первый город называет бот\n"
        "2️⃣ Твой город должен начинаться на последнюю букву предыдущего города\n"
        "3️⃣ Нельзя называть города, которые уже были в игре\n"
        "4️⃣ Если город заканчивается на 'ь', 'ъ', 'ы', берётся предпоследняя буква\n"
        "5️⃣ Если не знаешь город - можно сдаться кнопкой '⏹ Стоп игра'\n\n"
        "🎯 Побеждает тот, кто назвал больше городов!"
    )
    bot.send_message(message.chat.id, rules_text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "📊 Статистика")
def show_stats(message):
    chat_id = message.chat.id

    if chat_id in games:
        used = games[chat_id]['used_cities']
        player_cities, bot_cities = count_player_and_bot_cities(used)

        stats_text = (
            f"📊 *Статистика текущей игры:*\n\n"
            f"🧑 Ты назвал: *{player_cities}*\n"
            f"🤖 Бот назвал: *{bot_cities}*\n"
            f"📍 Всего ходов: *{len(used)}*\n"
            f"🏙 Последний город: *{used[-1].capitalize()}*\n"
            f"➡️ Следующая буква: *{games[chat_id]['last_letter']}*"
        )
    else:
        stats_text = "📊 *Нет активной игры!*\nНажми '🎮 Новая игра' чтобы начать."

    bot.send_message(chat_id, stats_text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def process_game(message):
    chat_id = message.chat.id
    user_city = message.text.strip().upper()

    if chat_id not in games:
        bot.send_message(
            chat_id,
            "❌ Сначала начни игру! Нажми '🎮 Новая игра'",
            reply_markup=main_keyboard()
        )
        return

    game = games[chat_id]

    if user_city not in ALL_CITIES:
        bot.send_message(
            chat_id,
            f"❌ Город '{message.text}' не найден в моей базе. Попробуй другой!"
        )
        return


    if user_city[0] != game['last_letter']:
        bot.send_message(
            chat_id,
            f"❌ Город должен начинаться на букву *{game['last_letter']}*",
            parse_mode='Markdown'
        )
        return


    if user_city in game['used_cities']:
        bot.send_message(
            chat_id,
            f"❌ Город '{message.text}' уже называли! Придумай другой."
        )
        return


    game['used_cities'].append(user_city)


    last_letter = get_last_letter(user_city)


    bot_city = find_city_by_letter(last_letter, game['used_cities'])

    if bot_city is None:

        player_cities, bot_cities = count_player_and_bot_cities(game['used_cities'])

        bot.send_message(
            chat_id,
            f"✅ Твой город *{message.text}* принят!\n\n"
            f"🎉 *ПОЗДРАВЛЯЮ! ТЫ ПОБЕДИЛ!*\n"
            f"Я не знаю больше городов на букву '{last_letter}'.\n\n"
            f"📊 Финальный счёт:\n"
            f"🧑 Ты: *{player_cities}*\n"
            f"🤖 Бот: *{bot_cities}*",
            parse_mode='Markdown'
        )
        del games[chat_id]
        return


    game['used_cities'].append(bot_city)
    game['last_letter'] = get_last_letter(bot_city)


    response = (
        f"Твой город *{message.text}* принят!\n\n"
        f"Я отвечаю: *{bot_city.capitalize()}*\n"
        f"Тебе на букву: *{game['last_letter']}*\n\n"
        f"Твоя очередь!"
    )
    bot.send_message(chat_id, response, parse_mode='Markdown')


print(" Бот запущен и готов к игре!")
print(f"Загружено городов: {len(ALL_CITIES)}")

if __name__ == '__main__':
    bot.infinity_polling()