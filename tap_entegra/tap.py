"""entegra tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_entegra import streams


class Tapentegra(Tap):
    """entegra tap class."""

    name = "tap-entegra"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "email",
            th.StringType(nullable=False),
            required=True,
            description="Your Entegra email for authentication",
        ),
        th.Property(
            "password",
            th.StringType(nullable=False),
            required=True,
            secret=True,  # Flag config as protected.
            description="Your Entegra password for authentication",
        ),
        th.Property(
            "api_url",
            th.StringType(nullable=False),
            default="https://apiv2.entegrabilisim.com",
            description="The base URL for the Entegra API",
        ),
        th.Property(
            "start_date",
            th.DateTimeType(nullable=True),
            description="The earliest record date to sync",
        ),
        th.Property(
            "page_size",
            th.IntegerType(nullable=True),
            default=100,
            description="Number of records to fetch per page",
        ),
        th.Property(
            "user_agent",
            th.StringType(nullable=True),
            description=(
                "A custom User-Agent header to send with each request. Default is "
                "'<tap_name>/<tap_version>'"
            ),
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.EntegraStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            # Core business data
            streams.ProductsStream(self),
            streams.OrdersStream(self),
            streams.CategoriesStream(self),
            streams.CustomersStream(self),
            
            # Master data
            streams.StoresStream(self),
            streams.BrandsStream(self),
            streams.PricesStream(self),
            
            # Marketplace settings
            streams.MarketplaceQuantitySettingsStream(self),
            streams.MarketplacePriceSettingsStream(self),
        ]


if __name__ == "__main__":
    Tapentegra.cli()
