from __future__ import annotations

"""
CLI-оболочка экспертной системы для подбора отдыха.
"""

from pathlib import Path
from typing import Dict, Tuple

from explanation import ExplanationComponent
from inference_engine import InferenceEngine
from knowledge_base import KnowledgeBase
from working_memory import WorkingMemory


RULES_PATH = Path(__file__).with_name("rules.yaml")


def ask_yes_no(prompt: str) -> bool:
    """Возвращает True/False в зависимости от ответа пользователя."""
    while True:
        answer = input(f"{prompt} (да/нет): ").strip().lower()
        if answer in {"да", "д", "yes", "y"}:
            return True
        if answer in {"нет", "н", "no", "n"}:
            return False
        print("Пожалуйста, введите 'да' или 'нет'.")


def ask_int(prompt: str) -> int:
    """Запрашивает целое число."""
    while True:
        value = input(f"{prompt}: ").strip()
        try:
            return int(value)
        except ValueError:
            print("Введите целое число.")


def collect_initial_facts(wm: WorkingMemory) -> None:
    """Собирает исходные факты на основе ответов пользователя."""
    budget = ask_int("Введите доступный бюджет (в рублях)")
    if budget < 50000:
        wm.add_fact("Бюджет = <50000", "user")
    if budget >= 50000:
        wm.add_fact("Бюджет = >=50000", "user")
    if budget < 100000:
        wm.add_fact("Бюджет = <100000", "user")
    if budget >= 150000:
        wm.add_fact("Бюджет = >=150000", "user")

    wm.add_fact(
        fact=f"Ограничения по здоровью = {'да' if ask_yes_no('Есть ли ограничения по здоровью?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Хочу море = {'да' if ask_yes_no('Хотите ли вы отдых на море?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Хочу горы = {'да' if ask_yes_no('Интересует ли отдых в горах?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Хочу экскурсии = {'да' if ask_yes_no('Хотите экскурсионную программу?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Есть транспорт = {'да' if ask_yes_no('Есть ли собственный транспорт?') else 'нет'}",
        source="user",
    )
    wm.add_fact(
        fact=f"Короткий отпуск = {'да' if ask_yes_no('Отпуск короче недели?') else 'нет'}",
        source="user",
    )

    season = ""
    while season not in {"лето", "зима"}:
        season = input("Какой сезон планируется (лето/зима): ").strip().lower()
        if season not in {"лето", "зима"}:
            print("Допустимы ответы только 'лето' или 'зима'.")
    wm.add_fact(f"Сезон = {season}", "user")


def choose_strategy() -> str:
    """Позволяет выбрать стратегию разрешения конфликтов."""
    strategies: Dict[str, Tuple[str, str]] = {
        "1": ("order", "По порядку правил"),
        "2": ("specificity", "По специфичности (больше условий)"),
        "3": ("recency", "По недавности фактов"),
    }

    print("\nВыберите стратегию разрешения конфликтов:")
    for key, (_, description) in strategies.items():
        print(f"  {key}. {description}")

    while True:
        choice = input("Ваш выбор [1-3]: ").strip()
        if choice in strategies:
            return strategies[choice][0]
        print("Недопустимый выбор, повторите ввод.")


def print_results(wm: WorkingMemory) -> None:
    """Выводит все полученные факты и итоговые рекомендации."""
    print("\nПолученные факты:")
    for record in wm.items():
        source = "пользователь" if record.source == "user" else f"правило {record.source}"
        print(f"  - {record.fact} (источник: {source})")

    recommendations = [fact for fact in wm.facts() if fact.startswith("Результат = ")]
    if recommendations:
        print("\nРекомендации:")
        for fact in recommendations:
            print(f"  * {fact}")
    else:
        print("\nРекомендаций получить не удалось. Попробуйте изменить исходные факты.")


def explanation_loop(explainer: ExplanationComponent) -> None:
    """Интерактивный цикл запросов объяснений."""
    print("\nВведите интересующий факт для объяснения (пустая строка — выход).")
    while True:
        fact = input("Факт: ").strip()
        if not fact:
            break
        try:
            print(explainer.explain(fact))
        except ValueError as error:
            print(error)


def main() -> None:
    kb = KnowledgeBase.from_yaml(RULES_PATH)
    wm = WorkingMemory()
    collect_initial_facts(wm)

    strategy = choose_strategy()
    engine = InferenceEngine(kb)
    applied_rules = engine.infer(wm, strategy=strategy)
    if applied_rules:
        print("\nСработавшие правила (в порядке применения):")
        for applied in applied_rules:
            print(f"  {applied.iteration}. {applied.rule.id} -> {applied.rule.conclusion}")
    else:
        print("\nНи одно правило не сработало.")

    print_results(wm)

    explainer = ExplanationComponent(wm)
    explanation_loop(explainer)


if __name__ == "__main__":
    main()

