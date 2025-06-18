# bot/handler/models/fork_maker.py

from typing import Any, Callable, Coroutine, Dict, Optional
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from functools import partial
import inspect
import itertools
import logging


logger = logging.getLogger(__name__)


def is_async_callable(func: Callable) -> bool:
    """
    Проверяет, является ли переданная функция асинхронной.
    Поддерживает также functools.partial.
    """
    if inspect.iscoroutinefunction(func):
        return True

    if isinstance(func, partial):
        return is_async_callable(func.func)

    return False


def _cb_factory(prefix: str):
    """
    Создаёт CallbackData-фабрику с динамическим классом,
    у которого одно поле — `name`, и указанный префикс.
    """
    class DynamicCallbackData(CallbackData, prefix=prefix):
        name: str
    return DynamicCallbackData


class BaseFlowCollector:
    """
    Упрощает регистрацию набора callback-хендлеров и построение
    inline-клавиатуры с кнопками, привязанными к этим хендлерам.

    При вызове данного экземпляра - вызывает соответствующий handler
    """
    _name_counter = itertools.count(1)

    def __init__(self,
                 prefix: str,
                 base_buttons: Optional[list[InlineKeyboardButton]] = None,
                ):
        """
        :param prefix: Префикс для CallbackData
        :param base_buttons: Дополнительные кнопки, которые будут добавлены внизу клавиатуры
        """
        self._handlers: Dict[str, dict] = {}
        self._base_buttons = base_buttons
        self.cb_factory = _cb_factory(prefix)


    def register_callback(
            self,
            text:str,
            name: Optional[str] = None,
        ) -> Callable[[Callable], Callable]:
        """
        Декоратор для регистрации callback-хендлера.
        Используется как:

        @flow.register_callback("Текст кнопки")
        async def handler(...): ...

        :param text: Текст кнопки
        :param name: Явное имя хендлера (если не указано — генерируется автоматически)
        :return: Декоратор
        """

        def decorator(func: Callable):
            final_name = name or f"auto_{next(self._name_counter)}"
            self._handlers[final_name] = {
                "handler": func,
                "text": text
            }
            return func
        return decorator


    def register(
        self,
        text: str,
        # handler: Callable,
        handler: Callable[[CallbackQuery, FSMContext], Coroutine[Any, Any, Any]],
        # name: Optional[str] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ):
        """
        Регистрирует хендлер вручную (вне декоратора).

        :param text: Текст кнопки
        :param handler: Асинхронная функция-обработчик
        # :param name: Имя, под которым будет сохранён хендлер (опционально)
        :param kwargs: Дополнительные параметры, которые будут переданы в handler через partial
        """
        # name = name or f"auto_{next(self._name_counter)}"
        name = f"auto_{next(self._name_counter)}"

        if not is_async_callable(handler):
            raise TypeError(
                    f"Handler '{handler}' должен быть async (coroutine),"
                    f"но получен {type(handler)}"
            )

        if kwargs:
            handler = partial(handler, **kwargs)

        self._handlers[name] = {"handler": handler, "text": text}


    def register_many(
        self,
        entries: list[
            tuple[
                str,  # text
                # Callable[[CallbackQuery, FSMContext], Coroutine[Any, Any, Any]],  # handler
                Callable, # handler
                Optional[dict[str, Any]]  # kwargs
                ]
            ]
        ):
        """
        Массовая регистрация хендлеров.
        Каждый элемент entries — кортеж: (text, handler[, kwargs])

        :param entries: Список кортежей для регистрации хендлеров
        """
        for entry in entries:
            try:
                if len(entry) == 2:
                    text, handler = entry
                    kwargs = None
                elif len(entry) == 3:
                    text, handler, kwargs = entry
                    if kwargs is not None and not isinstance(kwargs, dict):
                        raise TypeError(f"kwargs должен быть dict, а получен {type(kwargs)}")
                else:
                    raise ValueError("Ожидалось 2 или 3 элемента в кортеже.")

                self.register(text=text, handler=handler, kwargs=kwargs)

            except Exception as e:
                raise ValueError(f"Некорректная запись в entries: {entry}. Ошибка: {e}") from e


    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        """
        Вызывается при срабатывании callback'а. Определяет, какой хендлер запустить.

        :param callback: Объект callback-запроса от Telegram
        :param state: Контекст состояния FSM
        """
        if not callback.data:
            await callback.answer("Некорректный callback.")
            return

        cb_data = self.cb_factory.unpack(callback.data)
        handler_entry = self._handlers.get(cb_data.name)

        if not handler_entry:
            return

        await handler_entry["handler"](callback, state)


    def build_keyboard(self) -> InlineKeyboardMarkup:
        """
        Формирует inline-клавиатуру на основе зарегистрированных обработчиков
        и (опционально) базовых кнопок, заданных при инициализации.

        :return: Объект InlineKeyboardMarkup с готовыми кнопками.
        """
        builder = InlineKeyboardBuilder()

        for name, item in self._handlers.items():
            callback_data = self.cb_factory(name=name).pack()
            builder.button(text=item["text"], callback_data=callback_data)

        builder.adjust(1)

        if self._base_buttons:
            builder.row(*self._base_buttons)

        return builder.as_markup()



    # def get_registered_keys(self) -> set[str]:
    #     return set(self._handlers.keys())
