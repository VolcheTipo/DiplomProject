#Нечёткая логика для агрегации оценок аномальности от нескольких детекторов

def _fuzzify(x: float) -> str:
    #Перевод числовой оценки в лингвистическую переменную
    if x < 0.3:
        return "LOW"
    elif x < 0.7:
        return "MEDIUM"
    else:
        return "HIGH"

def _apply_rules(labels: list) -> float:
    #чем больше HIGH или MEDIUM — тем выше финальная оценка
    high = sum(v == "HIGH" for v in labels)
    medium = sum(v == "MEDIUM" for v in labels)
    n = len(labels)
    if n == 0:
        return 0.0
    ratio_high = high / n
    ratio_medium = medium / n

    if ratio_high >= 0.6:
        return 0.9
    elif ratio_high >= 0.4:
        return 0.75
    elif ratio_high >= 0.3 and ratio_medium >= 0.3:
        return 0.6
    elif ratio_medium >= 0.6:
        return 0.45
    elif ratio_medium >= 0.2:
        return 0.3
    else:
        return 0.1

def fuzzy_score(
        kmeans_score: float,
        iforest_score: float,
        svm_score: float,
        stat_score: float,
        ml_score: float,
        bad_packet_score: float | None = None,
) -> float:
    #Агрегирует оценки нескольких детекторов в единую гибридную оценку от 0 до 1
    labels = [
        _fuzzify(kmeans_score),
        _fuzzify(iforest_score),
        _fuzzify(svm_score),
        _fuzzify(stat_score),
        _fuzzify(ml_score),
    ]
    if bad_packet_score is not None:
        labels.append(_fuzzify(bad_packet_score))
    return _apply_rules(labels)
