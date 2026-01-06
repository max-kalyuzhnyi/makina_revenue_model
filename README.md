# Makina Revenue Model Dashboard

Interactive dashboard for modeling Makina's revenue projections across multiple asset management strategies (machines).

## Features

- **Interactive Dashboard**: Visualize AUM and fees over time with multiple chart types
- **Machine Management**: Add, edit, clone, and remove machines with custom parameters
- **Scenario Planning**: Adjust market prices (ETH/BTC) and see real-time impact
- **Multiple Views**:
  - Monthly projections (up to 60 months)
  - AUM by currency (ETH, USD, BTC)
  - Fee breakdown (Management vs Performance)
  - Fee % to AUM analysis
  - Yearly aggregations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Dashboard Tab
View all key metrics and charts:
- Total AUM and fees
- AUM over time by currency
- Fee breakdown (management vs performance)
- Fee percentage to AUM

### Machines Tab
Manage your strategies:
- Edit existing machine parameters
- Add new machines
- Clone machines (create multiple copies at once)
- Delete machines

### Yearly View Tab
See annual aggregations:
- Average AUM by year
- Total fees by year (split by type)

## Machine Parameters

Each machine has the following configurable parameters:

- **Name**: Machine identifier
- **Currency**: ETH, USD, or BTC
- **Launch Date**: When the machine starts (optional)
- **Initial AUM**: Starting assets under management
- **Monthly Growth Rate**: Percentage growth per month (e.g., 0.1 = 10%)
- **Yield APR**: Annual percentage return
- **Management Fee Total**: Total management fee rate
- **Management Fee Makina Share**: Makina's portion of management fees
- **Performance Fee Total**: Total performance fee rate
- **Performance Fee Makina Share**: Makina's portion of performance fees
- **Net Return Margin**: Net return after costs (default: 0.7 = 70%)

## Database

The app uses SQLite for data persistence:
- Database file: `data/makina_revenue.db`
- Includes default scenario with 7 machines (DETH, DUSD, DBIT, Lido, DNEW 1-3)
- All changes are automatically saved

## Deployment

For cloud deployment (e.g., Vercel, Streamlit Cloud):

1. Push code to GitHub repository
2. Connect to deployment platform
3. Set Python version to 3.9+
4. Deploy with `streamlit run app.py`

## Recommended Machine Templates

**Standard USD Machine** (based on DNEW 1):
- Currency: USD
- Initial AUM: $55,000,000
- Monthly Growth: 10%
- Yield APR: 8%
- Management Fee: 0.75% (Makina share: 40%)
- Performance Fee: 15% (Makina share: 40%)
- Net Return Margin: 70%

**Standard ETH Machine** (based on DETH):
- Currency: ETH
- Initial AUM: 9,300 ETH
- Monthly Growth: 10%
- Yield APR: 5%
- Management Fee: 0.75% (Makina share: 40%)
- Performance Fee: 13% (Makina share: 40%)
- Net Return Margin: 70%

**Standard BTC Machine** (based on DBIT):
- Currency: BTC
- Initial AUM: 200 BTC
- Monthly Growth: 10%
- Yield APR: 3%
- Management Fee: 0.5% (Makina share: 40%)
- Performance Fee: 10% (Makina share: 40%)
- Net Return Margin: 70%
