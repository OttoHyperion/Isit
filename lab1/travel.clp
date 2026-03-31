;; ============================================================================
;; РАЗДЕЛ 1: ОПРЕДЕЛЕНИЕ ШАБЛОНОВ (DEFTEMPLATES)
;; ============================================================================

;; Шаблон для хранения всех входных данных пользователя
(deftemplate user-input
  "Структура для хранения всех ответов пользователя"
  (slot budget-int          (type INTEGER)  (default 0))
  (slot health-limit        (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot want-sea            (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot want-mountains      (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot want-excursions     (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot has-transport       (type SYMBOL)   (default nil) (allowed-symbols да нет nil))
  (slot season              (type SYMBOL)   (default nil) (allowed-symbols лето зима nil))
  (slot short-vacation      (type SYMBOL)   (default nil) (allowed-symbols да нет nil)))


;; ============================================================================
;; РАЗДЕЛ 2: НАЧАЛЬНЫЕ ФАКТЫ (DEFFACTS)
;; ============================================================================

(deffacts startup
  "Начальные факты для запуска системы после команды (reset)"
  (stage awaiting-input)
  (system-ready))


;; ============================================================================
;; РАЗДЕЛ 3: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (DEFFUNCTIONS)
;; ============================================================================

;; Функция для запроса целого числа с валидацией
(deffunction ask-int (?question)
  "Запрашивает у пользователя целое число и проверяет корректность ввода"
  (printout t ?question " ")
  (bind ?input (read))
  (while (not (integerp ?input))
    (printout t "Ошибка! Введите целое число." crlf)
    (printout t ?question " ")
    (bind ?input (read)))
  (return ?input))

;; Функция для запроса ответа да/нет с валидацией
(deffunction ask-yes-no (?question)
  "Запрашивает у пользователя ответ да или нет и проверяет корректность"
  (printout t ?question " (да/нет): ")
  (bind ?input (read))
  (while (and (neq ?input да) (neq ?input нет))
    (printout t "Ошибка! Введите 'да' или 'нет'." crlf)
    (printout t ?question " (да/нет): ")
    (bind ?input (read)))
  (return ?input))

;; Функция для запроса сезона с валидацией
(deffunction ask-season (?question)
  "Запрашивает у пользователя сезон: лето или зима"
  (printout t ?question " (лето/зима): ")
  (bind ?input (read))
  (while (and (neq ?input лето) (neq ?input зима))
    (printout t "Ошибка! Введите 'лето' или 'зима'." crlf)
    (printout t ?question " (лето/зима): ")
    (bind ?input (read)))
  (return ?input))


;; ============================================================================
;; РАЗДЕЛ 4: ПРАВИЛА ИНИЦИАЛИЗАЦИИ И ОПРОСА
;; ============================================================================

;; Правило запуска интерактивного опроса
(defrule init-questions
  "Запускает процесс опроса пользователя при старте системы"
  (declare (salience 100))
  ?stage-fact <- (stage awaiting-input)
  (system-ready)
  =>
  (printout t crlf)
  (printout t "========================================" crlf)
  (printout t "СИСТЕМА РЕКОМЕНДАЦИЙ ПУТЕШЕСТВИЙ" crlf)
  (printout t "========================================" crlf)
  (printout t crlf)
  
  ;; Опрос пользователя через функции
  (bind ?budget (ask-int "Введите ваш бюджет (в условных единицах):"))
  (bind ?health (ask-yes-no "Есть ли у вас ограничения по здоровью?"))
  (bind ?sea (ask-yes-no "Хотите ли вы отдых на море?"))
  (bind ?mountains (ask-yes-no "Хотите ли вы отдых в горах?"))
  (bind ?excursions (ask-yes-no "Хотите ли вы экскурсии?"))
  (bind ?transport (ask-yes-no "Есть ли у вас личный транспорт?"))
  (bind ?season (ask-season "Какой сезон поездки?"))
  (bind ?short (ask-yes-no "У вас короткий отпуск?"))
  
  ;; Ассерт факта с пользовательскими данными
  (assert (user-input
    (budget-int ?budget)
    (health-limit ?health)
    (want-sea ?sea)
    (want-mountains ?mountains)
    (want-excursions ?excursions)
    (has-transport ?transport)
    (season ?season)
    (short-vacation ?short)))
  
  ;; Переход к фазе вывода
  (retract ?stage-fact)
  (assert (stage inference))
  (printout t crlf "Анализируем ваши предпочтения..." crlf crlf))


;; ============================================================================
;; РАЗДЕЛ 5: ПРАВИЛА КАТЕГОРИЗАЦИИ БЮДЖЕТА (ПРАВИЛА 1-3)
;; ============================================================================

;; Правило 1: Бюджет < 50000 => низкий
(defrule rule-01-categorize-budget-low
  "Категоризация бюджета как низкого при значении < 50000"
  (stage inference)
  (user-input (budget-int ?n))
  (test (< ?n 50000))
  (not (budget-category ?))
  =>
  (assert (budget-category низкий))
  (printout t "[Правило 1] Бюджет < 50000 => категория: низкий" crlf))

;; Правило 2: 50000 <= Бюджет < 100000 => средний
(defrule rule-02-categorize-budget-medium
  "Категоризация бюджета как среднего при значении 50000-99999"
  (stage inference)
  (user-input (budget-int ?n))
  (test (>= ?n 50000))
  (test (< ?n 100000))
  (not (budget-category ?))
  =>
  (assert (budget-category средний))
  (printout t "[Правило 2] 50000 <= Бюджет < 100000 => категория: средний" crlf))

;; Правило 2 (продолжение): 100000 <= Бюджет < 150000 => средний
(defrule rule-02b-categorize-budget-medium-high
  "Категоризация бюджета как среднего при значении 100000-149999"
  (stage inference)
  (user-input (budget-int ?n))
  (test (>= ?n 100000))
  (test (< ?n 150000))
  (not (budget-category ?))
  =>
  (assert (budget-category средний))
  (printout t "[Правило 2] 100000 <= Бюджет < 150000 => категория: средний" crlf))

;; Правило 3: Бюджет >= 150000 => высокий
(defrule rule-03-categorize-budget-high
  "Категоризация бюджета как высокого при значении >= 150000"
  (stage inference)
  (user-input (budget-int ?n))
  (test (>= ?n 150000))
  (not (budget-category ?))
  =>
  (assert (budget-category высокий))
  (printout t "[Правило 3] Бюджет >= 150000 => категория: высокий" crlf))


;; ============================================================================
;; РАЗДЕЛ 6: ПРАВИЛА ОПРЕДЕЛЕНИЯ НАПРАВЛЕНИЯ ПОЕЗДКИ (ПРАВИЛА 4-5)
;; ============================================================================

;; Правило 4: низкий бюджет + ограничения здоровья => Россия
(defrule rule-04-russia-trip-budget-health
  "Низкий бюджет и ограничения по здоровью => поездка по России"
  (stage inference)
  (budget-category низкий)
  (user-input (health-limit да))
  (not (trip-russia да))
  =>
  (assert (trip-russia да))
  (printout t "[Правило 4] Бюджет низкий + ограничения здоровья => Поездка по России = да" crlf))

;; Правило 5: средний/высокий бюджет + нет ограничений => заграница возможна
(defrule rule-05-abroad-trip-possible
  "Средний или высокий бюджет без ограничений здоровья => заграница возможна"
  (stage inference)
  (budget-category ?budget&средний|высокий)
  (user-input (health-limit нет))
  (not (trip-abroad да))
  =>
  (assert (trip-abroad да))
  (printout t "[Правило 5] Бюджет " ?budget " + нет ограничений => Возможна заграница = да" crlf))


;; ============================================================================
;; РАЗДЕЛ 7: ПРАВИЛА ОПРЕДЕЛЕНИЯ ТИПА ОТДЫХА (ПРАВИЛА 6-9)
;; ============================================================================

;; Правило 6: море + лето => пляжный отдых
(defrule rule-06-beach-vacation-available
  "Желание моря в летний сезон => пляжный отдых доступен"
  (stage inference)
  (user-input (want-sea да) (season лето))
  (not (beach-vacation да))
  =>
  (assert (beach-vacation да))
  (printout t "[Правило 6] Хочу море + сезон лето => Доступен пляжный отдых = да" crlf))

;; Правило 7: горы + лето => летний горный отдых
(defrule rule-07-summer-mountain-vacation
  "Желание гор в летний сезон => летний горный отдых"
  (stage inference)
  (user-input (want-mountains да) (season лето))
  (not (summer-mountain да))
  =>
  (assert (summer-mountain да))
  (printout t "[Правило 7] Хочу горы + сезон лето => Доступен летний горный отдых = да" crlf))

;; Правило 8: горы + зима => горнолыжный отдых
(defrule rule-08-ski-vacation-available
  "Желание гор в зимний сезон => горнолыжный отдых"
  (stage inference)
  (user-input (want-mountains да) (season зима))
  (not (ski-vacation да))
  =>
  (assert (ski-vacation да))
  (printout t "[Правило 8] Хочу горы + сезон зима => Доступен горнолыжный отдых = да" crlf))

;; Правило 9: экскурсии + транспорт => городской тур
(defrule rule-09-city-tour-available
  "Желание экскурсий при наличии транспорта => городской тур"
  (stage inference)
  (user-input (want-excursions да) (has-transport да))
  (not (city-tour да))
  =>
  (assert (city-tour да))
  (printout t "[Правило 9] Хочу экскурсии + есть транспорт => Доступен городской тур = да" crlf))


;; ============================================================================
;; РАЗДЕЛ 8: ПРАВИЛА КОМБИНИРОВАНИЯ НАПРАВЛЕНИЯ И ТИПА (ПРАВИЛА 10-17)
;; ============================================================================

;; Правило 10: Россия + пляжный => пляж в России
(defrule rule-10-beach-russia
  "Поездка по России и пляжный отдых => пляжный отдых в России"
  (stage inference)
  (trip-russia да)
  (beach-vacation да)
  (not (beach-russia да))
  =>
  (assert (beach-russia да))
  (printout t "[Правило 10] Россия + пляжный отдых => Доступен пляжный отдых в России = да" crlf))

;; Правило 11: Заграница + пляжный => пляж за границей
(defrule rule-11-beach-abroad
  "Заграница и пляжный отдых => пляжный отдых за границей"
  (stage inference)
  (trip-abroad да)
  (beach-vacation да)
  (not (beach-abroad да))
  =>
  (assert (beach-abroad да))
  (printout t "[Правило 11] Заграница + пляжный отдых => Доступен пляжный отдых за границей = да" crlf))

;; Правило 12: Россия + горнолыжный => зимний горный в России
(defrule rule-12-ski-russia
  "Поездка по России и горнолыжный отдых => зимний горный отдых в России"
  (stage inference)
  (trip-russia да)
  (ski-vacation да)
  (not (ski-russia да))
  =>
  (assert (ski-russia да))
  (printout t "[Правило 12] Россия + горнолыжный => Доступен зимний горный отдых в России = да" crlf))

;; Правило 13: Заграница + горнолыжный => зимний горный за границей
(defrule rule-13-ski-abroad
  "Заграница и горнолыжный отдых => зимний горный отдых за границей"
  (stage inference)
  (trip-abroad да)
  (ski-vacation да)
  (not (ski-abroad да))
  =>
  (assert (ski-abroad да))
  (printout t "[Правило 13] Заграница + горнолыжный => Доступен зимний горный отдых за границей = да" crlf))

;; Правило 14: Россия + летний горный => летний горный в России
(defrule rule-14-summer-mountain-russia
  "Поездка по России и летний горный отдых => летний горный отдых в России"
  (stage inference)
  (trip-russia да)
  (summer-mountain да)
  (not (summer-mountain-russia да))
  =>
  (assert (summer-mountain-russia да))
  (printout t "[Правило 14] Россия + летний горный => Доступен летний горный отдых в России = да" crlf))

;; Правило 15: Заграница + летний горный => летний горный за границей
(defrule rule-15-summer-mountain-abroad
  "Заграница и летний горный отдых => летний горный отдых за границей"
  (stage inference)
  (trip-abroad да)
  (summer-mountain да)
  (not (summer-mountain-abroad да))
  =>
  (assert (summer-mountain-abroad да))
  (printout t "[Правило 15] Заграница + летний горный => Доступен летний горный отдых за границей = да" crlf))

;; Правило 16: Россия + городской тур => городской тур в России
(defrule rule-16-city-tour-russia
  "Поездка по России и городской тур => городской тур в России"
  (stage inference)
  (trip-russia да)
  (city-tour да)
  (not (city-russia да))
  =>
  (assert (city-russia да))
  (printout t "[Правило 16] Россия + городской тур => Городской тур в России = да" crlf))

;; Правило 17: Заграница + городской тур => городской тур за границей
(defrule rule-17-city-tour-abroad
  "Заграница и городской тур => городской тур за границей"
  (stage inference)
  (trip-abroad да)
  (city-tour да)
  (not (city-abroad да))
  =>
  (assert (city-abroad да))
  (printout t "[Правило 17] Заграница + городской тур => Городской тур за границей = да" crlf))


;; ============================================================================
;; РАЗДЕЛ 9: ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ
;; ============================================================================

;; Правило 18: Пляж в России + короткий отпуск => Черноморье
(defrule rule-18-recommend-blacksea
  "Пляж в России + короткий отпуск => Черноморье"
  (declare (salience 10))
  (stage inference)
  (beach-russia да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Черноморье))
  (printout t "[Правило 18] Пляж в России + короткий отпуск => Результат = Черноморье" crlf))

;; Правило 19: Пляж в России + длинный отпуск => Крым
(defrule rule-19-recommend-crimea
  "Пляж в России + длинный отпуск => Крым"
  (declare (salience 10))
  (stage inference)
  (beach-russia да)
  (user-input (short-vacation нет))
  (not (final-result ?))
  =>
  (assert (final-result Крым))
  (printout t "[Правило 19] Пляж в России + длинный отпуск => Результат = Крым" crlf))

;; Правило 20: Пляж заграницей + короткий отпуск => Турция
(defrule rule-20-recommend-turkey
  "Пляж заграницей + короткий отпуск => Турция"
  (declare (salience 10))
  (stage inference)
  (beach-abroad да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Турция))
  (printout t "[Правило 20] Пляж заграницей + короткий отпуск => Результат = Турция" crlf))

;; Правило 21: Пляж заграницей + длинный отпуск => Таиланд
(defrule rule-21-recommend-thailand
  "Пляж заграницей + длинный отпуск => Таиланд"
  (declare (salience 10))
  (stage inference)
  (beach-abroad да)
  (user-input (short-vacation нет))
  (not (final-result ?))
  =>
  (assert (final-result Таиланд))
  (printout t "[Правило 21] Пляж заграницей + длинный отпуск => Результат = Таиланд" crlf))

;; Правило 22: Горнолыжный в России + короткий отпуск => Сочи
(defrule rule-22-recommend-sochi
  "Горнолыжный в России + короткий отпуск => Сочи"
  (declare (salience 10))
  (stage inference)
  (ski-russia да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Сочи))
  (printout t "[Правило 22] Горнолыжный в России + короткий отпуск => Результат = Сочи" crlf))

;; Правило 23: Горнолыжный в России + длинный отпуск => Домбай
(defrule rule-23-recommend-dombay
  "Горнолыжный в России + длинный отпуск => Домбай"
  (declare (salience 10))
  (stage inference)
  (ski-russia да)
  (user-input (short-vacation нет))
  (not (final-result ?))
  =>
  (assert (final-result Домбай))
  (printout t "[Правило 23] Горнолыжный в России + длинный отпуск => Результат = Домбай" crlf))

;; Правило 24: Горнолыжный заграницей + короткий отпуск => Альпы
(defrule rule-24-recommend-alps
  "Горнолыжный заграницей + короткий отпуск => Альпы"
  (declare (salience 10))
  (stage inference)
  (ski-abroad да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Альпы))
  (printout t "[Правило 24] Горнолыжный заграницей + короткий отпуск => Результат = Альпы" crlf))

