# tap-entegra

`tap-entegra` is a Singer tap for extracting data from the Entegra API.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

### For Meltano Users (Recommended)

#### Option 1: Install from PyPI (when published)
```bash
meltano add extractor tap-entegra
```

#### Option 2: Install from GitHub (current)
```bash
meltano add extractor tap-entegra --custom
```

Then configure in your `meltano.yml`:
```yaml
plugins:
  extractors:
  - name: tap-entegra
    namespace: tap_entegra
    pip_url: git+https://github.com/yourusername/tap-entegra.git@main
    capabilities:
    - state
    - catalog
    - discover
    - about
    - stream-maps
    settings:
    - name: email
      label: Email
      description: Your Entegra email for authentication
    - name: password
      kind: password
      label: Password
      description: Your Entegra password for authentication
      sensitive: true
    - name: api_url
      label: API URL
      description: The base URL for the Entegra API
      default: https://apiv2.entegrabilisim.com
    - name: start_date
      kind: date_iso8601
      label: Start Date
      description: The earliest record date to sync
    - name: page_size
      kind: integer
      label: Page Size
      description: Number of records to fetch per page
      default: 100
    - name: date_chunk_size
      kind: integer
      label: Date Chunk Size
      description: Number of days to process in each chunk for large datasets
      default: 30
```

### For Direct Use (Advanced)

#### Install from PyPI (when published)
```bash
pipx install tap-entegra
```

#### Install from GitHub
```bash
pipx install git+https://github.com/yourusername/tap-entegra.git@main
```

## Quick Start with Meltano

1. **Add the tap to your Meltano project:**
   ```bash
   meltano add extractor tap-entegra --custom
   ```

2. **Configure the tap:**
   ```bash
   meltano config tap-entegra set email your-email@example.com
   meltano config tap-entegra set password your-password
   meltano config tap-entegra set start_date '2020-01-01T00:00:00Z'
   ```

3. **Test the connection:**
   ```bash
   meltano invoke tap-entegra --test
   ```

4. **Discover available streams:**
   ```bash
   meltano invoke tap-entegra --discover
   ```

5. **Select streams to extract:**
   ```bash
   meltano select tap-entegra --list --all
   meltano select tap-entegra products orders customers
   ```

6. **Run a full extraction:**
   ```bash
   meltano run tap-entegra target-jsonl
   ```

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| email | True | None | Your Entegra email for authentication |
| password | True | None | Your Entegra password for authentication |
| api_url | False | https://apiv2.entegrabilisim.com | The base URL for the Entegra API |
| start_date | True | None | The earliest record date to sync (ISO format) |
| page_size | False | 100 | Number of records to fetch per page |
| date_chunk_size | False | 30 | Number of days to process in each chunk for large datasets |
| user_agent | False | None | A custom User-Agent header to send with each request |

### Authentication

The tap uses JWT authentication with the Entegra API. You need to provide your email and password, which will be used to obtain JWT tokens automatically.

### Configuration Examples

#### Using Meltano CLI
```bash
meltano config tap-entegra set email your-email@example.com
meltano config tap-entegra set password your-password
meltano config tap-entegra set api_url https://apiv2.entegrabilisim.com
meltano config tap-entegra set start_date '2020-01-01T00:00:00Z'
meltano config tap-entegra set page_size 100
meltano config tap-entegra set date_chunk_size 30
```

#### Using meltano.yml
```yaml
plugins:
  extractors:
  - name: tap-entegra
    config:
      email: your-email@example.com
      password: your-password
      api_url: https://apiv2.entegrabilisim.com
      start_date: '2020-01-01T00:00:00Z'
      page_size: 100
      date_chunk_size: 30
```

#### Using config.json (standalone)
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

## Supported Streams

The tap supports the following streams from the Entegra API:

| Stream | Endpoint | Replication Method | Primary Key | Description |
|--------|----------|-------------------|-------------|-------------|
| **orders** | `/order/` | FULL_TABLE | `id` | Order data with date-range chunking for performance |
| **products** | `/product/` | FULL_TABLE | `id` | Product catalog with variations and pricing |
| **categories** | `/category/` | FULL_TABLE | `id` | Product categories |
| **customers** | `/customer/` | FULL_TABLE | `id` | Customer information |
| **brands** | `/brand/` | FULL_TABLE | `id` | Product brands |
| **stores** | `/store/` | FULL_TABLE | `id` | Store information |
| **prices** | `/price/` | FULL_TABLE | `id` | Pricing information |
| **marketplace_quantity_settings** | `/marketplace/quantity/settings/` | FULL_TABLE | `id` | Marketplace quantity settings |
| **marketplace_price_settings** | `/marketplace/price/settings/` | FULL_TABLE | `id` | Marketplace price settings |

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

