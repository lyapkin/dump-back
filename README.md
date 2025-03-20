# Спсок статей
```
/api/articles/
[
    {
        "id": 2,
        "title": "Статья-2",
        "slug": "statya-2",
        "content_concise": "ыаыва",
        "image_url": "http://localhost:8000/media/uploads/2024/04/04/slider-equip-construct-slider.png",
        "date": "2024-04-04"
    },
    {
        "id": 1,
        "title": "Статья",
        "slug": "statya",
        "content_concise": "краткое описание",
        "image_url": "http://localhost:8000/media/uploads/2024/04/04/slider-chomut-equip-construct.png",
        "date": "2024-04-04"
    }
]
```


# Статья
```
/api/articles/statya/
{
    "id": 1,
    "title": "Статья",
    "content": "<h2>dfsd</....",
    "date": "2024-04-04"
}
```


# FAQ
```
/api/faq/
{
    "faqs": [
        {
            "id": 2,
            "answer": "<p>аыывфафвыаппвап</p><p>павпваып</p><p>ваыпвапы</p><p>пывапвап</p>",
            "question": "Какой срок службы лестницы?",
            "categories": [
                1,
                5
            ]
        },
        {
            "id": 1,
            "answer": "<h1>аываыва</h1><ol><li>выавыа</li><li>ываыва</li><li>ываыа</li></ol><p>ываываываы</p><p>выаываываываы</p>",
            "question": "Какие сроки доставки",
            "categories": [
                2
            ]
        }
    ],
    "categories": [
        {
            "id": 1,
            "name": "Комплектация объекта"
        },
        {
            "id": 2,
            "name": "Доставка"
        },
        {
            "id": 3,
            "name": "Оплата"
        },
        {
            "id": 4,
            "name": "Наши проекты"
        },
        {
            "id": 5,
            "name": "Лестницы"
        }
    ]
}
```



# Вакансии список
```
/api/vacancies/
[
    {
        "id": 3,
        "description": "<h1>ываываываыв</h1><ul><li>аыва</li><li>ываыв</li><li>ыва</li></ul><p>ываыва</p>",
        "name": "Работник 4",
        "slug": "rabotnik-4"
    },
    {
        "id": 2,
        "description": "<h1>ыавыаываыва</h1><p>выаывыва</p>",
        "name": "Работник 2",
        "slug": "rabotnik-2"
    }
]
```
# Вакансия
```
/api/vacancies/rabotnik-4/
{
    "id": 3,
    "description": "<h1>ываываываыв</h1><ul><li>аыва</li><li>ываыв</li><li>ыва</li></ul><p>ываыва</p>",
    "name": "Работник 4",
    "slug": "rabotnik-4"
}
```




# Наши проекты список
```
/api/projects/
[
    {
        "id": 1,
        "title": "Строительство Амурского Газоперерабатывающий завода",
        "slug": "stroitelstvo-amurskogo-gazopererabatyvayushij-zavoda",
        "preview_image": "http://localhost:8000/media/uploads/2024/04/04/projects-gazprom_jfYeIJv.jpg",
        "content_concise": "Поставка строительных лесов, опалубки и комплектующих, 2021-2027г. Поставка строительных лесов, опалубки",
        "customer_log": "http://localhost:8000/media/uploads/2024/04/04/gazprom-logo.png",
        "location": "г. Свободный"
    }
]
```

# Наши проекты проект
```
/api/projects/stroitelstvo-amurskogo-gazopererabatyvayushij-zavoda/
[
    {
        "id": 1,
        "title": "Строительство Амурского Газоперерабатывающий завода",
        "slug": "stroitelstvo-amurskogo-gazopererabatyvayushij-zavoda",
        "preview_image": "http://localhost:8000/media/uploads/2024/04/04/projects-gazprom_jfYeIJv.jpg",
        "content_concise": "Поставка строительных лесов, опалубки и комплектующих, 2021-2027г. Поставка строительных лесов, опалубки",
        "customer_log": "http://localhost:8000/media/uploads/2024/04/04/gazprom-logo.png",
        "location": "г. Свободный"
    }
]
```