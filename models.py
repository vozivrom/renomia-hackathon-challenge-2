from __future__ import annotations
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class State(str, Enum):
    draft = "draft"
    accepted = "accepted"
    cancelled = "cancelled"


class AssetType(str, Enum):
    other = "other"
    vehicle = "vehicle"


class ConcludedAs(str, Enum):
    agent = "agent"
    broker = "broker"


class ContractRegime(str, Enum):
    individual = "individual"
    frame = "frame"
    fleet = "fleet"
    coinsurance = "coinsurance"


class ActionOnTermination(str, Enum):
    auto_renewal = "auto-renewal"
    policy_termination = "policy-termination"


class NoticePeriod(str, Enum):
    six_weeks = "six-weeks"


class Premium(BaseModel):
    currency: str = "czk"
    isCollection: bool = False


class ContractOutput(BaseModel):
    contractNumber: Optional[str] = Field(None, description="Číslo pojistné smlouvy")
    insurerName: Optional[str] = Field(None, description="Název pojišťovny")
    state: Optional[State] = Field(None, description="Stav smlouvy: draft/accepted/cancelled")
    assetType: Optional[AssetType] = Field(None, description="other nebo vehicle (pokud pojištění vozidla)")
    concludedAs: Optional[ConcludedAs] = Field(None, description="broker pro Renomia smlouvy, agent pro přímé")
    contractRegime: Optional[ContractRegime] = Field(None, description="individual/frame/fleet/coinsurance")
    startAt: Optional[str] = Field(None, description="Počátek pojištění DD.MM.YYYY")
    endAt: Optional[str] = Field(None, description="Konec pojištění DD.MM.YYYY, null = doba neurčitá")
    concludedAt: Optional[str] = Field(None, description="Datum uzavření smlouvy DD.MM.YYYY")
    installmentNumberPerInsurancePeriod: Optional[int] = Field(None, description="Frekvence plateb: 1=ročně, 2=pololetně, 4=čtvrtletně, 12=měsíčně")
    insurancePeriodMonths: Optional[int] = Field(None, description="Délka pojistného období v měsících: 12=roční, 6=pololetní, 3=čtvrtletní, 1=měsíční")
    premium: Optional[Premium] = Field(None, description="Měna a způsob inkasa pojistného")
    actionOnInsurancePeriodTermination: Optional[ActionOnTermination] = Field(None, description="auto-renewal nebo policy-termination")
    noticePeriod: Optional[NoticePeriod] = Field(None, description="Výpovědní lhůta, null pokud neuvedeno")
    regPlate: Optional[str] = Field(None, description="SPZ vozidla, pouze pro pojištění vozidel")
    latestEndorsementNumber: Optional[str] = Field(None, description="Nejvyšší číslo dodatku ze všech dokumentů jako string")
    note: Optional[str] = Field(None, description="Zvláštní podmínky, null pokud žádné")
