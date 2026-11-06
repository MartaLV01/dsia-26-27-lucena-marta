
from dataclasses import dataclass
import pandas as pd


MIN_UNITS = 0
MIN_PRECIO_UNITARIO = 0

class ValidationError(Exception):
    """Datos que no cumplen reglas de negocio."""

@dataclass(frozen=True)
class SalesRecord:
    region: str
    product: str
    units: float
    unit_price: float

    @property
    def amount(self) -> float:
        return self.units * self.unit_price



class SalesValidator:
    """Single Responsibility: solo valida."""

    def split(self, frame: pd.DataFrame) -> tuple[list[SalesRecord], pd.DataFrame, pd.DataFrame]:
        required_columns = {
            "region",
            "producto",
            "unidades",
            "precio_unitario",
        }

        missing_columns = required_columns - set(frame.columns)

        if missing_columns:
            raise ValidationError(
                f"Faltan columnas obligatorias: {sorted(missing_columns)}"
            )
        
        work = frame.copy()
        work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
        work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")
        # Cambio ok por pass_validation
        pass_validation = work["unidades"].notna() & (work["unidades"] > MIN_UNITS) & (work["precio_unitario"] > MIN_PRECIO_UNITARIO)
        valid_rows = [
            SalesRecord(
                region=str(row.region),
                product=str(row.producto),
                units=float(row.unidades),
                unit_price=float(row.precio_unitario),
            )
            for row in work.loc[pass_validation].itertuples(index=False)
        ]
        return valid_rows, work.loc[pass_validation], work.loc[~pass_validation]