;; Правило 25: Короткий отпуск + летний горный в России => Кавказ
(defrule rule-25-recommend-caucasus
  "Летний горный в России + короткий отпуск => Кавказ"
  (declare (salience 10))
  (stage inference)
  (summer-mountain-russia да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Кавказ))
  (printout t "[Правило 25] Короткий отпуск + летний горный в России => Результат = Кавказ" crlf))

;; Правило 26: Короткий отпуск + летний горный заграницей => Карпаты
(defrule rule-26-recommend-carpathians
  "Летний горный заграницей + короткий отпуск => Карпаты"
  (declare (salience 10))
  (stage inference)
  (summer-mountain-abroad да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Карпаты))
  (printout t "[Правило 26] Короткий отпуск + летний горный заграницей => Результат = Карпаты" crlf))

;; Правило 27: Длинный отпуск + городской тур в России => Москва
(defrule rule-27-recommend-moscow
  "Городской тур в России + длинный отпуск => Москва"
  (declare (salience 10))
  (stage inference)
  (city-russia да)
  (user-input (short-vacation нет))
  (not (final-result ?))
  =>
  (assert (final-result Москва))
  (printout t "[Правило 27] Короткий отпуск = нет + городской тур в России => Результат = Москва" crlf))

;; Правило 28: Короткий отпуск + городской тур в России => Казань
(defrule rule-28-recommend-kazan
  "Городской тур в России + короткий отпуск => Казань"
  (declare (salience 10))
  (stage inference)
  (city-russia да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Казань))
  (printout t "[Правило 28] Короткий отпуск + городской тур в России => Результат = Казань" crlf))

