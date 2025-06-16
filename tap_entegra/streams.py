"""Stream type classes for tap-entegra."""

from __future__ import annotations

import typing as t
from importlib import resources
from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_entegra.client import EntegraStream, CategoriesPaginator, CustomersPaginator

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = resources.files(__package__) / "schemas"


class ProductsStream(EntegraStream):
    """Products stream for Entegra API."""

    name = "products"
    path = "/product/"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None  # Disable incremental replication - use full table sync
    records_jsonpath = "$.productList[*]"
    
    # Removed manual request_records to use SDK's built-in incremental logic

    schema = th.PropertiesList(
        # Basic product info
        th.Property("id", th.StringType, description="Product ID"),  # API returns as string
        th.Property("productCode", th.StringType, description="Product code/SKU"),
        th.Property("name", th.StringType, description="Product name"),  # Field name is 'name', not 'productName'
        th.Property("status", th.StringType, description="Product status (0=inactive, 1=active)"),
        th.Property("description", th.StringType, description="Product description"),
        th.Property("product_type", th.StringType, description="Product type"),
        th.Property("barcode", th.StringType, description="Product barcode"),
        th.Property("gtin", th.StringType, description="GTIN code"),
        th.Property("send_api", th.StringType, description="Send API flag"),
        th.Property("brand", th.StringType, description="Product brand"),
        th.Property("group", th.StringType, description="Product category ID"),
        
        # Inventory
        th.Property("quantity", th.StringType, description="Product quantity"),
        th.Property("quantity2", th.StringType, description="Secondary quantity"),
        th.Property("quantity2_enable", th.StringType, description="Secondary quantity enabled"),
        
        # Pricing
        th.Property("currencyType", th.StringType, description="Currency type"),
        th.Property("kdv_id", th.StringType, description="VAT rate ID"),
        th.Property("price1", th.StringType, description="Price 1"),
        th.Property("price2", th.StringType, description="Price 2"),
        th.Property("price3", th.StringType, description="Price 3"),
        th.Property("price4", th.StringType, description="Price 4"),
        th.Property("price5", th.StringType, description="Price 5"),
        th.Property("price6", th.StringType, description="Price 6"),
        th.Property("price7", th.StringType, description="Price 7"),
        th.Property("price8", th.StringType, description="Price 8"),
        th.Property("amazon_price", th.StringType, description="Amazon price"),
        th.Property("amazon_salePrice", th.StringType, description="Amazon sale price"),
        th.Property("buying_price", th.StringType, description="Buying price"),
        
        # Supplier and dates
        th.Property("supplier", th.StringType, description="Supplier name"),
        th.Property("date_change", th.StringType, description="Last modification date"),
        th.Property("date_add", th.StringType, description="Date added"),
        
        # Additional fields
        th.Property("hb_sku", th.StringType, description="Hepsiburada SKU"),
        th.Property("mpn", th.StringType, description="Manufacturer part number"),
        th.Property("desi", th.StringType, description="Desi value"),
        th.Property("height", th.StringType, description="Height"),
        th.Property("width", th.StringType, description="Width"),
        th.Property("weight", th.StringType, description="Weight"),
        th.Property("depth", th.StringType, description="Depth"),
        th.Property("miad", th.StringType, description="Expiration date"),
        th.Property("critical_stock_enable", th.StringType, description="Critical stock enabled"),
        th.Property("critical_stock", th.StringType, description="Critical stock level"),
        th.Property("alan1", th.StringType, description="Custom field 1"),
        th.Property("alan2", th.StringType, description="Custom field 2"),
        th.Property("alan3", th.StringType, description="Custom field 3"),
        th.Property("alan4", th.StringType, description="Custom field 4"),
        th.Property("alan5", th.StringType, description="Custom field 5"),
        
        # Variations array
        th.Property(
            "variatios",  # Note: API uses "variatios" (typo in API)
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType, description="Variation ID"),
                    th.Property("productCode", th.StringType, description="Variation product code"),
                    th.Property("barcode", th.StringType, description="Variation barcode"),
                    th.Property("gtin", th.StringType, description="Variation GTIN"),
                    th.Property("quantity", th.StringType, description="Variation quantity"),
                    th.Property("quantity2", th.StringType, description="Variation secondary quantity"),
                    th.Property("price", th.StringType, description="Variation price"),
                    th.Property("hb_st_sku", th.StringType, description="HB store SKU"),
                    th.Property("hb_sku", th.StringType, description="HB SKU"),
                    th.Property("desi", th.StringType, description="Variation desi"),
                    th.Property("height", th.StringType, description="Variation height"),
                    th.Property("width", th.StringType, description="Variation width"),
                    th.Property("weight", th.StringType, description="Variation weight"),
                    th.Property("depth", th.StringType, description="Variation depth"),
                    th.Property("price1", th.StringType, description="Variation price 1"),
                    th.Property("price2", th.StringType, description="Variation price 2"),
                    th.Property("price3", th.StringType, description="Variation price 3"),
                    th.Property("price4", th.StringType, description="Variation price 4"),
                    th.Property("price5", th.StringType, description="Variation price 5"),
                    th.Property("price6", th.StringType, description="Variation price 6"),
                    th.Property("price7", th.StringType, description="Variation price 7"),
                    th.Property("price8", th.StringType, description="Variation price 8"),
                    th.Property("amazon_price", th.StringType, description="Variation Amazon price"),
                    th.Property("amazon_salePrice", th.StringType, description="Variation Amazon sale price"),
                    th.Property("buying_price", th.StringType, description="Variation buying price"),
                    th.Property("itemdim1code", th.StringType, description="Item dimension 1 code"),
                    th.Property("itemdim2code", th.StringType, description="Item dimension 2 code"),
                    th.Property(
                        "variationSpec",
                        th.ArrayType(
                            th.ObjectType(
                                th.Property("name", th.StringType, description="Spec name"),
                                th.Property("value", th.StringType, description="Spec value"),
                            )
                        ),
                        description="Variation specifications",
                    ),
                    th.Property(
                        "variation_pictures",
                        th.ArrayType(th.ObjectType()),
                        description="Variation pictures",
                    ),
                )
            ),
            description="Product variations",
        ),
        
        # Pictures array
        th.Property(
            "pictures",
            th.ArrayType(
                th.ObjectType(
                    th.Property("picture", th.StringType, description="Picture URL"),
                )
            ),
            description="Product pictures",
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return URL parameters for the request."""
        params = super().get_url_params(context, next_page_token)
        return params


class OrdersStream(EntegraStream):
    """Orders stream for Entegra API with date-range chunking for large datasets."""

    name = "orders"
    path = "/order/"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None  # Use full table sync with date chunking
    records_jsonpath = "$.orders[*]"
    
    def request_records(self, context: dict | None) -> t.Iterable[dict]:
        """Request records using date-range chunking for better performance with large datasets."""
        import requests
        from datetime import datetime, timedelta
        
        # Get start date from config
        start_date_config = self.config.get("start_date")
        if not start_date_config:
            self.logger.error("start_date is required for orders sync")
            return
            
        # Parse start date and ensure timezone-naive
        if hasattr(start_date_config, 'strftime'):
            start_date = start_date_config
            # Remove timezone info if present
            if start_date.tzinfo is not None:
                start_date = start_date.replace(tzinfo=None)
        else:
            try:
                if isinstance(start_date_config, str):
                    if 'T' in start_date_config:
                        # Parse ISO format and remove timezone
                        start_date = datetime.fromisoformat(start_date_config.replace('Z', '+00:00'))
                        start_date = start_date.replace(tzinfo=None)
                    else:
                        start_date = datetime.strptime(start_date_config, '%Y-%m-%d')
                else:
                    start_date = datetime.now() - timedelta(days=365)  # Default to 1 year ago
            except (ValueError, TypeError):
                start_date = datetime.now() - timedelta(days=365)  # Default to 1 year ago
        
        # Current date as end date (timezone-naive)
        end_date = datetime.now()
        
        # Define chunk size (days) from config
        chunk_days = self.config.get("date_chunk_size", 30)  # Default to 30 days
        
        current_date = start_date
        total_records = 0
        
        self.logger.info(f"Starting date-chunked sync from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        while current_date < end_date:
            # Calculate chunk end date
            chunk_end = min(current_date + timedelta(days=chunk_days), end_date)
            
            # Format dates for API
            start_date_str = current_date.strftime('%Y-%m-%d')
            end_date_str = chunk_end.strftime('%Y-%m-%d')
            
            self.logger.info(f"Processing chunk: {start_date_str} to {end_date_str}")
            
            # Fetch orders for this date range
            chunk_records = 0
            page = 1
            
            while True:
                # Construct URL with date parameters
                url = f"{self.url_base}{self.path}page={page}/"
                
                # Parameters for this chunk
                params = {
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "limit": self.config.get("page_size", 100)
                }
                
                # Make request
                headers = self.http_headers
                auth = self.authenticator
                
                try:
                    response = requests.get(url, headers=headers, auth=auth, params=params, verify=False)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if "orders" in data and len(data["orders"]) > 0:
                        orders = data["orders"]
                        chunk_records += len(orders)
                        
                        # Yield all orders from this page
                        yield from orders
                        
                        # Check if we got less than page size (last page)
                        if len(orders) < params["limit"]:
                            break
                            
                        page += 1
                    else:
                        # No more orders in this chunk
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error fetching chunk {start_date_str} to {end_date_str}, page {page}: {e}")
                    break
            
            total_records += chunk_records
            self.logger.info(f"Chunk {start_date_str} to {end_date_str}: {chunk_records} records")
            
            # Move to next chunk
            current_date = chunk_end + timedelta(days=1)
        
        self.logger.info(f"Date-chunked sync completed. Total records: {total_records}")

    schema = th.PropertiesList(
        # Basic order info
        th.Property("id", th.StringType, description="Order ID"),
        th.Property("no", th.StringType, description="Order number"),
        th.Property("datetime", th.StringType, description="Order datetime"),
        th.Property("entegration", th.StringType, description="Integration source"),
        th.Property("status", th.StringType, description="Order status"),
        th.Property("customer_id", th.StringType, description="Customer ID"),
        
        # Customer info
        th.Property("company", th.StringType, description="Company name"),
        th.Property("firstname", th.StringType, description="Customer first name"),
        th.Property("lastname", th.StringType, description="Customer last name"),
        th.Property("email", th.StringType, description="Customer email"),
        th.Property("mobil_phone", th.StringType, description="Customer mobile phone"),
        th.Property("telephone", th.StringType, description="Customer telephone"),
        th.Property("fax", th.StringType, description="Customer fax"),
        th.Property("username", th.StringType, description="Customer username"),
        
        # Invoice address
        th.Property("invoice_address", th.StringType, description="Invoice address"),
        th.Property("invoice_city", th.StringType, description="Invoice city"),
        th.Property("invoice_district", th.StringType, description="Invoice district"),
        th.Property("invoice_fullname", th.StringType, description="Invoice full name"),
        th.Property("invoice_postcode", th.StringType, description="Invoice postal code"),
        th.Property("invoice_tel", th.StringType, description="Invoice telephone"),
        th.Property("invoice_gsm", th.StringType, description="Invoice mobile phone"),
        th.Property("invoice_country", th.StringType, description="Invoice country"),
        th.Property("invoice_country_code", th.StringType, description="Invoice country code"),
        th.Property("invoice_date", th.StringType, description="Invoice date"),
        th.Property("invoice_number", th.StringType, description="Invoice number"),
        th.Property("invoice_print", th.StringType, description="Invoice print status"),
        th.Property("invoice_type", th.StringType, description="Invoice type"),
        th.Property("invoice_url", th.StringType, description="Invoice URL"),
        
        # Shipping address
        th.Property("ship_address", th.StringType, description="Shipping address"),
        th.Property("ship_city", th.StringType, description="Shipping city"),
        th.Property("ship_district", th.StringType, description="Shipping district"),
        th.Property("ship_fullname", th.StringType, description="Shipping full name"),
        th.Property("ship_postcode", th.StringType, description="Shipping postal code"),
        th.Property("ship_tel", th.StringType, description="Shipping telephone"),
        th.Property("ship_gsm", th.StringType, description="Shipping mobile phone"),
        th.Property("ship_country", th.StringType, description="Shipping country"),
        th.Property("ship_country_code", th.StringType, description="Shipping country code"),
        th.Property("ship_date", th.StringType, description="Ship date"),
        th.Property("ship_number", th.StringType, description="Ship number"),
        th.Property("ship_print", th.StringType, description="Ship print status"),
        th.Property("ship_price", th.StringType, description="Shipping price"),
        
        # Financial info
        th.Property("total", th.StringType, description="Order total"),
        th.Property("discount", th.StringType, description="Order discount"),
        th.Property("grand_total", th.StringType, description="Grand total"),
        th.Property("tax", th.StringType, description="Tax amount"),
        th.Property("currencyType", th.StringType, description="Currency type"),
        th.Property("currency_rate", th.StringType, description="Currency rate"),
        th.Property("eur_rate", th.StringType, description="EUR rate"),
        th.Property("usd_rate", th.StringType, description="USD rate"),
        th.Property("coupon_price", th.StringType, description="Coupon price"),
        th.Property("total_paid_price", th.StringType, description="Total paid price"),
        th.Property("payment_status", th.StringType, description="Payment status"),
        th.Property("paymentType", th.StringType, description="Payment type"),
        th.Property("bank_code", th.StringType, description="Bank code"),
        th.Property("installment", th.StringType, description="Installment count"),
        
        # Tax info
        th.Property("tc_id", th.StringType, description="TC ID"),
        th.Property("tax_office", th.StringType, description="Tax office"),
        th.Property("tax_number", th.StringType, description="Tax number"),
        
        # Cargo info
        th.Property("cargo_code", th.StringType, description="Cargo tracking code"),
        th.Property("cargo_code2", th.StringType, description="Secondary cargo code"),
        th.Property("cargo_company", th.StringType, description="Cargo company"),
        th.Property("cargo_fee_type", th.StringType, description="Cargo fee type"),
        th.Property("cargo_follow_url", th.StringType, description="Cargo follow URL"),
        th.Property("cargo_finally_statu", th.StringType, description="Cargo final status"),
        th.Property("cargo_send_date", th.StringType, description="Cargo send date"),
        th.Property("cargo_barcode_raw", th.StringType, description="Cargo barcode raw"),
        th.Property("cargo_packet_quantity", th.StringType, description="Cargo packet quantity"),
        th.Property("cargo_error_message", th.StringType, description="Cargo error message"),
        th.Property("cargo_sync", th.StringType, description="Cargo sync status"),
        th.Property("cargo_cancel_sync", th.StringType, description="Cargo cancel sync"),
        th.Property("cargo_service_information", th.StringType, description="Cargo service info"),
        th.Property("cargo_delivery_status_sync", th.StringType, description="Cargo delivery status sync"),
        th.Property("cargo_packet_type", th.StringType, description="Cargo packet type"),
        th.Property("cargo_auto_sync", th.StringType, description="Cargo auto sync"),
        th.Property("cargo_store_code", th.StringType, description="Cargo store code"),
        th.Property("cargoDeliveryDueDate", th.StringType, description="Cargo delivery due date"),
        
        # Supplier info
        th.Property("supplier", th.StringType, description="Supplier name"),
        th.Property("supplier_id", th.StringType, description="Supplier ID"),
        th.Property("supplier_order_id", th.StringType, description="Supplier order ID"),
        th.Property("supplier_packet_id", th.StringType, description="Supplier packet ID"),
        
        # System fields
        th.Property("sync", th.StringType, description="Sync status"),
        th.Property("order_number", th.StringType, description="Order number"),
        th.Property("order_prefix", th.StringType, description="Order prefix"),
        th.Property("delivery_method", th.StringType, description="Delivery method"),
        th.Property("guid", th.StringType, description="GUID"),
        th.Property("customer_code", th.StringType, description="Customer code"),
        th.Property("store_order_status", th.StringType, description="Store order status"),
        th.Property("store_order_status_name", th.StringType, description="Store order status name"),
        th.Property("marketing_sync", th.StringType, description="Marketing sync"),
        th.Property("tracking_number_sync", th.StringType, description="Tracking number sync"),
        th.Property("gib_number", th.StringType, description="GIB number"),
        th.Property("morhipo_order_statu", th.StringType, description="Morhipo order status"),
        th.Property("date_add", th.StringType, description="Date added"),
        th.Property("date_change", th.StringType, description="Date changed"),
        
        # ERP fields
        th.Property("erp_order_number", th.StringType, description="ERP order number"),
        th.Property("erp_error", th.StringType, description="ERP error"),
        th.Property("erp_message", th.StringType, description="ERP message"),
        th.Property("erp_cargo_info_sync", th.StringType, description="ERP cargo info sync"),
        th.Property("erp_serial_sync", th.StringType, description="ERP serial sync"),
        th.Property("erp_cancel_sync", th.StringType, description="ERP cancel sync"),
        
        # Fulfillment fields
        th.Property("fulfillment", th.StringType, description="Fulfillment"),
        th.Property("fulfillment_sync", th.StringType, description="Fulfillment sync"),
        th.Property("fulfillment_code", th.StringType, description="Fulfillment code"),
        th.Property("fulfillment_error_message", th.StringType, description="Fulfillment error message"),
        th.Property("is_fulfillment", th.StringType, description="Is fulfillment"),
        th.Property("platform_reference_no", th.StringType, description="Platform reference number"),
        th.Property("is_partial", th.StringType, description="Is partial"),
        
        # Additional fields
        th.Property("total_commission_include_tax", th.StringType, description="Total commission include tax"),
        th.Property("grand_total_desi", th.StringType, description="Grand total desi"),
        th.Property("einvoice_error_message", th.StringType, description="E-invoice error message"),
        th.Property("hb_discount_invoice", th.StringType, description="HB discount invoice"),
        th.Property("mut_odeme", th.StringType, description="Mut odeme"),
        th.Property("mut_kargo", th.StringType, description="Mut kargo"),
        th.Property("mut_iptal", th.StringType, description="Mut iptal"),
        th.Property("total_product", th.StringType, description="Total product"),
        th.Property("total_product_quantity", th.StringType, description="Total product quantity"),
        th.Property("mut_hizmet", th.StringType, description="Mut hizmet"),
        th.Property("delivered_person_name", th.StringType, description="Delivered person name"),
        th.Property("delivered_date", th.StringType, description="Delivered date"),
        th.Property("shop_id", th.StringType, description="Shop ID"),
        th.Property("store_id", th.StringType, description="Store ID"),
        th.Property("preparation_time", th.StringType, description="Preparation time"),
        th.Property("preparation_state_sync", th.StringType, description="Preparation state sync"),
        th.Property("efatura_sync", th.StringType, description="E-fatura sync"),
        th.Property("platform_serial_sync", th.StringType, description="Platform serial sync"),
        th.Property("api_sync", th.StringType, description="API sync"),
        th.Property("scanned_date", th.StringType, description="Scanned date"),
        th.Property("hb_bnpl", th.StringType, description="HB BNPL"),
        th.Property("scanned_user", th.StringType, description="Scanned user"),
        th.Property("easyShip_sync", th.StringType, description="EasyShip sync"),
        th.Property("easyShip_error_message", th.StringType, description="EasyShip error message"),
        th.Property("send_invoice_url_sync", th.StringType, description="Send invoice URL sync"),
        th.Property("send_invoice_url_error_message", th.StringType, description="Send invoice URL error message"),
        th.Property("sync_ai", th.StringType, description="Sync AI"),
        th.Property("micro_export_order", th.StringType, description="Micro export order"),
        th.Property("delivery_terms", th.StringType, description="Delivery terms"),
        th.Property("commercial", th.StringType, description="Commercial"),
        th.Property("VendorApproveTransactionId", th.StringType, description="Vendor approve transaction ID"),
        th.Property("printed_user", th.StringType, description="Printed user"),
        th.Property("amazon_vendor_orderStatus", th.StringType, description="Amazon vendor order status"),
        th.Property("VendorSubmitShipmentTransactionId", th.StringType, description="Vendor submit shipment transaction ID"),
        th.Property("VendorShipLabelTransactionId", th.StringType, description="Vendor ship label transaction ID"),
        th.Property("ettn", th.StringType, description="ETTN"),
        th.Property("send_efatura", th.StringType, description="Send e-fatura"),
        th.Property("create_common_label_sync", th.StringType, description="Create common label sync"),
        th.Property("order_process", th.StringType, description="Order process"),
        th.Property("note", th.StringType, description="Note"),
        
        # Order products array
        th.Property(
            "order_product",
            th.ArrayType(
                th.ObjectType(
                    th.Property("order_product_id", th.StringType, description="Order product ID"),
                    th.Property("order_id", th.StringType, description="Order ID"),
                    th.Property("product_id", th.StringType, description="Product ID"),
                    th.Property("name", th.StringType, description="Product name"),
                    th.Property("picture", th.StringType, description="Product picture"),
                    th.Property("model", th.StringType, description="Product model"),
                    th.Property("quantity", th.StringType, description="Quantity"),
                    th.Property("price", th.StringType, description="Price"),
                    th.Property("total", th.StringType, description="Total"),
                    th.Property("tax", th.StringType, description="Tax"),
                    th.Property("sellerdiscount", th.StringType, description="Seller discount"),
                    th.Property("malldiscount", th.StringType, description="Mall discount"),
                    th.Property("sellerinvoiceamount", th.StringType, description="Seller invoice amount"),
                    th.Property("dueamount", th.StringType, description="Due amount"),
                    th.Property("commission", th.StringType, description="Commission"),
                    th.Property("status", th.StringType, description="Status"),
                    th.Property("tax_id", th.StringType, description="Tax ID"),
                    th.Property("store_stock_code", th.StringType, description="Store stock code"),
                    th.Property("store_stock_name", th.StringType, description="Store stock name"),
                    th.Property("store_order_status", th.StringType, description="Store order status"),
                    th.Property("store_order_status_name", th.StringType, description="Store order status name"),
                    th.Property("quantity_decrease", th.StringType, description="Quantity decrease"),
                    th.Property("pricex", th.StringType, description="Price X"),
                    th.Property("currencyType", th.StringType, description="Currency type"),
                    th.Property("priceIncludedTax", th.StringType, description="Price included tax"),
                    th.Property("product_option_value_id", th.StringType, description="Product option value ID"),
                    th.Property("product_option_name", th.StringType, description="Product option name"),
                    th.Property("product_option_value_name", th.StringType, description="Product option value name"),
                    th.Property("invoice_name", th.StringType, description="Invoice name"),
                    th.Property("store_stock_id", th.StringType, description="Store stock ID"),
                    th.Property("ShippingType", th.StringType, description="Shipping type"),
                    th.Property("ShipmentProvider", th.StringType, description="Shipment provider"),
                    th.Property("TrackingCode", th.StringType, description="Tracking code"),
                    th.Property("pov_productCode", th.StringType, description="POV product code"),
                    th.Property("store_stock_varcode", th.StringType, description="Store stock var code"),
                    th.Property("barcode", th.StringType, description="Barcode"),
                    th.Property("product_type", th.StringType, description="Product type"),
                    th.Property("product_supplier", th.StringType, description="Product supplier"),
                    th.Property("packet_id", th.StringType, description="Packet ID"),
                    th.Property("packet_code", th.StringType, description="Packet code"),
                    th.Property("packet_price", th.StringType, description="Packet price"),
                    th.Property("packet_tax_id", th.StringType, description="Packet tax ID"),
                    th.Property("packet_quantity", th.StringType, description="Packet quantity"),
                    th.Property("note", th.StringType, description="Note"),
                    th.Property("supplier", th.StringType, description="Supplier"),
                    th.Property("supplier_id", th.StringType, description="Supplier ID"),
                    th.Property("commission_rate", th.StringType, description="Commission rate"),
                    th.Property("discount_rate", th.StringType, description="Discount rate"),
                    th.Property("first_price", th.StringType, description="First price"),
                    th.Property("is_fulfillment", th.StringType, description="Is fulfillment"),
                    th.Property("platform_reference_no", th.StringType, description="Platform reference no"),
                    th.Property("total_desi", th.StringType, description="Total desi"),
                    th.Property("total_cargo_packet_amount", th.StringType, description="Total cargo packet amount"),
                    th.Property("buying_price", th.StringType, description="Buying price"),
                    th.Property("scanned", th.StringType, description="Scanned"),
                    th.Property("manual_scanned", th.StringType, description="Manual scanned"),
                    th.Property("shop_id", th.StringType, description="Shop ID"),
                    th.Property("store_id", th.StringType, description="Store ID"),
                    th.Property("who_scanned", th.StringType, description="Who scanned"),
                    th.Property("sync_ai", th.StringType, description="Sync AI"),
                    th.Property("width", th.StringType, description="Width"),
                    th.Property("height", th.StringType, description="Height"),
                    th.Property("depth", th.StringType, description="Depth"),
                    th.Property("weight", th.StringType, description="Weight"),
                    th.Property("gtip", th.StringType, description="GTIP"),
                    th.Property("erp_code", th.StringType, description="ERP code"),
                    th.Property("origin", th.StringType, description="Origin"),
                    th.Property(
                        "variation_values",
                        th.ArrayType(th.ObjectType()),
                        description="Variation values",
                    ),
                )
            ),
            description="Order products",
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return URL parameters for the request."""
        params = super().get_url_params(context, next_page_token)
        
        # Full table replication: Always fetch all orders from start_date to current date
        # This ensures we get ALL orders every time, replacing the entire table
        if self.config.get("start_date"):
            start_date = self.config["start_date"]
            if hasattr(start_date, 'strftime'):
                start_date_str = start_date.strftime('%Y-%m-%d')
            else:
                # Handle ISO string format
                from datetime import datetime
                if isinstance(start_date, str):
                    try:
                        parsed_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        start_date_str = parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        start_date_str = start_date
                else:
                    start_date_str = str(start_date)
            
            params["start_date"] = start_date_str
            
            # Always add end_date as current date
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            params["end_date"] = current_date
            
        return params

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        """Process the record after extraction."""
        # No filtering needed for full table replication - return all records
        return row


class CategoriesStream(EntegraStream):
    """Categories stream for Entegra API."""

    name = "categories" 
    path = "/category/page=1/"  # Categories endpoint requires page=1 but returns all data
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    records_jsonpath = "$[*]"  # API returns array directly, not wrapped in "categories"
    
    def get_new_paginator(self) -> CategoriesPaginator:
        """Return a paginator that stops after first page since categories returns all data at once."""
        return CategoriesPaginator(start_value=1, page_size=100)

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Category ID"),  # API returns as string
        th.Property("name", th.StringType, description="Category name"),
        th.Property("parent_id", th.StringType, description="Parent category ID"),  # API returns as string
        th.Property("description", th.StringType, description="Category description"),
        th.Property("sort_order", th.StringType, description="Sort order"),  # API returns as string
        th.Property("status", th.StringType, description="Category status"),  # API returns as string
        th.Property("date_added", th.StringType, description="Date added"),  # API returns as string
        th.Property("date_modified", th.StringType, description="Date modified"),  # API returns as string
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return URL parameters for the request."""
        params = super().get_url_params(context, next_page_token)
        return params


class StoresStream(EntegraStream):
    """Stores stream for Entegra API."""

    name = "stores"
    path = "/store/getStores"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    records_jsonpath = "$.stores[*]"
    
    # This is a non-paginated endpoint
    is_paginated = False

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Store ID"),  # API returns as string
        th.Property("name", th.StringType, description="Store name"),
        th.Property("status", th.StringType, description="Store status"),  # API returns as string
    ).to_dict()


class BrandsStream(EntegraStream):
    """Brands stream for Entegra API."""

    name = "brands"
    path = "/product/brand/page=1/"  # Brands endpoint requires page=1 but returns all data
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    records_jsonpath = "$.brand[*]"  # API returns data wrapped in "brand" array
    
    def get_new_paginator(self) -> CategoriesPaginator:
        """Return a paginator that stops after first page since brands returns all data at once."""
        return CategoriesPaginator(start_value=1, page_size=100)

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Brand ID"),  # API returns as string
        th.Property("name", th.StringType, description="Brand name"),
        th.Property("sync", th.StringType, description="Sync status flag"),
        th.Property("status", th.StringType, description="Brand status"),
    ).to_dict()


class CustomersStream(EntegraStream):
    """Customers stream for Entegra API."""

    name = "customers"
    path = "/customer/"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None  # No date_change field in actual response
    records_jsonpath = "$.customers[*]"  # API returns data wrapped in "customers" array
    
    def request_records(self, context: dict | None) -> t.Iterable[dict]:
        """Request records from paginated endpoint, stopping when empty response."""
        import requests
        
        page = 1
        while True:
            # Construct URL for current page
            url = f"{self.url_base}{self.path}page={page}/"
            
            # Create request manually
            headers = self.http_headers
            auth = self.authenticator
            
            response = requests.get(url, headers=headers, auth=auth, verify=False)
            response.raise_for_status()
            
            # Parse response
            try:
                data = response.json()
                if "customers" in data:
                    customers = data["customers"]
                    if len(customers) == 0:
                        # Empty response means no more pages
                        break
                    # Yield all customers from this page
                    yield from customers
                    page += 1
                else:
                    # No customers key, stop
                    break
            except (ValueError, KeyError):
                # Invalid response, stop
                break

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Customer ID"),  # API returns as string
        th.Property("code", th.StringType, description="Customer code"),
        th.Property("company", th.StringType, description="Company name"),
        th.Property("firstname", th.StringType, description="First name"),
        th.Property("lastname", th.StringType, description="Last name"),
        th.Property("email", th.StringType, description="Email address"),
        th.Property("username", th.StringType, description="Username"),
        th.Property("mobil_phone", th.StringType, description="Mobile phone"),
        th.Property("telephone", th.StringType, description="Telephone"),
        th.Property("fax", th.StringType, description="Fax number"),
        
        # Invoice address fields
        th.Property("invoice_fullname", th.StringType, description="Invoice full name"),
        th.Property("invoice_address", th.StringType, description="Invoice address"),
        th.Property("invoice_city", th.StringType, description="Invoice city"),
        th.Property("invoice_district", th.StringType, description="Invoice district"),
        th.Property("invoice_postcode", th.StringType, description="Invoice postal code"),
        th.Property("invoice_tel", th.StringType, description="Invoice telephone"),
        th.Property("invoice_gsm", th.StringType, description="Invoice mobile phone"),
        th.Property("invoice_country", th.StringType, description="Invoice country"),
        th.Property("invoice_country_code", th.StringType, description="Invoice country code"),
        th.Property("invoice_type", th.StringType, description="Invoice type"),
        
        # Shipping address fields
        th.Property("ship_fullname", th.StringType, description="Shipping full name"),
        th.Property("ship_address", th.StringType, description="Shipping address"),
        th.Property("ship_city", th.StringType, description="Shipping city"),
        th.Property("ship_district", th.StringType, description="Shipping district"),
        th.Property("ship_postcode", th.StringType, description="Shipping postal code"),
        th.Property("ship_tel", th.StringType, description="Shipping telephone"),
        th.Property("ship_gsm", th.StringType, description="Shipping mobile phone"),
        th.Property("ship_country", th.StringType, description="Shipping country"),
        th.Property("ship_country_code", th.StringType, description="Shipping country code"),
        
        # Tax and business fields
        th.Property("tc_id", th.StringType, description="Turkish ID number"),
        th.Property("tax_office", th.StringType, description="Tax office"),
        th.Property("tax_number", th.StringType, description="Tax number"),
        
        # Additional fields
        th.Property("date_add", th.StringType, description="Date added"),
        th.Property("date_change", th.StringType, description="Date changed"),
        th.Property("supplier", th.StringType, description="Supplier name"),
        th.Property("supplier_id", th.StringType, description="Supplier ID"),
        th.Property("location", th.StringType, description="Location"),
        th.Property("customerType", th.StringType, description="Customer type"),
        th.Property("erp_code", th.StringType, description="ERP code"),
    ).to_dict()


class PricesStream(EntegraStream):
    """Prices stream for Entegra API."""

    name = "prices"
    path = "/price/getPrices"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None  # No date_modified field in actual response
    records_jsonpath = "$.prices[*]"
    
    # This is a non-paginated endpoint
    is_paginated = False

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Price ID"),  # API returns as string
        th.Property("name", th.StringType, description="Price name"),
        th.Property("code", th.StringType, description="Price code"),
        th.Property("default_xml_rate", th.StringType, description="Default XML rate formula"),
        th.Property("visibility", th.StringType, description="Price visibility flag"),
        th.Property("currencyType", th.StringType, description="Currency type"),
        th.Property("sort_order", th.StringType, description="Sort order"),
        th.Property("smart_price_enable", th.StringType, description="Smart price enabled flag"),
        th.Property("smart_critical_price_calculation_enable", th.StringType, description="Smart critical price calculation enabled flag"),
    ).to_dict()


class MarketplaceQuantitySettingsStream(EntegraStream):
    """Marketplace quantity settings stream for Entegra API."""

    name = "marketplace_quantity_settings"
    path = "/store/getMarketplaceQuantitySettings"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None  # No date_modified field in actual response
    records_jsonpath = "$.MarketplaceQuantitySettings[*]"  # Fixed JSONPath
    
    # This is a non-paginated endpoint
    is_paginated = False

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Setting ID"),  # API returns as string
        th.Property("supplier", th.StringType, description="Supplier name"),
        th.Property("product_store_id", th.StringType, description="Product store ID"),
        th.Property("order_store_id", th.StringType, description="Order store ID"),  
        th.Property("critical_stock_enable", th.StringType, description="Critical stock enabled flag"),
        th.Property("critical_stock", th.StringType, description="Critical stock level"),
        th.Property("quantity2_enable", th.StringType, description="Quantity 2 enabled flag"),
    ).to_dict()


class MarketplacePriceSettingsStream(EntegraStream):
    """Marketplace price settings stream for Entegra API."""

    name = "marketplace_price_settings"
    path = "/price/getMarketplacePriceSettings"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None  # No date_modified field in actual response
    records_jsonpath = "$.MarketplacePriceSettings[*]"  # Fixed JSONPath
    
    # This is a non-paginated endpoint
    is_paginated = False

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Setting ID"),  # API returns as string
        th.Property("supplier", th.StringType, description="Supplier name"),
        th.Property("listPrice_name", th.StringType, description="List price name"),
        th.Property("salePrice_name", th.StringType, description="Sale price name"),
        th.Property("store_id", th.StringType, description="Store ID"),
        th.Property("povSalePrice_name", th.StringType, description="POV sale price name"),
    ).to_dict()
