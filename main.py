from aiogram import Dispatcher, executor, types, Bot
from random import choice
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from keyboard import kb1, ikbFAQ, ikbClubs, ikbA, ikbClubs2
from aiogram.dispatcher.filters import Text

from generalBase import answers, clubMembers, clubNames

from aiogram.types import InputMediaPhoto, ReplyKeyboardRemove

TOKEN_API = '6638220487:AAGI4ho7mcl7Hed9xHs1kkE5F5Ha_C6t4ZQ'

CLUBINDEX = 0

HELP_COMMAND = '''
<b>/start</b> - <em>Начало пользования ботом</em>
<b>/help</b> - <em>Помощь по пользованию ботом</em>
<b>/description</b> - <em>Описание бота</em>
'''

DESCRIPTION = '''
Телеграмм Бот проекта Charity++ с ответами на часто задаваемые вопросы и для записи в различные секции.  
'''

class MyStatesGroup(StatesGroup):
    waiting_for_text = State()
    sign_up = State()

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text='Здравствуйте, приветсвуем вас в нашем боте!',
                           reply_markup=kb1)
    await message.delete()

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text=HELP_COMMAND,
                           parse_mode='HTML')
    await message.delete()

@dp.message_handler(commands=['description'])
async def description_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text=DESCRIPTION,
                           parse_mode='HTML')
    await message.delete()

@dp.message_handler(commands=['event'])
async def event_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text='Выберите клуб для отправки оповещения',
                           reply_markup=ikbClubs2)
    await message.delete()

@dp.message_handler(Text(equals='Часто задаваемые вопросы'))
async def FAQ_inline(message: types.Message):
    await bot.send_photo(chat_id=message.chat.id,
                           photo='https://img.freepik.com/premium-vector/frequently-asked-questions-faq-banner-speech-bubble-with-text-faq-vector-stock-illustration_100456-4253.jpg',
                           reply_markup=ikbFAQ)
    await message.delete()

@dp.message_handler(Text(equals='Записатья на кружок'))
async def Clubs_inline(message: types.Message):
    await bot.send_photo(chat_id=message.chat.id,
                           photo='https://www.mumbaicoworking.com/wp-content/uploads/2019/11/2019-11-04-1.jpg',
                           reply_markup=ikbClubs)
    await message.delete()

@dp.message_handler(state=MyStatesGroup.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    text = message.text
    
    async with state.proxy() as data:
       clubIndex = data['clubIndex']
    for chatID in clubMembers[clubIndex]:
            await bot.send_message(chat_id=chatID,
                                text=text)
    await bot.send_message(chat_id=message.chat.id,
                            text='Оповещения отправлены',
                            reply_markup=kb1)    
    await state.finish()

@dp.message_handler(state=MyStatesGroup.sign_up)
async def process_sign_up(message: types.Message, state: FSMContext):
    text = message.text
    
    async with state.proxy() as data:
       clubIndex = data['clubIndex']

    

    await state.finish()

@dp.callback_query_handler()
async def vote_photo(callback: types.CallbackQuery, state: FSMContext):
    callbackData = callback.data
    clubIndex = 0

    if callbackData == 'FAQ':
        await FAQ_inline(callback.message)
        await callback.answer()

    elif callbackData[0] == 'Q':
        await callback.message.delete()
        await callback.message.answer(text=answers[int(callbackData[1]) - 1], 
                                      reply_markup=ikbA,
                                      parse_mode='HTML')

    elif callbackData[0] == 'C':
        clubIndex = int(callbackData[1]) - 1
        await callback.message.delete()
        if not (callback.message.from_user.id in clubMembers[clubIndex]):
            clubMembers[clubIndex].add(callback.message.chat.id)
            await bot.send_message(chat_id=callback.message.chat.id, 
                                text='Вы записаны')
            print(clubMembers)
        else:
            await bot.send_message(chat_id=callback.message.chat.id, 
                                text=f'Вы уже записаны на {clubNames[clubIndex]}')

    elif callbackData[0] == 'H':
        clubIndex = int(callbackData[1]) - 1
        await callback.message.delete()

        async with state.proxy() as data:
            data["clubIndex"] = clubIndex
        
        await bot.send_message(chat_id=callback.message.chat.id,
                           text='Введите текст оповещения:')
        await MyStatesGroup.waiting_for_text.set()

        await callback.answer()




async def on_startup(_):
    print('Bot is started')

if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)