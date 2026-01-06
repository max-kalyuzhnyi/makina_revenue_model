"""Database models and operations for Makina Revenue Model"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
import os

Base = declarative_base()


class Scenario(Base):
    """Scenario configurations (Base Case, Bear Case, Bull Case)"""
    __tablename__ = 'scenarios'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    eth_price = Column(Float, default=3000.0)
    btc_price = Column(Float, default=90000.0)
    is_active = Column(Boolean, default=False)

    machines = relationship("Machine", back_populates="scenario", cascade="all, delete-orphan")


class Machine(Base):
    """Individual strategy/machine configuration"""
    __tablename__ = 'machines'

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    name = Column(String, nullable=False)
    currency = Column(String, nullable=False)  # ETH, USD, or BTC
    launch_date = Column(Date, nullable=True)

    # Financial parameters
    initial_aum = Column(Float, nullable=False)
    monthly_growth_rate = Column(Float, default=0.1)  # Additions rate

    # Fee structure
    management_fee_total = Column(Float, default=0.0075)
    management_fee_makina_share = Column(Float, default=0.4)
    performance_fee_total = Column(Float, default=0.15)
    performance_fee_makina_share = Column(Float, default=0.4)

    # Yield parameters
    yield_apr = Column(Float, default=0.08)
    net_return_margin = Column(Float, default=0.7)

    # Employee capital (currently unused but keeping for future)
    employee_capital = Column(Float, default=0.0)

    scenario = relationship("Scenario", back_populates="machines")

    @property
    def management_fee_makina(self):
        """Calculated: Total Management Fee * Makina Share"""
        return self.management_fee_total * self.management_fee_makina_share

    @property
    def performance_fee_makina(self):
        """Calculated: Total Performance Fee * Makina Share"""
        return self.performance_fee_total * self.performance_fee_makina_share


class DatabaseManager:
    """Handles database operations"""

    def __init__(self, db_path='data/makina_revenue.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def init_default_data(self):
        """Initialize database with default scenario and machines"""
        session = self.get_session()

        try:
            # Check if data already exists
            if session.query(Scenario).count() > 0:
                return

            # Create Base Case scenario
            base_case = Scenario(
                name="Base Case",
                eth_price=3000.0,
                btc_price=90000.0,
                is_active=True
            )
            session.add(base_case)
            session.flush()

            # Add machines with data from Excel
            machines = [
                {
                    'name': 'DETH',
                    'currency': 'ETH',
                    'launch_date': None,
                    'initial_aum': 9300.0,
                    'monthly_growth_rate': 0.1,
                    'management_fee_total': 0.0075,
                    'management_fee_makina_share': 0.4,
                    'performance_fee_total': 0.13,
                    'performance_fee_makina_share': 0.4,
                    'yield_apr': 0.05,
                    'net_return_margin': 0.7,
                },
                {
                    'name': 'DUSD',
                    'currency': 'USD',
                    'launch_date': None,
                    'initial_aum': 55000000.0,
                    'monthly_growth_rate': 0.1,
                    'management_fee_total': 0.01,
                    'management_fee_makina_share': 0.4,
                    'performance_fee_total': 0.15,
                    'performance_fee_makina_share': 0.4,
                    'yield_apr': 0.08,
                    'net_return_margin': 0.7,
                },
                {
                    'name': 'DBIT',
                    'currency': 'BTC',
                    'launch_date': None,
                    'initial_aum': 200.0,
                    'monthly_growth_rate': 0.1,
                    'management_fee_total': 0.005,
                    'management_fee_makina_share': 0.4,
                    'performance_fee_total': 0.1,
                    'performance_fee_makina_share': 0.4,
                    'yield_apr': 0.03,
                    'net_return_margin': 0.7,
                },
                {
                    'name': 'Lido',
                    'currency': 'USD',
                    'launch_date': date(2026, 2, 1),
                    'initial_aum': 400000000.0,
                    'monthly_growth_rate': 0.0,
                    'management_fee_total': 0.0015,
                    'management_fee_makina_share': 0.1153846154,
                    'performance_fee_total': 0.13,
                    'performance_fee_makina_share': 0.1153846154,
                    'yield_apr': 0.08,
                    'net_return_margin': 0.7,
                },
                {
                    'name': 'DNEW 1',
                    'currency': 'USD',
                    'launch_date': date(2026, 4, 1),
                    'initial_aum': 55000000.0,
                    'monthly_growth_rate': 0.1,
                    'management_fee_total': 0.0075,
                    'management_fee_makina_share': 0.4,
                    'performance_fee_total': 0.15,
                    'performance_fee_makina_share': 0.4,
                    'yield_apr': 0.08,
                    'net_return_margin': 0.7,
                },
                {
                    'name': 'DNEW 2',
                    'currency': 'USD',
                    'launch_date': date(2026, 5, 1),
                    'initial_aum': 55000000.0,
                    'monthly_growth_rate': 0.1,
                    'management_fee_total': 0.0075,
                    'management_fee_makina_share': 0.4,
                    'performance_fee_total': 0.15,
                    'performance_fee_makina_share': 0.4,
                    'yield_apr': 0.08,
                    'net_return_margin': 0.7,
                },
                {
                    'name': 'DNEW 3',
                    'currency': 'USD',
                    'launch_date': date(2026, 6, 1),
                    'initial_aum': 55000000.0,
                    'monthly_growth_rate': 0.1,
                    'management_fee_total': 0.0075,
                    'management_fee_makina_share': 0.4,
                    'performance_fee_total': 0.15,
                    'performance_fee_makina_share': 0.4,
                    'yield_apr': 0.08,
                    'net_return_margin': 0.7,
                },
            ]

            for machine_data in machines:
                machine = Machine(scenario_id=base_case.id, **machine_data)
                session.add(machine)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_machines_snapshot(self, scenario_id):
        """Save current machines as a snapshot for reset functionality"""
        session = self.get_session()
        try:
            machines = session.query(Machine).filter_by(scenario_id=scenario_id).all()
            snapshot = []
            for m in machines:
                snapshot.append({
                    'name': m.name,
                    'currency': m.currency,
                    'launch_date': m.launch_date,
                    'initial_aum': m.initial_aum,
                    'monthly_growth_rate': m.monthly_growth_rate,
                    'management_fee_total': m.management_fee_total,
                    'management_fee_makina_share': m.management_fee_makina_share,
                    'performance_fee_total': m.performance_fee_total,
                    'performance_fee_makina_share': m.performance_fee_makina_share,
                    'yield_apr': m.yield_apr,
                    'net_return_margin': m.net_return_margin,
                })
            return snapshot
        finally:
            session.close()

    def restore_machines_snapshot(self, scenario_id, snapshot):
        """Restore machines from a snapshot"""
        session = self.get_session()
        try:
            # Delete all current machines
            session.query(Machine).filter_by(scenario_id=scenario_id).delete()

            # Recreate machines from snapshot
            for machine_data in snapshot:
                machine = Machine(scenario_id=scenario_id, **machine_data)
                session.add(machine)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_active_scenario(self):
        """Get the currently active scenario"""
        session = self.get_session()
        try:
            return session.query(Scenario).filter_by(is_active=True).first()
        finally:
            session.close()

    def get_all_scenarios(self):
        """Get all scenarios"""
        session = self.get_session()
        try:
            return session.query(Scenario).all()
        finally:
            session.close()

    def get_machines_for_scenario(self, scenario_id):
        """Get all machines for a scenario"""
        session = self.get_session()
        try:
            return session.query(Machine).filter_by(scenario_id=scenario_id).all()
        finally:
            session.close()