;; Правило 29: Длинный отпуск + городской тур заграницей => Париж
(defrule rule-29-recommend-paris
  "Городской тур заграницей + длинный отпуск => Париж"
  (declare (salience 10))
  (stage inference)
  (city-abroad да)
  (user-input (short-vacation нет))
  (not (final-result ?))
  =>
  (assert (final-result Париж))
  (printout t "[Правило 29] Короткий отпуск = нет + городской тур заграницей => Результат = Париж" crlf))

;; Правило 30: Короткий отпуск + городской тур заграницей => Прага
(defrule rule-30-recommend-prague
  "Городской тур заграницей + короткий отпуск => Прага"
  (declare (salience 10))
  (stage inference)
  (city-abroad да)
  (user-input (short-vacation да))
  (not (final-result ?))
  =>
  (assert (final-result Прага))
  (printout t "[Правило 30] Короткий отпуск + городской тур заграницей => Результат = Прага" crlf))


;; ============================================================================
;; РАЗДЕЛ 10: ПРАВИЛА ВЫВОДА ИТОГОВОГО РЕЗУЛЬТАТА
;; ============================================================================

;; Правило вывода финальной рекомендации
(defrule display-final-recommendation
  "Выводит итоговую рекомендацию пользователю"
  (declare (salience 5))
  (stage inference)
  (final-result ?destination)
  (not (result-displayed))
  =>
  (assert (result-displayed))
  (printout t crlf)
  (printout t "========================================" crlf)
  (printout t "  ИТОГОВАЯ РЕКОМЕНДАЦИЯ" crlf)
  (printout t "========================================" crlf)
  (printout t "  Рекомендуем вам поехать в: " ?destination crlf)
  (printout t "========================================" crlf)
  (printout t crlf))

;; Правило завершения работы системы
(defrule finalize-system
  "Завершает работу экспертной системы и выводит справочную информацию"
  (declare (salience 1))
  (stage inference)
  (result-displayed)
  =>
  (printout t "Работа экспертной системы завершена." crlf)
  (printout t "Для просмотра всех фактов введите: (facts)" crlf)
  (printout t crlf))


;; ============================================================================
;; КОНЕЦ СКРИПТА
;; ============================================================================
;; Для запуска системы повторно выполните:
;; (reset) - для инициализации начальных фактов из deffacts
;; (run)   - для запуска правил вывода
;; ============================================================================