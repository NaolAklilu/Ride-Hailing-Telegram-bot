import asyncio
import logging
import sys
import random

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

TOKEN = "BOT_TOKEN_HERE"
form_router = Router()

users_data = {}
users_ride_history = {} 

class User(StatesGroup):
    name = State()
    role = State()
    phone = State()

class Ride(StatesGroup):
    current_loc = State()
    destination_loc = State()
    rate = State()

@form_router.message(CommandStart())
async def handle_phone_input(message: Message) -> None:
    await message.answer(
    f"Hello {message.from_user.full_name}, Welcome to Ride Hailing Telegram bot", 
    reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Login", callback_data="login"),
                InlineKeyboardButton(text="Signup", callback_data="signup")
            ]
        ],
        resize_keyboard=True
    )
)
    
@form_router.callback_query(lambda c: c.data == "signup")
async def command_signup(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.name)
    await callback_query.message.answer("To sign up, please provide your full name.")

@form_router.callback_query(lambda c: c.data == "login")
async def command_login(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        text="Enjoy our services! \n", 
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Ride Booking", callback_data="ride"),
                    InlineKeyboardButton(text="Driver Matching", callback_data="match")
                ],
                [
                    InlineKeyboardButton(text="Rating & Previews", callback_data="rate")
                ],
                [
                    InlineKeyboardButton(text="History & Receipts", callback_data="history")
                ]
            ],
            resize_keyboard=True
        ))
    
    # user_id = callback_query.message.from_user.id
    # if user_id in users_data:
    #     await display_services(Message)
    # else:
    #     await callback_query.message.answer(
    #     f"Hello {callback_query.message.from_user.full_name}, You were not registered, \nWould like to register?", 
    #     reply_markup=InlineKeyboardMarkup(
    #         inline_keyboard=[
    #             [
    #                 InlineKeyboardButton(text="Yeah", callback_data="register"),
    #                 InlineKeyboardButton(text="No, Thanks", callback_data="cancel_registration")
    #             ]
    #         ],
    #         resize_keyboard=True
    #     ))


@form_router.callback_query(lambda c: c.data == "cancel_registration")
async def command_register(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.answer("Sorry, You can't move forward!")

@form_router.callback_query(lambda c: c.data == "register")
async def command_signup(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(User.name)
    await callback_query.message.answer("To sign up, please provide your full name.")

@form_router.callback_query(lambda c: c.data == "match")
async def command_signup(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(f"You will get matched with driver soon!", 
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Back to Home", callback_data="login")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        ))
     

@form_router.callback_query(lambda c: c.data == "history")
async def command_signup(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(f"You don't have ride history yet", 
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Back to Home", callback_data="login")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        ))


@form_router.callback_query(lambda c: c.data == "ride")
async def process_user_ride_request(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Ride.current_loc)
    await callback_query.message.answer(f"We are so happy to have you in our ride\nPlease can you provide us you current location?")

@form_router.callback_query(lambda c: c.data == "rate")
async def process_user_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Ride.rate)
    await callback_query.message.answer(f"How would you like to rate our service?\n",
        reply_markup=InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text="⭐", callback_data='1')],
            [InlineKeyboardButton(text="⭐⭐", callback_data='2')],
            [InlineKeyboardButton(text="⭐⭐⭐", callback_data='3')],
            [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data='4')],
            [InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data='5')]
        ],
        resize_keyboard=True
    ))

@form_router.callback_query(Ride.rate)
async def handle_user_rating(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data(rate=callback_query.data)
    await callback_query.message.answer(f"Thanks for your feedback!", 
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Back to Home", callback_data="login")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        ))

@form_router.message(Ride.current_loc)
async def handle_current_location_input(message:Message, state: FSMContext) -> None:
    await state.update_data(current_loc=message.text)
    await state.set_state(Ride.destination_loc)
    await message.answer(f"Sure, your destination location?")

@form_router.message(Ride.destination_loc)
async def handle_current_location_input(message:Message, state: FSMContext) -> None:
    data = await state.update_data(destination_loc=message.text)
    estimated_time = random.randint(10, 60)
    estimated_distance = random.randint(1, 10)
    replyMarkup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Back to Home", callback_data="login")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(f"Thanks for choosing us!\n\nYour journey from {data['current_loc']} to {data['destination_loc']}, approximately {estimated_distance} kilometers away, is estimated to take about {estimated_time} minutes.",  reply_markup=replyMarkup)

@form_router.message(User.name)
async def handle_name_input(message:Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(User.phone)
    markup=ReplyKeyboardMarkup(
        keyboard=[
            [ 
                KeyboardButton(text="Share my phone number", request_contact=True),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Great! Now, please use the 'Share my phone number' button to provide your phone number.",
                        reply_markup=markup)

@form_router.message(User.phone, lambda c: c.text == "Share my phone number")
async def handle_phone_input(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(User.role)
    await message.answer(
        "Thanks! Please select your role:", 
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="driver"),
                    KeyboardButton(text="passenger")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

@form_router.message(User.phone, lambda message: message.text != "Share my phone number")
async def handle_phone_ignore_input(message: Message, state: FSMContext) -> None:
    await state.update_data(phone="")
    await state.set_state(User.role)
    await message.answer(
        "Thanks! Please select your role:", 
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="driver"),
                    KeyboardButton(text='passenger')
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@form_router.message(User.role)
async def process_role_input(message: Message, state:FSMContext) -> None:
    data = await state.update_data(role=message.text)
    await state.clear()
    user_id = message.from_user.id

    user = {
        'name': data['name'], 
        'phone':data['phone'], 
        'role':data['role']
    }

    users_data[user_id] = user
    await message.answer(f"Registration completed Successfully!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Back to Home", callback_data="login")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        ))


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == 'cancel')
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    await state.clear()
    
    logging.info("Cancelling state %r", current_state)
    
    await message.answer(
        "Cancelled",
        reply_markup=ReplyKeyboardRemove(),
    )

async def main():
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())