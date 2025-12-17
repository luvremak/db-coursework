from aiogram import Router
from . import common, company


def register_handlers(router: Router):
    common.register_common_handlers(router)
    company.register_company_handlers(router)
