from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from generalBase import questions, clubNames


kb1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
b1 = KeyboardButton(text='/help')
b2 = KeyboardButton(text='/description')
b3 = KeyboardButton(text='Часто задаваемые вопросы')
b4 = KeyboardButton(text='Записатья на кружок')
kb1.add(b1, b2).add(b3, b4)


ikbFAQ = InlineKeyboardMarkup(row_width=2)
ib1 = InlineKeyboardButton(text=questions[0],
                           callback_data='Q1')
ib2 = InlineKeyboardButton(text=questions[1],
                           callback_data='Q2')
ib3 = InlineKeyboardButton(text=questions[2],
                           callback_data='Q3')
ib4 = InlineKeyboardButton(text=questions[3],
                           callback_data='Q4')
ib5 = InlineKeyboardButton(text=questions[4],
                           callback_data='Q5')
ib6 = InlineKeyboardButton(text=questions[5],
                           callback_data='Q6')
ib7 = InlineKeyboardButton(text=questions[6],
                           callback_data='Q7')
ib8 = InlineKeyboardButton(text=questions[7],
                           callback_data='Q8')
ikbFAQ.add(ib1).add(ib2).add(ib3).add(ib4).add(ib5).add(ib6).add(ib7).add(ib8)

ikbClubs = InlineKeyboardMarkup(row_width=2)
ibC1 = InlineKeyboardButton(text=clubNames[0],
                           callback_data='C1')
ibC2 = InlineKeyboardButton(text=clubNames[1],
                           callback_data='C2')
ibC3 = InlineKeyboardButton(text=clubNames[2],
                           callback_data='C3')
ibC4 = InlineKeyboardButton(text=clubNames[3],
                           callback_data='C4')
ikbClubs.add(ibC1, ibC2).add(ibC3, ibC4)


ikbClubs2 = InlineKeyboardMarkup(row_width=2)
ibC21 = InlineKeyboardButton(text=clubNames[0],
                           callback_data='H1')
ibC22 = InlineKeyboardButton(text=clubNames[1],
                           callback_data='H2')
ibC23 = InlineKeyboardButton(text=clubNames[2],
                           callback_data='H3') 
ibC24 = InlineKeyboardButton(text=clubNames[3],
                           callback_data='H4')
ikbClubs2.add(ibC21, ibC22).add(ibC23, ibC24)

ikbA = InlineKeyboardMarkup(row_width=2)
ibA1 = InlineKeyboardButton(text='Назад', 
                            callback_data='FAQ')
ikbA.add(ibA1)