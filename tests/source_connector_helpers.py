from wraeclast_quant.config.resources_loader import load_resources


def official_currency_exchange_resource():
    return [
        resource
        for resource in load_resources("RESOURCES.md")
        if resource.id == "official_currency_exchange_api"
    ][0]


__all__ = ["official_currency_exchange_resource"]
