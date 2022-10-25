#Импорт используемых библиотек и токена
from telebot import types
import time
import cv2
from Settings import CONST_bot_token as bot

#Установление используемых каскадов для распознования
face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

#Алгоритм распознования лица
def raspoznovanie(image_path):
    img = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade_db.detectMultiScale(img_gray, 1.1, 19)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        img_gray_face = img_gray[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(img_gray_face, 1.1, 19)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(img, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 0, 0), 2)
    new_path = image_path + '_' + '.jpg'
    cv2.imwrite(new_path, img)
    return new_path

#Функция удаления неиспользуемого контента для предотвращения засорения временной папки
# def clear_content(chat_id):
#      try:
#          for img in images[chat_id]:
#              os.remove(img)
#      except Exception as e:
#          time.sleep(3)
#          clear_content(chat_id)
#      images[chat_id] = []

#Создание нового ассоциативного массива
images = dict()

#Описание начала работы бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Как дела?")
    item2 = types.KeyboardButton("Перейдем к делу?")
    markup.add(item1, item2)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Как дела?")
    item2 = types.KeyboardButton("Перейдем к делу?")
    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный распозновать лица и общаться.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


#Описание рабочей части бота
@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text in ('Перейдем к делу?', '/go'):
            # bot.send_message(message.chat.id, "Эта часть бота пока не может с вами разговаривать!\nПростите её, пожалуйста, она не хотела вас обидеть.\nВы самый лучший человек!")
            # bot.send_photo(message.chat.id, open("sorry.jpg", 'rb'))
            bot.send_message(message.chat.id, "Чтобы обработать фото отправьте фотографию.")
            bot.register_next_step_handler(message, handle_docs_photo)
        elif message.text == 'Как дела?':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
            item2 = types.InlineKeyboardButton("Не очень", callback_data='bad')
            markup.add(item1, item2)
            bot.send_message(message.chat.id, 'Отлично, сам как?', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить 😢, Напиши /go')

#Загрузка фотографий на сервер
@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        print(message.photo[:-1])
        images[str(message.chat.id)] = []
        try:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = 'tmp/' + file_info.file_path
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
                bot.reply_to(message, "Фото добавлено")
                bot.send_message(message.chat.id, "Ожидайте, пожалуйста!")
                bot.send_message(message.chat.id, "Идет обработка...")
                images[str(message.chat.id)].append(src)
        except Exception as e:
                bot.reply_to(message, e)
    except Exception as e:
        bot.send_message(message.chat.id, "Простите, видимо вместо фотографии вы прислали мне что-то другое")
        bot.send_message(message.chat.id, "Чем очень сильно меня запутали, напишите мне что-нибудь, пожалуйста")

    time.sleep(3)

    print('img: ', images)
    reply_img = ''
    if (len(images[str(message.chat.id)]) == 1):
        reply_img = raspoznovanie(images[str(message.chat.id)][0])
        images[str(message.chat.id)].append(reply_img)
        bot.send_photo(message.chat.id, open(reply_img, 'rb'))
        #clear_content(str(message.chat.id))


# #Описание общительной части бота
@   bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и отличненько 😊')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Бывает 😢')

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="😊 Как дела?",
                                  reply_markup=None)

            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="😢ВЫ САМЫЙ ЛУЧШИЙ ЧЕЛОВЕК НА БЕЛОМ СВЕТЕ!!!😢")

    except Exception as e:
        print(repr(e))


bot.infinity_polling()