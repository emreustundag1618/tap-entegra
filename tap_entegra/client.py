"""REST client handling, including EntegraStream base class."""

from __future__ import annotations

import decimal
import typing as t
from functools import cached_property

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator  # noqa: TC002
from singer_sdk.streams import RESTStream

from tap_entegra.auth import EntegraAuthenticator

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Auth, Context


class EntegraStream(RESTStream):
    """Entegra stream class."""

    # Most Entegra endpoints return data in a 'results' or similar array
    records_jsonpath = "$.results[*]"

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url"]

    @cached_property
    def authenticator(self) -> Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return EntegraAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        headers["Content-Type"] = "application/json"
        return headers

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance.

        Entegra API uses page-based pagination with ?page= parameter.

        Returns:
            A pagination helper instance.
        """
        return EntegraPaginator(start_value=1)

    def get_url_params(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        # Base implementation returns empty dict, streams can override to add params
        return {}
    
    def get_url(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: t.Any | None = None,  # noqa: ANN401
    ) -> str:
        """Get the full URL for this stream request.
        
        Entegra API uses path-based pagination like /product/page=1/
        Some endpoints have fixed paths with page=1 built in.
        Some endpoints are non-paginated and use direct paths.
        
        Args:
            context: The stream context.
            next_page_token: The next page index or value.
            
        Returns:
            The full URL for the request.
        """
        base_path = self.path
        
        # Check if this is a non-paginated endpoint
        if hasattr(self, 'is_paginated') and not self.is_paginated:
            return self.url_base + base_path
        
        # If path already contains 'page=', use it as-is (for categories, brands)
        if 'page=' in base_path:
            return self.url_base + base_path
        
        # For paginated endpoints, add page parameter
        page = next_page_token or 1
        paginated_path = f"{base_path}page={page}/"
        return self.url_base + paginated_path

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        json_response = response.json(parse_float=decimal.Decimal)
        
        # Handle Entegra API response structure - many endpoints return direct arrays
        if isinstance(json_response, list):
            # Direct array response (categories, brands, customers, etc.)
            yield from json_response
        elif "productList" in json_response:
            # Products endpoint returns {totalProduct: X, productList: [...]}
            yield from json_response["productList"]
        elif "orders" in json_response:
            # Orders endpoint returns {totalOrder: X, orders: [...]}
            yield from json_response["orders"]
        elif "categories" in json_response:
            # Categories endpoint returns {categories: [...]} (if wrapped)
            yield from json_response["categories"]
        elif "brands" in json_response:
            # Brands endpoint returns {brands: [...]} (if wrapped)
            yield from json_response["brands"]
        elif "customers" in json_response:
            # Customers endpoint returns {customers: [...]} (if wrapped)
            yield from json_response["customers"]
        elif "stores" in json_response:
            # Stores endpoint returns {stores: [...]}
            yield from json_response["stores"]
        elif "prices" in json_response:
            # Prices endpoint returns {prices: [...]}
            yield from json_response["prices"]
        elif "settings" in json_response:
            # Settings endpoints return {settings: [...]}
            yield from json_response["settings"]
        elif "results" in json_response:
            # Generic results field
            yield from json_response["results"]
        elif "data" in json_response:
            # Generic data field
            yield from json_response["data"]
        else:
            # Fallback: try to extract using jsonpath
            yield from extract_jsonpath(
                self.records_jsonpath,
                input=json_response,
            )

    def post_process(
        self,
        row: dict,
        context: Context | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        return row


class CategoriesPaginator(BaseAPIPaginator):
    """Special paginator for categories that stops after first page."""
    
    def __init__(self, start_value: int = 1, page_size: int = 100) -> None:
        """Initialize the paginator."""
        super().__init__(start_value)
        self.page_size = page_size
    
    def get_next(self, response: requests.Response) -> int | None:
        """Always return None to stop after first page since categories returns all data."""
        return None


class CustomersPaginator(BaseAPIPaginator):
    """Special paginator for customers that handles proper pagination."""
    
    def __init__(self, start_value: int = 1, page_size: int = 100) -> None:
        """Initialize the paginator."""
        super().__init__(start_value)
        self.page_size = page_size
    
    def get_next(self, response: requests.Response) -> int | None:
        """Get next page number or None if no more pages.
        
        Customers API returns {"customers": []} when there are no more records.
        """
        try:
            data = response.json()
            
            if "customers" in data:
                customers = data["customers"]
                # If we got an empty array, we're done
                if len(customers) == 0:
                    return None
                # If we got results, return next page number
                # The SDK will automatically update current_value
                return (self.current_value or 1) + 1
            else:
                # Fallback: no more pages
                return None
                
        except (ValueError, KeyError):
            return None


class EntegraPaginator(BaseAPIPaginator):
    """Paginator for Entegra API that uses page numbers."""

    def __init__(self, start_value: int = 1) -> None:
        """Initialize the paginator with a starting page number.
        
        Args:
            start_value: The starting page number (default is 1).
        """
        super().__init__(start_value)

    def get_next_url(self, response: requests.Response) -> str | None:
        """Get the next page URL from the API response.

        Args:
            response: The HTTP response object.

        Returns:
            The next page URL or None if no more pages.
        """
        try:
            data = response.json()
            
            # Check if there's a next page
            if "next" in data and data["next"]:
                return data["next"]
            
            # Check if we need to construct next page URL
            if "count" in data and "results" in data:
                current_page = self.current_value or 1
                total_count = data["count"]
                page_size = len(data["results"])
                
                if page_size > 0 and (current_page * page_size) < total_count:
                    return None  # Let get_next return the next page number
                    
        except (ValueError, KeyError):
            pass
            
        return None

    def get_next(self, response: requests.Response) -> int | None:
        """Get the next page token from the API response.

        Args:
            response: The HTTP response object.

        Returns:
            The next page number or None if no more pages.
        """
        try:
            data = response.json()
            current_page = self.current_value or 1
            
            # Handle Entegra API pagination based on actual response structure
            if isinstance(data, list):
                # Direct array response (like categories, brands)
                results = data
                # If we got no results, we're done
                if len(results) == 0:
                    return None
                # For most endpoints, if we get fewer than 20 results, we're done
                return None if len(results) < 20 else current_page + 1
            elif "productList" in data:
                # Products endpoint
                total_count = data.get("totalProduct", 0)
                results = data["productList"]
                page_size = len(results)
                
                if page_size > 0 and (current_page * page_size) < total_count:
                    return current_page + 1
            elif "orders" in data:
                # Orders endpoint
                total_count = data.get("totalOrder", 0)
                results = data["orders"]
                page_size = len(results)
                
                if page_size > 0 and (current_page * page_size) < total_count:
                    return current_page + 1
            elif "categories" in data:
                # Categories endpoint - wrapped in object
                results = data["categories"]
                return None if len(results) == 0 or len(results) < 20 else current_page + 1
            elif "brands" in data:
                # Brands endpoint - wrapped in object
                results = data["brands"]
                return None if len(results) == 0 or len(results) < 20 else current_page + 1
            elif "customers" in data:
                # Customers endpoint - wrapped in object
                results = data["customers"]
                # If we got fewer than expected results, assume we're done
                return None if len(results) < 20 else current_page + 1
            elif "stores" in data or "prices" in data or "settings" in data:
                # Non-paginated endpoints (stores, prices, settings) - always return None
                return None
            elif "next" in data and data["next"]:
                # If there's a next URL in the response, extract page number
                import re
                match = re.search(r'page=(\d+)', data["next"])
                if match:
                    return int(match.group(1))
            else:
                # Generic fallback
                results = data.get("results", [])
                if len(results) >= 20:  # Assume 20+ results means more pages
                    return current_page + 1
                    
        except (ValueError, KeyError):
            pass
            
        return None