## Usage Examples

### With Meltano

#### Basic extraction to JSON Lines
```bash
meltano run tap-entegra target-jsonl
```

#### Extract specific streams
```bash
meltano select tap-entegra products orders
meltano run tap-entegra target-jsonl
```

#### Extract to database (ClickHouse example)
```bash
meltano add loader target-clickhouse
meltano run tap-entegra target-clickhouse
```

#### Scheduled runs
```bash
meltano schedule add tap-entegra-daily --extractor tap-entegra --loader target-jsonl --interval "@daily"
meltano schedule run tap-entegra-daily
```

### Standalone

You can also run the tap directly:

```bash
tap-entegra --config config.json --discover
tap-entegra --config config.json --catalog catalog.json
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
git clone https://github.com/yourusername/tap-entegra.git
cd tap-entegra
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `config.json` file with your configuration:
```json
{
  "email": "your-email@example.com",
  "password": "your-password",
  "api_url": "https://apiv2.entegrabilisim.com",
  "start_date": "2020-01-01T00:00:00Z"
}
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

### Local Development with Meltano

1. Install the tap in development mode:
```bash
meltano add extractor tap-entegra --custom
```

2. Update your `meltano.yml` to use the local version:
```yaml
plugins:
  extractors:
  - name: tap-entegra
    pip_url: -e .
```

3. Install and test:
```bash
meltano install
meltano invoke tap-entegra --discover
```

## Publishing to PyPI

Once you've built your tap and it is providing you the data you need, we encourage sharing it with the world!

### Prerequisites

1. **Create a PyPI account**: Sign up at [PyPI](https://pypi.org/account/register/)

2. **Set up credentials for publishing**:
   - **GitHub Actions (Recommended)**: Set up a [Trusted Publisher](https://docs.pypi.org/trusted-publishers/) for your project
   - **Local Publishing**: Create a [PyPI API token](https://pypi.org/help/#apitoken)

### Publishing Steps

1. **Build the package**:
```bash
uv build
```

2. **Publish to PyPI**:

   **Option A: Using Trusted Publisher (from GitHub Actions)**:
   ```bash
   uv publish --trusted-publishing=automatic
   ```

   **Option B: Using API Token**:
   ```bash
   uv publish --token=<your-pypi-token>
   ```

3. **Test the installation**:
```bash
# Using pipx (recommended)
pipx install tap-entegra

# Or using pip
pip install tap-entegra
```

### Making it Discoverable

Once published to PyPI, make your tap discoverable to other Meltano users:

1. **Update MeltanoHub**: Submit a pull request to [MeltanoHub](https://github.com/MeltanoLabs/hub) to list your tap
2. **Update documentation**: Ensure your README includes clear installation and usage instructions
3. **Add topics to your GitHub repo**: Add topics like `meltano`, `singer`, `tap`, `entegra-api`

## Production Deployment

### Updates for Production Use

Once your tap is published to PyPI, update your `meltano.yml` for production:

1. **Update the pip_url**:
```yaml
plugins:
  extractors:
  - name: tap-entegra
    pip_url: tap-entegra  # Instead of git URL or local path
```

2. **Or install from a specific version**:
```yaml
plugins:
  extractors:
  - name: tap-entegra
    pip_url: tap-entegra==1.0.0
```

3. **Reinstall to use the PyPI version**:
```bash
meltano install
```

### CI/CD Integration

Example GitHub Actions workflow for automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v2
    - name: Build
      run: uv build
    - name: Publish
      run: uv publish --trusted-publishing=automatic
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the Apache 2.0 License.

## Support

For issues and questions:

1. Check the [GitHub Issues](https://github.com/yourusername/tap-entegra/issues)
2. Review the [Meltano Documentation](https://docs.meltano.com)
3. Consult the [Singer SDK Documentation](https://sdk.meltano.com)

## Troubleshooting

### Common Issues

**Authentication Errors**
```
Error: Authentication failed
```
- Verify your email and password are correct
- Check that your Entegra account has API access

**SSL Certificate Issues**
```
Error: SSL certificate verification failed
```
- This is handled automatically by the tap, but if you encounter issues, contact support

**Rate Limiting**
```
Error: Too many requests
```
- Reduce the `page_size` setting
- Increase `date_chunk_size` for the orders stream
- Contact Entegra support to increase your rate limits

**Memory Issues with Large Datasets**
```
Error: Out of memory
```
- Reduce `date_chunk_size` for the orders stream
- Process data in smaller date ranges
- Consider using a more powerful machine for extraction
