# tap-entegra

A Singer tap for extracting data from the Entegra API, built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Overview

This tap extracts data from the [Entegra API](https://apiv2.entegrabilisim.com) and produces JSON-formatted data following the Singer specification. It supports comprehensive data extraction from an e-commerce platform with the following streams:

### Available Streams

- **Categories** (29 records) - Product category hierarchy
- **Brands** (100 records) - Brand information
- **Stores** - Store locations and details
- **Marketplace Settings** - Quantity and price settings for marketplaces
- **Prices** (70 records) - Pricing configurations
- **Customers** - Customer information with pagination support
- **Products** - Complex product catalog with variations, images, and marketplace data
- **Orders** (1,100+ records) - Complete order information with customer details and line items

## Features

✅ **Comprehensive Data Extraction** - All major Entegra API endpoints supported  
✅ **Pagination Handling** - Automatic pagination for large datasets  
✅ **JWT Authentication** - Secure API authentication with token refresh  
✅ **ClickHouse Integration** - Direct loading to ClickHouse database  
✅ **Docker Support** - Containerized execution with Meltano  
✅ **Schema Validation** - Proper data type handling and validation  

## Installation

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/tap-entegra.git
cd tap-entegra

# Run with Meltano in Docker
docker run -v ${pwd}:/projects -w /projects meltano/meltano run tap-entegra target-clickhouse
```

### From Source

```bash
git clone https://github.com/yourusername/tap-entegra.git
cd tap-entegra
pip install -e .
```

## Configuration

The tap requires the following configuration parameters:

| Setting | Required | Type | Description |
|---------|----------|------|-------------|
| `email` | Yes | String | Your Entegra account email |
| `password` | Yes | String | Your Entegra account password |
| `api_url` | No | String | API base URL (default: `https://apiv2.entegrabilisim.com`) |
| `start_date` | No | Date | Earliest record date for incremental sync (ISO 8601 format) |
| `page_size` | No | Integer | Records per page (default: 100) |
| `user_agent` | No | String | Custom User-Agent header |

### Example Configuration

The project includes a pre-configured `meltano.yml` with test credentials:

```yaml
config:
  email: apitestv2@entegrabilisim.com
  password: apitestv2
  api_url: https://apiv2.entegrabilisim.com
  page_size: 100
  start_date: '2010-01-01T00:00:00Z'
```

## ClickHouse Integration

This tap includes pre-configured ClickHouse integration for direct data loading:

### ClickHouse Configuration

```yaml
loaders:
- name: target-clickhouse
  variant: shaped-ai
  config:
    host: host.docker.internal
    port: 8123
    username: default
    database: raw_dev
    engine_type: MergeTree
```

### Running the Pipeline

```bash
# Extract and load to ClickHouse
docker run -v ${pwd}:/projects -w /projects meltano/meltano run tap-entegra target-clickhouse

# Extract to JSON Lines format
docker run -v ${pwd}:/projects -w /projects meltano/meltano run tap-entegra target-jsonl
```

## Authentication

The tap uses JWT authentication with the Entegra API:

1. Authenticates using email/password to obtain JWT token
2. Uses "JWT {token}" format in Authorization header
3. Automatically refreshes tokens (default: 1-hour refresh cycle)
4. Tokens are valid for 90 days according to API documentation

## Stream Details

### Products Stream
- **Endpoint**: `/product/page={page}/`
- **Records**: 4,833 total products
- **Features**: Complex nested data with variations, images, and marketplace pricing
- **Pagination**: Custom implementation with page-based URLs

### Orders Stream  
- **Endpoint**: `/order/page={page}/`
- **Records**: 1,355 total orders
- **Features**: Complete order details with customer info, addresses, and line items
- **Performance**: ~1,100 records extracted in 21.96 seconds

### Customers Stream
- **Endpoint**: `/customer/page={page}/`
- **Features**: Customer information with pagination support
- **Pagination**: Stops when receiving empty `{"customers": []}` response

### Other Streams
- **Categories**: `/category/` - 29 categories, single page
- **Brands**: `/brand/` - 100 brands, single page  
- **Prices**: `/price/` - 70 price configurations, single page
- **Stores**: `/store/getStores` - Store information
- **Marketplace Settings**: Quantity and price settings for marketplaces

## Usage

### With Meltano (Docker)

```bash
# Discover streams
docker run -v ${pwd}:/projects -w /projects meltano/meltano invoke tap-entegra --discover

# Run full pipeline to ClickHouse
docker run -v ${pwd}:/projects -w /projects meltano/meltano run tap-entegra target-clickhouse

# Run specific streams only
# Edit meltano.yml select configuration and run again
```

### Direct Usage

```bash
# Discovery
tap-entegra --config config.json --discover

# Extract data
tap-entegra --config config.json --catalog catalog.json
```

## API Limits

Be aware of Entegra API limitations:

- **Daily Limit**: 20,000 requests per day
- **Token Expiry**: 90 days
- **Rate Limiting**: Implement appropriate delays if needed

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/tap-entegra.git
cd tap-entegra
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
ruff format .
ruff check . --fix
```

## Troubleshooting

### Common Issues

1. **Pagination Loops**: Fixed with custom `request_records` methods
2. **Schema Mismatches**: All fields configured as `StringType` for ClickHouse compatibility
3. **Authentication**: JWT tokens automatically refreshed every hour

### Docker Issues

```bash
# If ClickHouse connection fails, ensure ClickHouse is running:
docker run -d --name clickhouse-server -p 8123:8123 clickhouse/clickhouse-server

# Check container logs:
docker logs clickhouse-server
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

1. Check the [GitHub Issues](https://github.com/yourusername/tap-entegra/issues)
2. Review the [Entegra API Documentation](ENTEGRA_API_DOCUMENTATION.md)
3. Consult the [Meltano Singer SDK Documentation](https://sdk.meltano.com)
