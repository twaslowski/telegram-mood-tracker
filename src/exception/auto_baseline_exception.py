from src.model.user import User


class MetricBaselinesNotDefinedException(Exception):
    def __init__(self, user: User):
        message = (
            f"Not all metrics have baselines defined. "
            f"Undefined metrics: {','.join(user.get_metrics_without_baselines())}"
        )
        super().__init__(message)


class AutoBaselineTimeNotDefinedException(Exception):
    def __init__(self):
        super().__init__("Auto-baseline time not defined")
