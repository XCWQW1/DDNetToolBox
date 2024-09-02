def exponential_cdf(x):
  return 1 - 2 ** -x

def points_rank(current_points: int, total_points: int, online_time: int, global_rank: int):
    grade_thresholds = {
        "S+": 1.00,
        "S": 0.95,
        "A+": 0.90,
        "A": 0.85,
        "A-": 0.80,
        "B+": 0.75,
        "B": 0.70,
        "B-": 0.65,
        "C+": 0.60,
        "C": 0.55,
        "C-": 0.50,
        "D+": 0.45,
        "D": 0.40,
        "D-": 0.35,
        "E+": 0.30,
        "E": 0.25,
        "E-": 0.20,
        "F+": 0.15,
        "F": 0.10,
        "F-": 0.05,
        "G": 0.00
    }

    POINTS_WEIGHT = 4
    ONLINE_TIME_MEDIAN = 500
    ONLINE_TIME_WEIGHT = 2
    GLOBAL_RANK_MEDIAN = 1000
    GLOBAL_RANK_WEIGHT = 3

    TOTAL_WEIGHT = POINTS_WEIGHT + ONLINE_TIME_WEIGHT + GLOBAL_RANK_WEIGHT

    score_percentage = (POINTS_WEIGHT * (current_points / total_points) +
                        ONLINE_TIME_WEIGHT * exponential_cdf(online_time / ONLINE_TIME_MEDIAN) +
                        GLOBAL_RANK_WEIGHT * (1 - exponential_cdf(global_rank / GLOBAL_RANK_MEDIAN))) / TOTAL_WEIGHT

    for grade, threshold in sorted(grade_thresholds.items(), key=lambda x: -x[1]):
        if score_percentage >= threshold:
            return grade

    return "G"
