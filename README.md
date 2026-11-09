# Дизайн ТЗ

Скилл для подготовки понятных заданий дизайнерам: цель, список изменений, термины, ссылки, зависимости полей и конкретные проверки. Без отдельного брифа и служебного раздела «Материалы».

## Установка

Скопируйте папку `skills/design-tz` в каталог скиллов вашего агента или попросите Codex установить скилл из этого репозитория. Для вызова используйте `$design-tz`.

**Из ZIP-релиза.** Скачайте [актуальный design-tz.zip](https://github.com/aedixxe/design-tz/releases/latest/download/design-tz.zip) из [последнего релиза](https://github.com/aedixxe/design-tz/releases/latest) и распакуйте папку `design-tz` в каталог скиллов. Если она уже существует, сначала сохраните свои изменения.

Для полного тандема также установите [актуальный Business-Skill-Issue.zip](https://github.com/aedixxe/Business-Skill-Issue/releases/latest/download/Business-Skill-Issue.zip). Две папки скиллов размещаются рядом. Business Skill Issue проверяет материалы и бизнес-логику, затем Дизайн ТЗ пишет постановку по подготовленным требованиям.

Пример запроса: «Используй $design-tz и собери ТЗ для дизайнера по приложенным материалам».

## Пример и правила

- [Инструкция скилла](skills/design-tz/SKILL.md)
- [Правила текста и оформления](skills/design-tz/references/format.md)
- [Пример PDF](skills/design-tz/assets/reference.pdf)
- [Пример Word](skills/design-tz/assets/reference.docx)

Пример вымышленный и показывает только формат. Клиентские документы и закрытые ссылки в пакет не входят. Для разбора и проверки бизнес-требований используется [Business Skill Issue](https://github.com/aedixxe/Business-Skill-Issue).

Для генератора чистой заготовки нужен Python и `python-docx`. Сам скилл можно использовать без генератора. DOCX/PDF необходимо проверять визуально перед выдачей.
