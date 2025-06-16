# tap-entegra

`tap-entegra` is a Singer tap for extracting data from the Entegra API.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from PyPi:

```bash
pipx install tap-entegra
```

Install from GitHub:

```bash
pipx install git+https://github.com/emreustundag/tap-entegra.git@main
```

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| email | True | None | Your Entegra email for authentication |
| password | True | None | Your Entegra password for authentication |
| api_url | True | https://apiv2.entegrabilisim.com | The base URL for the Entegra API |
| start_date | True | None | The earliest record date to sync (ISO format) |
| page_size | False | 100 | Number of records to fetch per page |
| date_chunk_size | False | 30 | Number of days to process in each chunk for large datasets |
| user_agent | False | None | A custom User-Agent header to send with each request |

### Authentication

The tap uses JWT authentication with the Entegra API. You need to provide your email and password, which will be used to obtain JWT tokens automatically.

### Configuration Example

Create a `config.json` file (copy from `config.sample.json`):

```json
{
  "email": "your-email@example.com",
  "password": "your-password",
  "api_url": "https://apiv2.entegrabilisim.com",
  "start_date": "2020-01-01T00:00:00Z",
  "page_size": 100,
  "date_chunk_size": 30
}
```

Or configure in `meltano.yml`:

```yaml
# meltano.yml
plugins:
  extractors:
  - name: tap-entegra
    pip_url: git+https://github.com/emreustundag/tap-entegra.git@main
    config:
      email: your-email@example.com
      password: your-password
      api_url: https://apiv2.entegrabilisim.com
      start_date: '2020-01-01T00:00:00Z'
      page_size: 100
      date_chunk_size: 30
```

## Supported Streams

The tap supports the following streams from the Entegra API:

| Stream | Endpoint | Replication Method | Primary Key | Description |
|--------|----------|-------------------|-------------|-------------|
| **orders** | `/order/` | FULL_TABLE | `id` | Order data with date-range chunking for performance |
| **products** | `/product/` | FULL_TABLE | `id` | Product catalog with variations and pricing |
| **categories** | `/category/` | FULL_TABLE | `id` | Product categories |
| **customers** | `/customer/` | FULL_TABLE | `id` | Customer information |
| **brands** | `/product/brand/` | FULL_TABLE | `id` | Product brands |
| **stores** | `/store/getStores` | FULL_TABLE | `id` | Store information |
| **prices** | `/price/getPrices` | FULL_TABLE | `id` | Pricing information |
| **marketplace_quantity_settings** | `/store/getMarketplaceQuantitySettings` | FULL_TABLE | `id` | Marketplace quantity settings |
| **marketplace_price_settings** | `/price/getMarketplacePriceSettings` | FULL_TABLE | `id` | Marketplace price settings |

### Replication Strategy

All streams use **FULL_TABLE** replication, meaning they extract all available data on each run. This approach was chosen because:

1. **API Limitations**: The Entegra API's incremental filtering has limitations
2. **Data Consistency**: Ensures complete data synchronization
3. **Simplicity**: Reliable and predictable behavior

### Performance Optimizations

#### Orders Stream - Date Chunking
The orders stream implements date-range chunking to handle large datasets efficiently:

- **Chunk Size**: Configurable via `date_chunk_size` (default: 30 days)
- **Date Range**: From `start_date` to current date
- **Benefits**: Reduces memory usage and improves reliability for large order volumes

Example for large datasets:
```yaml
config:
  date_chunk_size: 7  # Process 7 days at a time for very large datasets
```

## Usage

### With Meltano

1. Add the tap to your Meltano project:
```bash
meltano add extractor tap-entegra
```

2. Configure the tap:
```bash
meltano config tap-entegra set email your-email@example.com
meltano config tap-entegra set password your-password
meltano config tap-entegra set start_date '2020-01-01T00:00:00Z'
```

3. Test the connection:
```bash
meltano invoke tap-entegra --test
```

4. Run the tap:
```bash
meltano run tap-entegra target-jsonl
```

### Standalone

You can also run the tap directly:

```bash
tap-entegra --config CONFIG --discover
tap-entegra --config CONFIG --catalog CATALOG
```

## API Rate Limits

The Entegra API has the following limits:
- **Daily Requests**: 20,000 requests per day
- **Token Expiry**: JWT tokens expire after 90 days
- **Concurrent Requests**: Not specified, but the tap makes sequential requests

## Data Schema

### Orders Stream
The orders stream includes comprehensive order data:
- Order details (ID, number, status, dates)
- Customer information
- Product line items with pricing
- Shipping and fulfillment data
- Marketplace-specific fields

### Products Stream  
The products stream includes:
- Product catalog information
- Variations and specifications
- Pricing across different channels
- Inventory quantities
- Images and descriptions

## Development

### Requirements

* Python 3.8+
* Poetry for dependency management

### Setup

1. Clone the repository:
```bash
git clone https://github.com/emreustundag/tap-entegra.git
cd tap-entegra
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file with your configuration:
```bash
TAP_ENTEGRA_EMAIL=your-email@example.com
TAP_ENTEGRA_PASSWORD=your-password
TAP_ENTEGRA_START_DATE=2020-01-01T00:00:00Z
```

4. Run tests:
```bash
poetry run pytest
```

### Testing

Run the tap in discovery mode:
```bash
poetry run tap-entegra --config config.json --discover
```

Run the tap with a catalog:
```bash
poetry run tap-entegra --config config.json --catalog catalog.json
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache 2.0 License.

## Support

For issues and questions:

1. Check the [GitHub Issues](https://github.com/yourusername/tap-entegra/issues)
2. Review the [Entegra API Documentation](ENTEGRA_API_DOCUMENTATION.md)
3. Consult the [Meltano Singer SDK Documentation](https://sdk.meltano.com)
