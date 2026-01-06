# Quick Start Guide

## Run the App Locally

### Option 1: Using the run script (recommended)
```bash
./run.sh
```

### Option 2: Manual run
```bash
export PATH="/Users/maksim/Library/Python/3.9/bin:$PATH"
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## First Steps

1. **View Dashboard** - The main tab shows all revenue projections with charts
   - Total AUM across all machines
   - Monthly and yearly fee projections
   - Fee % to AUM analysis

2. **Adjust Prices** - Use the sidebar to modify:
   - ETH price (impacts all ETH-denominated machines)
   - BTC price (impacts all BTC-denominated machines)
   - Projection period (12-60 months)

3. **Manage Machines** - Go to "Machines" tab:
   - Edit existing machines by expanding their panel
   - Add new machines with custom parameters
   - Clone machines to quickly create multiple similar strategies

4. **View Yearly Data** - Check "Yearly View" tab for:
   - Annual AUM averages
   - Total fees per year
   - Year-over-year growth

## Adding Machines

### Quick Add (using defaults from DNEW 1):
1. Go to "Machines" tab
2. Scroll to "Add New Machine" section
3. Just change the name and click "Add Machine"

### Clone Existing:
1. Go to "Machines" tab
2. Scroll to "Clone Machine" section
3. Select machine to clone (e.g., "DNEW 1" for USD machines)
4. Set number of clones
5. Click "Clone"

### Bulk Add Example:
To add 10 standard USD machines:
1. Clone "DNEW 1" 10 times
2. Edit each clone's name and launch date as needed

## Understanding the Calculations

### AUM Growth
- Starts with Initial AUM
- Each month adds: `Initial AUM × Monthly Growth Rate`
- Example: $55M initial + 10% monthly = $5.5M added per month

### Management Fees
- Monthly fee = `(AUM × Management Fee Rate) / 12`
- Makina receives: `Monthly Fee × Makina Share`

### Performance Fees
- Monthly yield = `AUM × Yield APR / 12`
- Performance fee = `Performance Fee Rate × Monthly Yield × Net Return Margin`
- Makina receives: `Performance Fee × Makina Share`

## Database

- All data is stored in `data/makina_revenue.db` (SQLite)
- Changes are auto-saved
- To reset: delete the database file and restart the app

## Project Structure

```
makina_rev_model/
├── app.py                    # Main Streamlit app
├── src/
│   ├── database.py          # Database models & operations
│   └── calculator.py        # Revenue calculation engine
├── data/
│   └── makina_revenue.db   # SQLite database (auto-created)
├── requirements.txt         # Python dependencies
├── run.sh                   # Launch script
└── README.md               # Full documentation
```

## Troubleshooting

### "streamlit: command not found"
Use the run.sh script which includes the correct PATH

### Database errors
Delete `data/makina_revenue.db` and restart to recreate with defaults

### Charts not showing
Refresh the page or click "Rerun" in the Streamlit UI
