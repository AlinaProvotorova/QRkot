from datetime import datetime
from typing import List

from app.models import BaseModel


def investing(
        target: BaseModel,
        sources: List[BaseModel]
):
    result = []
    for source in sources:
        balance = min(
            source.full_amount - source.invested_amount,
            target.full_amount - (target.invested_amount or 0)
        )
        if balance == 0:
            break
        for base_model in [source, target]:
            base_model.invested_amount = (base_model.invested_amount or 0) + balance
            if base_model.invested_amount == base_model.full_amount:
                base_model.fully_invested = True
                base_model.close_date = datetime.now()
        result.append(source)
    return result
