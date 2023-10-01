import asyncio
from datetime import date, datetime, timedelta
import random
from charity.db.duel import DuelFields
from charity.db.report import ReportFields
from charity.db.route import RouteFields
from charity.services import generate_tags
from charity.consts import UserRoles
from charity.core import db
from charity.db.user import UserFields
from charity.db.fund import FundFields
from charity.services import get_user

# my magic regular expr: (?<=\w)=
async def insert_test_data():
    await db.drop_collections()
    await db.ensure_all_indexes()

    ivan = {
        UserFields.fullname: "Ермолов Иван Олегович",
        UserFields.roles: [UserRoles.dev],
        UserFields.mail: "ermolovivan2018@gmail.com",
        UserFields.company: "Aviacode",
        UserFields.division: "IT",
        UserFields.coins: random.randint(200, 1000),
        UserFields.donations: random.randint(0, 1000),
    }
    # ilya = {
    #     UserFields.fullname: "Хакимов Илья Александрович",
    #     UserFields.roles: [UserRoles.employee],
    #     UserFields.mail: "ilyakhakimov03@gmail.com",
    #     UserFields.company: "Codenrock",
    #     UserFields.division: "IT",
    #     UserFields.coins: random.randint(200, 1000),
    #     UserFields.donations: random.randint(0, 1000),
    # }
    vadim = {
        UserFields.fullname: "Султанов Вадим Муслимович",
        UserFields.roles: [UserRoles.user],
        UserFields.mail: "gu-gu-gu.fake@yandex.ru",
        UserFields.company: "Codenrock",
        UserFields.division: "IT",
        UserFields.coins: random.randint(200, 1000),
        UserFields.donations: random.randint(0, 1000),
    }
    
    await db.user_collection.insert_document(ivan)
    await db.user_collection.insert_document(vadim)
    # await db.user_collection.insert_document(ilya)
    company = ["Codenrock", "Aviacode"]
    division = ["IT", "Lawyer"]

    for user_number in range(40):
        user = {
        UserFields.fullname: "Иванов Иван Иванович",
        UserFields.roles: [UserRoles.user],
        UserFields.mail: f"{user_number}@gmail.com",
        UserFields.company: company[random.randint(0, 1)],
        UserFields.division: division[random.randint(0, 1)],
        UserFields.coins: random.randint(200, 1000),
        UserFields.donations: random.randint(0, 1000),
        }
        await db.user_collection.insert_document(user)

    s1 = "Благотворительный фонд помощи бездомным животным НИКА реализует различные программы помощи животным. У фонда есть два собственных приюта, в которых проживает около 800 животныx"
    nika = {
        FundFields.name: "НИКА",
        FundFields.desc: s1,
        FundFields.categories: generate_tags(s1),
        FundFields.link: "https://fond-nika.ru/",
        FundFields.money: random.randint(1000, 10000),
    }

    s2 = "Чем занимается фонд и как помогает детям. Помощь системная и адресная, волонтерство, донорство, реабилитация, — подробно, с цифрами, чтобы не оставалось вопросов."
    podari_zhizn = {
        FundFields.name: "Подари Жизнь",
        FundFields.desc: s2,
        FundFields.categories: generate_tags(s2),
        FundFields.link: "https://podari-zhizn.ru/ru",
        FundFields.money: random.randint(1000, 10000),
    }

    s3 = "Благотворительный фонд Старость в радость вырос из одноименного волонтерского движения, главной задачей которого было улучшение жизни пожилых людей в интернатах и уменьшение того эмоционального вакуума, в котором они оказываются после попадания в интернат. Мы прошли большой путь от поездок в несколько интернатов до участия в выстраивании системы помощи пожилым людям и инвалидам на государственном уровне.  И мы всегда стояли и стоим на том, что система должна быть для человека, а не человек для системы."
    starikam = {
        FundFields.name: "Старость в Радость",
        FundFields.desc: s3,
        FundFields.categories: generate_tags(s3),
        FundFields.link: "https://starikam.org/about/mission/",
        FundFields.money: random.randint(1000, 10000),
    }

    s4 = "Бездомные — это люди, которые оказались на улице из-за семейных конфликтов, мошенничества, потери работы и проблем со здоровьем. Мы помогаем им"
    night = {
        FundFields.name: "Ночлежка",
        FundFields.desc: s4,
        FundFields.categories: generate_tags(s4),
        FundFields.link: "https://homeless.ru/",
        FundFields.money: random.randint(1000, 10000),
    }
    
    s5 = "Фонд создан в 2007 году для реализации долгосрочных социально значимых программ и проектов, где могут быть применимы принципы социального предпринимательства. Фонд региональных социальных программ Наше будущее – некоммерческая организация, чья цель – способствовать качественным социальным изменениям. Мы добиваемся этого, вкладывая ресурсы и знания в развитие социального предпринимательства."
    future = {
        FundFields.name: "Наше будущее",
        FundFields.desc: s5,
        FundFields.categories: generate_tags(s5),
        FundFields.link: "https://www.nb-fund.ru/",
        FundFields.money: random.randint(1000, 10000),
    }

    s6 = "Некоммерческая благотворительная организация Благотворительный фонд САФМАР была создана 16 cентября 2013 г. Фонд зарегистрирован Главным управлением Министерства юстиции Российской Федерации по г.Москве за учетным номером № 7714014272."
    safmar = {
        FundFields.name: "Сафмар",
        FundFields.desc: s6,
        FundFields.categories: generate_tags(s6),
        FundFields.link: "https://safmar.ru/",
        FundFields.money: random.randint(1000, 10000),
    }

    s7 = "Благотворительный фонд Защити жизнь создан в 2009 году для оказания помощи детям с онкологическими заболеваниями, проживающими и проходящими лечение на территории Новосибирской области. Мы курируем детей на протяжении всего лечения, даже если им требуются медицинские услуги и реабилитация в других клиниках, городах и странах."
    protect_life = {
        FundFields.name: "Защити жизнь",
        FundFields.desc: s7,
        FundFields.categories: generate_tags(s7),
        FundFields.link: "https://save-life.ru/",
        FundFields.money: random.randint(1000, 10000),
    }

    s8 = "Первый и единственный благотворительный фонд в России, который с 2006 года занимается системной помощью детям и взрослым с тяжелыми врожденными нарушениями иммунитета.Миссия фонда – находить пациентов с врожденными заболеваниями иммунитета и помогать им жить полноценной жизнью."
    podsolnuch = {
        FundFields.name: "Подсолнух",
        FundFields.desc: s8,
        FundFields.categories: generate_tags(s8),
        FundFields.link: "https://www.fondpodsolnuh.ru/",
        FundFields.money: random.randint(1000, 10000),
    }

    s9 = "Благотворительный фонд Система — один из крупнейших благотворительных фондов России. С 2004 года мы реализуем социальные, образовательные, культурные и просветительские проекты, направленные на поддержку талантов, развитие территорий и предоставление молодежи равных возможностей личностной, социальной и профессиональной реализации."
    sistema = {
        FundFields.name: "Система",
        FundFields.desc: s9,
        FundFields.categories: generate_tags(s9),
        FundFields.link: "https://bf.sistema.ru/",
        FundFields.money: random.randint(1000, 10000),
    }

    s10 = "Подопечные Благотворительного фонда Адели, это дети, подростки и взрослые инвалиды с поражением центральной нервной системы, заболеваниями опорно-двигательного аппарата, с неврологическими и генетическими заболеваниями. Мы ищем и изучаем новые технологии реабилитации, сотрудничаем с высокопрофессиональными клиниками и врачами, которые могут оказать эффективную помощь нашим подопечным."

    adeli = {
        FundFields.name: "Адели",
        FundFields.desc: s10,
        FundFields.categories: generate_tags(s10),
        FundFields.link: "https://www.adeli-club.com/",
        FundFields.money: random.randint(1000, 10000),
    }

    await db.fund_collection.insert_document(nika)
    await db.fund_collection.insert_document(podari_zhizn)
    await db.fund_collection.insert_document(starikam)
    await db.fund_collection.insert_document(night)
    await db.fund_collection.insert_document(future)
    await db.fund_collection.insert_document(safmar)
    await db.fund_collection.insert_document(protect_life)
    await db.fund_collection.insert_document(podsolnuch)
    await db.fund_collection.insert_document(sistema)
    await db.fund_collection.insert_document(adeli)
    for duel_number in range(5):
        rand_num = random.randint(1, 10)
        duel = {
            DuelFields.bet: random.randint(50, 100),
            DuelFields.user_id:  rand_num,
            DuelFields.owner_id: rand_num + 1,
            DuelFields.referee_id: rand_num + 2,
            DuelFields.is_finish: True,
            DuelFields.winner_id: rand_num
        }
        inserted_duel = await db.duel_collection.insert_document(duel)

        report = {
            ReportFields.user_id: rand_num,
            ReportFields.desc: f"Судья неприльно мне поставил результат. Предоставляю докозательства: https://clck.ru/35uqSa",
            ReportFields.duel_id: inserted_duel["int_id"]
        }
        await db.report_collection.insert_document(report)
        

if __name__ == '__main__':
    asyncio.run(insert_test_data())