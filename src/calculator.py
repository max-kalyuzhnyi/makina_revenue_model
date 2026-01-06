"""Revenue calculation engine for Makina"""

import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import List, Dict
from src.database import Machine, Scenario


class RevenueCalculator:
    """Calculates AUM and fees over time for machines"""

    def __init__(self, start_date: date = None, months: int = 36):
        """
        Initialize calculator

        Args:
            start_date: Starting date for projections (defaults to Jan 2026)
            months: Number of months to project (default 36)
        """
        self.start_date = start_date or date(2026, 1, 1)
        self.months = months
        self.dates = [self.start_date + relativedelta(months=i) for i in range(months)]

    def calculate_machine_projections(self, machine: Machine, scenario: Scenario) -> pd.DataFrame:
        """
        Calculate monthly projections for a single machine

        Returns DataFrame with columns:
        - date: Month date
        - aum: AUM in machine's native currency
        - aum_usd: AUM converted to USD
        - management_fee: Management fee for Makina in native currency
        - management_fee_usd: Management fee in USD
        - performance_fee: Performance fee for Makina in native currency
        - performance_fee_usd: Performance fee in USD
        - total_fee_usd: Total fees in USD
        """
        results = []

        # Get currency conversion rate
        currency_rates = {
            'ETH': scenario.eth_price,
            'USD': 1.0,
            'BTC': scenario.btc_price
        }
        rate = currency_rates.get(machine.currency, 1.0)

        # Initialize AUM
        current_aum = machine.initial_aum

        for month_date in self.dates:
            # Check if machine has launched
            if machine.launch_date and month_date < machine.launch_date:
                # Before launch - all zeros
                results.append({
                    'date': month_date,
                    'aum': 0.0,
                    'aum_usd': 0.0,
                    'management_fee': 0.0,
                    'management_fee_usd': 0.0,
                    'performance_fee': 0.0,
                    'performance_fee_usd': 0.0,
                    'total_fee_usd': 0.0
                })
                continue

            # If this is launch month, start with initial AUM
            if machine.launch_date and month_date == machine.launch_date:
                current_aum = machine.initial_aum

            # Calculate management fee for this month
            # Management Fee = (AUM * annual_fee_rate) / 12
            management_fee_native = current_aum * machine.management_fee_makina / 12
            management_fee_usd = management_fee_native * rate

            # Calculate yield for the month
            # Monthly Yield = AUM * (annual_yield / 12)
            monthly_yield = current_aum * machine.yield_apr / 12

            # Calculate performance fee
            # Performance Fee = Performance_Fee_Rate * Monthly_Yield * Net_Return_Margin * (1 - Employee_Capital_%)
            employee_capital_rate = machine.employee_capital if machine.employee_capital else 0.0
            performance_fee_native = (
                machine.performance_fee_makina *
                monthly_yield *
                machine.net_return_margin *
                (1 - employee_capital_rate)
            )
            performance_fee_usd = performance_fee_native * rate

            # Total fees
            total_fee_usd = management_fee_usd + performance_fee_usd

            # Store results
            results.append({
                'date': month_date,
                'aum': current_aum,
                'aum_usd': current_aum * rate,
                'management_fee': management_fee_native,
                'management_fee_usd': management_fee_usd,
                'performance_fee': performance_fee_native,
                'performance_fee_usd': performance_fee_usd,
                'total_fee_usd': total_fee_usd
            })

            # Update AUM for next month (add monthly growth)
            monthly_addition = machine.initial_aum * machine.monthly_growth_rate
            current_aum = current_aum + monthly_addition

        df = pd.DataFrame(results)
        df['machine_name'] = machine.name
        df['currency'] = machine.currency
        return df

    def calculate_all_machines(self, machines: List[Machine], scenario: Scenario) -> pd.DataFrame:
        """
        Calculate projections for all machines and aggregate

        Returns DataFrame with all machine projections combined
        """
        all_dfs = []
        for machine in machines:
            df = self.calculate_machine_projections(machine, scenario)
            all_dfs.append(df)

        if not all_dfs:
            # Return empty dataframe with correct structure
            return pd.DataFrame(columns=[
                'date', 'aum', 'aum_usd', 'management_fee', 'management_fee_usd',
                'performance_fee', 'performance_fee_usd', 'total_fee_usd',
                'machine_name', 'currency'
            ])

        return pd.concat(all_dfs, ignore_index=True)

    def aggregate_by_currency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate AUM by currency and date

        Returns DataFrame with columns: date, currency, aum, aum_usd
        """
        if df.empty:
            return pd.DataFrame(columns=['date', 'currency', 'aum', 'aum_usd'])

        agg = df.groupby(['date', 'currency']).agg({
            'aum': 'sum',
            'aum_usd': 'sum'
        }).reset_index()

        return agg

    def aggregate_fees_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate fees by date (all currencies combined in USD)

        Returns DataFrame with columns: date, management_fee_usd, performance_fee_usd, total_fee_usd
        """
        if df.empty:
            return pd.DataFrame(columns=['date', 'management_fee_usd', 'performance_fee_usd', 'total_fee_usd'])

        agg = df.groupby('date').agg({
            'management_fee_usd': 'sum',
            'performance_fee_usd': 'sum',
            'total_fee_usd': 'sum',
            'aum_usd': 'sum'
        }).reset_index()

        return agg

    def aggregate_by_year(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate metrics by year

        Returns DataFrame with:
        - year: Calendar year
        - end_of_year_aum: AUM at end of year (December)
        - total_management_fees: Sum of management fees for the year
        - total_performance_fees: Sum of performance fees for the year
        - total_fees: Sum of all fees for the year
        - avg_fee_pct: Average fee % (total_fees / avg AUM * 100)
        """
        if df.empty:
            return pd.DataFrame(columns=[
                'year', 'end_of_year_aum', 'total_management_fees',
                'total_performance_fees', 'total_fees', 'avg_fee_pct'
            ])

        # First aggregate by date to get daily totals
        daily_totals = df.groupby('date').agg({
            'aum_usd': 'sum',
            'management_fee_usd': 'sum',
            'performance_fee_usd': 'sum',
            'total_fee_usd': 'sum'
        }).reset_index()

        # Add year and month columns
        daily_totals['year'] = pd.to_datetime(daily_totals['date']).dt.year
        daily_totals['month'] = pd.to_datetime(daily_totals['date']).dt.month

        # Get end of year AUM (last month of each year)
        end_of_year = daily_totals.groupby('year').apply(
            lambda x: x.loc[x['date'].idxmax(), 'aum_usd']
        ).reset_index()
        end_of_year.columns = ['year', 'end_of_year_aum']

        # Calculate average AUM for fee % calculation
        avg_aum = daily_totals.groupby('year').agg({
            'aum_usd': 'mean'
        }).reset_index()
        avg_aum.columns = ['year', 'avg_aum_usd']

        # Sum fees by year
        yearly_fees = daily_totals.groupby('year').agg({
            'management_fee_usd': 'sum',
            'performance_fee_usd': 'sum',
            'total_fee_usd': 'sum'
        }).reset_index()

        # Merge all together
        yearly = end_of_year.merge(yearly_fees, on='year')
        yearly = yearly.merge(avg_aum, on='year')

        # Calculate average fee percentage
        yearly['avg_fee_pct'] = (yearly['total_fee_usd'] / yearly['avg_aum_usd'] * 100).fillna(0)

        # Drop avg_aum_usd (we don't need it in final output)
        yearly = yearly.drop('avg_aum_usd', axis=1)

        yearly.columns = [
            'year', 'end_of_year_aum', 'total_management_fees',
            'total_performance_fees', 'total_fees', 'avg_fee_pct'
        ]

        return yearly

    def calculate_fee_percentage(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate fee as percentage of AUM (annualized)

        Returns DataFrame with columns: date, fee_pct_annualized
        """
        if df.empty:
            return pd.DataFrame(columns=['date', 'fee_pct_annualized'])

        agg = self.aggregate_fees_by_date(df)

        # Annualized fee % = (monthly_fee / monthly_aum) * 12 * 100
        agg['fee_pct_annualized'] = (agg['total_fee_usd'] / agg['aum_usd'] * 12 * 100).fillna(0)

        return agg[['date', 'fee_pct_annualized', 'total_fee_usd', 'aum_usd']]
