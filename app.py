"""Revenue Model - Interactive Dashboard"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date
from src.database import DatabaseManager, Machine, Scenario
from src.calculator import RevenueCalculator

# Utility function for number formatting
def format_number(num):
    """Format numbers with M/B suffixes and max 2 decimals"""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.2f}"

def format_percentage(num):
    """Format percentage with 2 decimals"""
    return f"{num:.2f}%"

# Page configuration
st.set_page_config(
    page_title="Revenue Model",
    page_icon="💰",
    layout="wide"
)

# Custom CSS to reduce top padding
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def init_db():
    db = DatabaseManager()
    db.init_default_data()
    return db

db = init_db()

# Sidebar - Scenario and General Inputs
with st.sidebar:
    # Title in sidebar
    st.markdown("**⚙️ Revenue Model**")
    st.markdown("---")
    st.markdown("**Configuration**")

    # Get default scenario (Base Case)
    session = db.get_session()
    selected_scenario = session.query(Scenario).filter_by(name="Base Case").first()

    # Initialize session state for prices if not exists
    if 'eth_price' not in st.session_state:
        st.session_state.eth_price = float(selected_scenario.eth_price)
    if 'btc_price' not in st.session_state:
        st.session_state.btc_price = float(selected_scenario.btc_price)

    # Initialize default scenario values (only once)
    if 'default_eth_price' not in st.session_state:
        st.session_state.default_eth_price = 3000.0
        st.session_state.default_btc_price = 120000.0
        st.session_state.default_yield_eth = 5.0
        st.session_state.default_yield_usd = 8.0
        st.session_state.default_yield_btc = 3.0
        st.session_state.default_subscription_growth = 10.0
        # Save initial machines snapshot
        try:
            st.session_state.default_machines_snapshot = db.save_machines_snapshot(selected_scenario.id)
        except AttributeError:
            # If method doesn't exist (cached old version), initialize empty snapshot
            st.session_state.default_machines_snapshot = []
            st.warning("⚠️ Please restart the app to enable save/restore functionality")

    st.markdown("**Market Prices**")
    eth_price = st.number_input("ETH Price (USD)", value=st.session_state.eth_price, min_value=0.0, step=100.0, key='eth_input')
    btc_price = st.number_input("BTC Price (USD)", value=st.session_state.btc_price, min_value=0.0, step=1000.0, key='btc_input')

    # Update scenario prices if changed
    if eth_price != st.session_state.eth_price or btc_price != st.session_state.btc_price:
        st.session_state.eth_price = eth_price
        st.session_state.btc_price = btc_price
        selected_scenario.eth_price = eth_price
        selected_scenario.btc_price = btc_price
        session.commit()

    # Use session state values for calculations
    current_eth_price = st.session_state.eth_price
    current_btc_price = st.session_state.btc_price

    st.markdown("**Scenario Assumptions**")
    st.write("Yield APR by Asset")
    yield_eth = st.number_input("ETH Yield APR (%)", value=5.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f", key='yield_eth')
    yield_usd = st.number_input("USD Yield APR (%)", value=8.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f", key='yield_usd')
    yield_btc = st.number_input("BTC Yield APR (%)", value=3.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f", key='yield_btc')

    st.write("Monthly Growth Rate")
    subscription_growth = st.number_input("Subscription Growth (%)", value=10.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f", key='sub_growth')

    apply_to_all = st.checkbox("Apply to all machines", value=False, key='apply_to_all')

    if apply_to_all and st.button("Update All Machines"):
        session_update = db.get_session()
        machines_to_update = session_update.query(Machine).filter_by(scenario_id=selected_scenario.id).all()

        for machine in machines_to_update:
            # Apply yield based on currency (convert from % to decimal)
            if machine.currency == 'ETH':
                machine.yield_apr = yield_eth / 100
            elif machine.currency == 'USD':
                machine.yield_apr = yield_usd / 100
            elif machine.currency == 'BTC':
                machine.yield_apr = yield_btc / 100

            # Apply growth rate (convert from % to decimal)
            machine.monthly_growth_rate = subscription_growth / 100

        session_update.commit()
        session_update.close()
        st.success(f"✅ Updated {len(machines_to_update)} machines!")
        st.rerun()

    st.markdown("**Projection Settings**")
    projection_months = st.slider("Projection Period (months)", 12, 60, 36, 6)

    # Save current as default button
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save as Default"):
            st.session_state.default_eth_price = st.session_state.eth_price
            st.session_state.default_btc_price = st.session_state.btc_price
            st.session_state.default_yield_eth = yield_eth
            st.session_state.default_yield_usd = yield_usd
            st.session_state.default_yield_btc = yield_btc
            st.session_state.default_subscription_growth = subscription_growth
            # Save current machines snapshot
            try:
                st.session_state.default_machines_snapshot = db.save_machines_snapshot(selected_scenario.id)
                st.success("✅ Saved as default!")
            except AttributeError:
                st.error("⚠️ Please restart the app to enable this feature")

    with col2:
        if st.button("🔄 Reset to Default"):
            st.session_state.eth_price = st.session_state.default_eth_price
            st.session_state.btc_price = st.session_state.default_btc_price
            selected_scenario.eth_price = st.session_state.default_eth_price
            selected_scenario.btc_price = st.session_state.default_btc_price
            session.commit()
            # Restore machines from snapshot
            try:
                db.restore_machines_snapshot(selected_scenario.id, st.session_state.default_machines_snapshot)
                st.success("✅ Reset to default!")
                st.rerun()
            except AttributeError:
                st.error("⚠️ Please restart the app to enable this feature")

    # Store values before closing session
    scenario_id = selected_scenario.id
    scenario_name = selected_scenario.name

    session.close()

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "⚙️ Machines", "📈 Yearly View"])

# Calculate projections - use a fresh session
session = db.get_session()
selected_scenario = session.query(Scenario).filter_by(id=scenario_id).first()

# Override with session state values (for real-time updates)
selected_scenario.eth_price = current_eth_price
selected_scenario.btc_price = current_btc_price

machines = session.query(Machine).filter_by(scenario_id=scenario_id).all()

# Extract data before closing session
machines_list = list(machines)

calculator = RevenueCalculator(months=projection_months)
all_projections = calculator.calculate_all_machines(machines_list, selected_scenario)

# Close session after getting all needed data
session.close()

# TAB 1: Dashboard
with tab1:
    if all_projections.empty:
        st.warning("No machines configured. Please add machines in the Machines tab.")
    else:
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)

        total_aum = all_projections.groupby('date')['aum_usd'].sum().iloc[-1]
        total_fees_monthly = all_projections.groupby('date')['total_fee_usd'].sum().iloc[-1]
        total_fees_annual = total_fees_monthly * 12
        fee_pct_data = calculator.calculate_fee_percentage(all_projections)
        avg_fee_pct = fee_pct_data['fee_pct_annualized'].mean()

        with col1:
            st.metric("Total AUM (USD)", format_number(total_aum))
        with col2:
            st.metric("Monthly Fees", format_number(total_fees_monthly))
        with col3:
            st.metric("Annual Fees (Projected)", format_number(total_fees_annual))
        with col4:
            st.metric("Avg Fee %", format_percentage(avg_fee_pct))

        st.markdown("---")

        # AUM Stacked Area Chart by Currency
        st.subheader("Total AUM Over Time (USD) - By Currency")
        aum_by_currency = calculator.aggregate_by_currency(all_projections)

        # Create stacked area chart
        fig_aum = go.Figure()

        # Define color scheme for currencies
        currency_colors = {
            'USD': '#2ecc71',  # Green
            'ETH': '#3498db',  # Blue
            'BTC': '#f39c12'   # Orange
        }

        # Sort currencies for consistent stacking order
        for currency in ['BTC', 'ETH', 'USD']:
            if currency in aum_by_currency['currency'].values:
                currency_data = aum_by_currency[aum_by_currency['currency'] == currency]
                fig_aum.add_trace(go.Scatter(
                    x=currency_data['date'],
                    y=currency_data['aum_usd'],
                    name=currency,
                    mode='lines',
                    stackgroup='one',
                    fillcolor=currency_colors.get(currency, '#95a5a6'),
                    line=dict(width=0.5, color=currency_colors.get(currency, '#95a5a6')),
                    hovertemplate='%{y:,.2f}<extra></extra>'
                ))

        fig_aum.update_layout(
            xaxis_title="Date",
            yaxis_title="AUM (USD)",
            hovermode='x unified',
            height=500,
            yaxis=dict(tickformat=',.0f')
        )
        st.plotly_chart(fig_aum, use_container_width=True)

        st.markdown("---")

        # AUM Stacked Area Chart by Machine
        st.subheader("Total AUM Over Time (USD) - By Machine")

        # Create stacked area chart by machine
        fig_aum_machine = go.Figure()

        # Get unique machines and assign colors
        unique_machines = all_projections['machine_name'].unique()
        # Generate enough colors by cycling through multiple color sets if needed
        all_colors = (px.colors.qualitative.Set3 +
                     px.colors.qualitative.Pastel +
                     px.colors.qualitative.Set2 +
                     px.colors.qualitative.Set1)
        machine_colors = all_colors[:len(unique_machines)]

        for i, machine_name in enumerate(unique_machines):
            machine_data = all_projections[all_projections['machine_name'] == machine_name]
            fig_aum_machine.add_trace(go.Scatter(
                x=machine_data['date'],
                y=machine_data['aum_usd'],
                name=machine_name,
                mode='lines',
                stackgroup='one',
                fillcolor=machine_colors[i],
                line=dict(width=0.5, color=machine_colors[i]),
                hovertemplate='%{y:,.2f}<extra></extra>'
            ))

        fig_aum_machine.update_layout(
            xaxis_title="Date",
            yaxis_title="AUM (USD)",
            hovermode='x unified',
            height=500,
            yaxis=dict(tickformat=',.0f')
        )
        st.plotly_chart(fig_aum_machine, use_container_width=True)

        st.markdown("---")

        # Fees Over Time (with split)
        st.subheader("Fees Over Time (Management vs Performance)")
        fees_by_date = calculator.aggregate_fees_by_date(all_projections)

        fig_fees = go.Figure()
        fig_fees.add_trace(go.Bar(
            x=fees_by_date['date'],
            y=fees_by_date['management_fee_usd'],
            name='Management Fees',
            marker_color='#2ecc71',
            hovertemplate='%{y:,.2f}<extra></extra>'
        ))
        fig_fees.add_trace(go.Bar(
            x=fees_by_date['date'],
            y=fees_by_date['performance_fee_usd'],
            name='Performance Fees',
            marker_color='#3498db',
            hovertemplate='%{y:,.2f}<extra></extra>'
        ))

        fig_fees.update_layout(
            barmode='stack',
            xaxis_title="Date",
            yaxis_title="Fees (USD)",
            hovermode='x unified',
            height=400,
            yaxis=dict(tickformat=',.0f')
        )
        st.plotly_chart(fig_fees, use_container_width=True)

        st.markdown("---")

        # Fee % to AUM
        st.subheader("Fee % to AUM (Annualized)")

        fig_fee_pct = go.Figure()
        fig_fee_pct.add_trace(go.Scatter(
            x=fee_pct_data['date'],
            y=fee_pct_data['fee_pct_annualized'],
            name='Fee %',
            mode='lines+markers',
            line=dict(width=2, color='#e74c3c'),
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))

        fig_fee_pct.update_layout(
            xaxis_title="Date",
            yaxis_title="Fee % (Annualized)",
            yaxis=dict(
                range=[0, 1],
                tickformat='.2f',
                ticksuffix='%'
            ),
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_fee_pct, use_container_width=True)

# TAB 2: Machines Management
with tab2:
    st.header("Machines Configuration")

    # Display existing machines
    st.subheader("Current Machines")

    session = db.get_session()
    machines = session.query(Machine).filter_by(scenario_id=selected_scenario.id).all()

    if not machines:
        st.info("No machines configured yet.")
    else:
        for i, machine in enumerate(machines):
            with st.expander(f"🔧 {machine.name} ({machine.currency})", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    new_name = st.text_input("Name", value=machine.name, key=f"name_{machine.id}")
                    currency = st.selectbox("Currency", ["ETH", "USD", "BTC"],
                                          index=["ETH", "USD", "BTC"].index(machine.currency),
                                          key=f"curr_{machine.id}")
                    launch_date_val = st.date_input("Launch Date (optional)",
                                                   value=machine.launch_date,
                                                   key=f"launch_{machine.id}")
                    initial_aum = st.number_input("Initial AUM", value=float(machine.initial_aum),
                                                 min_value=0.0, key=f"aum_{machine.id}")
                    monthly_growth = st.number_input("Monthly Growth Rate (%)",
                                                    value=float(machine.monthly_growth_rate * 100),
                                                    min_value=0.0, max_value=100.0, step=1.0,
                                                    format="%.1f",
                                                    key=f"growth_{machine.id}")
                    yield_apr = st.number_input("Yield APR (%)", value=float(machine.yield_apr * 100),
                                               min_value=0.0, max_value=100.0, step=1.0,
                                               format="%.1f",
                                               key=f"yield_{machine.id}")

                with col2:
                    mgmt_fee_total = st.number_input("Management Fee Total (%)",
                                                    value=float(machine.management_fee_total * 100),
                                                    min_value=0.0, max_value=100.0, step=0.01,
                                                    format="%.2f", key=f"mgmt_total_{machine.id}")
                    mgmt_fee_share = st.number_input("Management Fee Makina Share (%)",
                                                    value=float(machine.management_fee_makina_share * 100),
                                                    min_value=0.0, max_value=100.0, step=1.0,
                                                    format="%.1f",
                                                    key=f"mgmt_share_{machine.id}")
                    perf_fee_total = st.number_input("Performance Fee Total (%)",
                                                    value=float(machine.performance_fee_total * 100),
                                                    min_value=0.0, max_value=100.0, step=1.0,
                                                    format="%.1f",
                                                    key=f"perf_total_{machine.id}")
                    perf_fee_share = st.number_input("Performance Fee Makina Share (%)",
                                                    value=float(machine.performance_fee_makina_share * 100),
                                                    min_value=0.0, max_value=100.0, step=1.0,
                                                    format="%.1f",
                                                    key=f"perf_share_{machine.id}")
                    net_return = st.number_input("Net Return Margin (%)",
                                                value=float(machine.net_return_margin * 100),
                                                min_value=0.0, max_value=100.0, step=1.0,
                                                format="%.1f",
                                                key=f"net_return_{machine.id}")

                col_btn1, col_btn2 = st.columns([1, 5])
                with col_btn1:
                    if st.button("💾 Save", key=f"save_{machine.id}"):
                        machine.name = new_name
                        machine.currency = currency
                        machine.launch_date = launch_date_val if launch_date_val else None
                        machine.initial_aum = initial_aum
                        machine.monthly_growth_rate = monthly_growth / 100
                        machine.yield_apr = yield_apr / 100
                        machine.management_fee_total = mgmt_fee_total / 100
                        machine.management_fee_makina_share = mgmt_fee_share / 100
                        machine.performance_fee_total = perf_fee_total / 100
                        machine.performance_fee_makina_share = perf_fee_share / 100
                        machine.net_return_margin = net_return / 100
                        session.commit()
                        st.success(f"✅ {machine.name} updated!")
                        st.rerun()

                with col_btn2:
                    if st.button("🗑️ Delete", key=f"delete_{machine.id}"):
                        session.delete(machine)
                        session.commit()
                        st.success(f"❌ {machine.name} deleted!")
                        st.rerun()

    session.close()

    st.markdown("---")

    # Add New Machine
    st.subheader("➕ Add New Machine")

    col1, col2 = st.columns(2)

    with col1:
        new_machine_name = st.text_input("Machine Name", value="New Machine")
        new_currency = st.selectbox("Currency", ["USD", "ETH", "BTC"], key="new_curr")
        new_launch_date = st.date_input("Launch Date (optional)", value=None, key="new_launch")
        new_initial_aum = st.number_input("Initial AUM", value=55000000.0, min_value=0.0, key="new_aum")
        new_monthly_growth = st.number_input("Monthly Growth Rate", value=0.1, min_value=0.0, max_value=1.0, step=0.01, key="new_growth")
        new_yield_apr = st.number_input("Yield APR", value=0.08, min_value=0.0, max_value=1.0, step=0.01, key="new_yield")

    with col2:
        new_mgmt_fee_total = st.number_input("Management Fee Total", value=0.0075, min_value=0.0, max_value=1.0, step=0.0001, format="%.4f", key="new_mgmt_total")
        new_mgmt_fee_share = st.number_input("Management Fee Makina Share", value=0.4, min_value=0.0, max_value=1.0, step=0.01, key="new_mgmt_share")
        new_perf_fee_total = st.number_input("Performance Fee Total", value=0.15, min_value=0.0, max_value=1.0, step=0.01, key="new_perf_total")
        new_perf_fee_share = st.number_input("Performance Fee Makina Share", value=0.4, min_value=0.0, max_value=1.0, step=0.01, key="new_perf_share")
        new_net_return = st.number_input("Net Return Margin", value=0.7, min_value=0.0, max_value=1.0, step=0.01, key="new_net_return")

    if st.button("➕ Add Machine"):
        session = db.get_session()
        new_machine = Machine(
            scenario_id=selected_scenario.id,
            name=new_machine_name,
            currency=new_currency,
            launch_date=new_launch_date if new_launch_date else None,
            initial_aum=new_initial_aum,
            monthly_growth_rate=new_monthly_growth,
            yield_apr=new_yield_apr,
            management_fee_total=new_mgmt_fee_total,
            management_fee_makina_share=new_mgmt_fee_share,
            performance_fee_total=new_perf_fee_total,
            performance_fee_makina_share=new_perf_fee_share,
            net_return_margin=new_net_return
        )
        session.add(new_machine)
        session.commit()
        session.close()
        st.success(f"✅ Machine '{new_machine_name}' added!")
        st.rerun()

    # Clone Machine
    st.markdown("---")
    st.subheader("📋 Clone Machine")

    session = db.get_session()
    machines = session.query(Machine).filter_by(scenario_id=selected_scenario.id).all()

    if machines:
        machine_to_clone = st.selectbox("Select machine to clone",
                                       [m.name for m in machines],
                                       key="clone_select")
        num_clones = st.number_input("Number of clones", min_value=1, max_value=20, value=1, key="num_clones")

        if st.button("📋 Clone"):
            source_machine = next(m for m in machines if m.name == machine_to_clone)

            for i in range(int(num_clones)):
                clone = Machine(
                    scenario_id=selected_scenario.id,
                    name=f"{source_machine.name} (Clone {i+1})",
                    currency=source_machine.currency,
                    launch_date=source_machine.launch_date,
                    initial_aum=source_machine.initial_aum,
                    monthly_growth_rate=source_machine.monthly_growth_rate,
                    yield_apr=source_machine.yield_apr,
                    management_fee_total=source_machine.management_fee_total,
                    management_fee_makina_share=source_machine.management_fee_makina_share,
                    performance_fee_total=source_machine.performance_fee_total,
                    performance_fee_makina_share=source_machine.performance_fee_makina_share,
                    net_return_margin=source_machine.net_return_margin,
                    employee_capital=source_machine.employee_capital
                )
                session.add(clone)

            session.commit()
            st.success(f"✅ Created {num_clones} clone(s) of '{machine_to_clone}'!")
            st.rerun()

    session.close()

# TAB 3: Yearly View
with tab3:
    st.header("📈 Yearly Aggregation")

    if all_projections.empty:
        st.warning("No data available. Please configure machines first.")
    else:
        yearly_data = calculator.aggregate_by_year(all_projections)

        # Display table
        st.subheader("Yearly Summary")
        yearly_display = yearly_data.copy()

        # Format with M/B suffixes
        def format_for_table(x):
            if x >= 1_000_000_000:
                return f"${x/1_000_000_000:.2f}B"
            elif x >= 1_000_000:
                return f"${x/1_000_000:.2f}M"
            else:
                return f"${x:,.2f}"

        yearly_display['end_of_year_aum'] = yearly_display['end_of_year_aum'].apply(format_for_table)
        yearly_display['total_management_fees'] = yearly_display['total_management_fees'].apply(format_for_table)
        yearly_display['total_performance_fees'] = yearly_display['total_performance_fees'].apply(format_for_table)
        yearly_display['total_fees'] = yearly_display['total_fees'].apply(format_for_table)
        yearly_display['avg_fee_pct'] = yearly_display['avg_fee_pct'].apply(lambda x: f"{x:.2f}%")

        yearly_display.columns = ['Year', 'End of Year AUM', 'Management Fees', 'Performance Fees', 'Total Fees', 'Avg Fee %']
        st.dataframe(yearly_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("End of Year AUM")
            fig_yearly_aum = px.bar(yearly_data, x='year', y='end_of_year_aum',
                                    labels={'year': 'Year', 'end_of_year_aum': 'AUM (USD)'},
                                    color_discrete_sequence=['#1f77b4'])
            fig_yearly_aum.update_layout(
                height=400,
                yaxis=dict(tickformat=',.0f')
            )
            fig_yearly_aum.update_traces(hovertemplate='%{y:,.2f}<extra></extra>')
            st.plotly_chart(fig_yearly_aum, use_container_width=True)

        with col2:
            st.subheader("Total Fees by Year")
            fig_yearly_fees = go.Figure()
            fig_yearly_fees.add_trace(go.Bar(
                x=yearly_data['year'],
                y=yearly_data['total_management_fees'],
                name='Management Fees',
                marker_color='#2ecc71',
                hovertemplate='%{y:,.2f}<extra></extra>'
            ))
            fig_yearly_fees.add_trace(go.Bar(
                x=yearly_data['year'],
                y=yearly_data['total_performance_fees'],
                name='Performance Fees',
                marker_color='#3498db',
                hovertemplate='%{y:,.2f}<extra></extra>'
            ))
            fig_yearly_fees.update_layout(
                barmode='stack',
                xaxis_title='Year',
                yaxis_title='Fees (USD)',
                height=400,
                yaxis=dict(tickformat=',.0f')
            )
            st.plotly_chart(fig_yearly_fees, use_container_width=True)
