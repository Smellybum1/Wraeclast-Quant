from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation import (
    CurrencyExchangeUiObservation,
    currency_exchange_ui_observation_manual_import_payload,
    currency_exchange_ui_observation_review_notes,
    currency_exchange_ui_observation_signals,
    load_currency_exchange_ui_observation,
    write_currency_exchange_ui_observation_manual_import,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_io import (
    load_currency_exchange_ui_observation as io_module_load,
    write_currency_exchange_ui_observation_manual_import as io_module_write,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_manual_import import (
    currency_exchange_ui_observation_manual_import_payload as manual_import_module_payload,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_models import (
    CurrencyExchangeUiObservation as ModelCurrencyExchangeUiObservation,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_review import (
    currency_exchange_ui_observation_review_notes as review_module_review_notes,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_signals import (
    currency_exchange_ui_observation_signals as signals_module_signals,
)


def test_ui_observation_models_remain_available_from_facade() -> None:
    assert CurrencyExchangeUiObservation is ModelCurrencyExchangeUiObservation


def test_ui_observation_review_notes_remain_available_from_facade() -> None:
    assert currency_exchange_ui_observation_review_notes is review_module_review_notes


def test_ui_observation_signals_remain_available_from_facade() -> None:
    assert currency_exchange_ui_observation_signals is signals_module_signals


def test_ui_observation_manual_import_payload_remains_available_from_facade() -> None:
    assert currency_exchange_ui_observation_manual_import_payload is manual_import_module_payload


def test_ui_observation_io_helpers_remain_available_from_facade() -> None:
    assert load_currency_exchange_ui_observation is io_module_load
    assert write_currency_exchange_ui_observation_manual_import is io_module_write
