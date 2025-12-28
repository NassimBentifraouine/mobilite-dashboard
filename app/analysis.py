import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class MobilityAnalyzer:

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df_communes = None
        self.df_transport = None
        self.df_merged = None

    def load_data(self):
        try:
            self.df_communes = pd.read_csv(f"{self.data_path}/communes.csv")
            self.df_transport = pd.read_csv(f"{self.data_path}/transport.csv")
            return True
        except FileNotFoundError as e:
            print(f"Erreur lors du chargement des données : {e}")
            return False

    def clean_data(self):
        if self.df_communes is not None:
            self.df_communes = self.df_communes.drop_duplicates(subset=['code_commune'])

            self.df_communes['population'] = self.df_communes['population'].fillna(0)

        if self.df_transport is not None:
            self.df_transport = self.df_transport.drop_duplicates()

            numeric_columns = ['temps_moyen_trajet', 'taux_velo', 'taux_transport_commun',
                             'taux_voiture']
            for col in numeric_columns:
                if col in self.df_transport.columns:
                    self.df_transport[col] = self.df_transport[col].fillna(0)

    def merge_data(self):
        if self.df_communes is not None and self.df_transport is not None:
            self.df_merged = pd.merge(
                self.df_communes,
                self.df_transport,
                on='code_commune',
                how='left'
            )

    def calculate_indicators(self) -> Dict:
        if self.df_merged is None or self.df_merged.empty:
            return {}

        indicators = {
            'taux_couverture_transport': self._calculate_coverage_rate(),
            'temps_moyen_domicile_travail': self._calculate_avg_commute_time(),
            'taux_mobilite_verte': self._calculate_green_mobility_rate(),
            'nb_zones_mal_desservies': self._count_underserved_zones(),
            'population_totale': int(self.df_merged['population'].sum()),
            'nb_communes': len(self.df_merged)
        }

        return indicators

    def _calculate_coverage_rate(self) -> float:
        if 'a_acces_transport' in self.df_merged.columns:
            total_pop = self.df_merged['population'].sum()
            pop_avec_acces = self.df_merged[
                self.df_merged['a_acces_transport'] == True
            ]['population'].sum()
            return round((pop_avec_acces / total_pop * 100), 2) if total_pop > 0 else 0
        return 0

    def _calculate_avg_commute_time(self) -> float:
        if 'temps_moyen_trajet' in self.df_merged.columns:
            total_pop = self.df_merged['population'].sum()
            if total_pop > 0:
                weighted_time = (
                    self.df_merged['temps_moyen_trajet'] * self.df_merged['population']
                ).sum() / total_pop
                return round(weighted_time, 1)
        return 0

    def _calculate_green_mobility_rate(self) -> float:
        if 'taux_velo' in self.df_merged.columns and 'taux_transport_commun' in self.df_merged.columns:
            total_pop = self.df_merged['population'].sum()
            if total_pop > 0:
                green_rate = (
                    (self.df_merged['taux_velo'] + self.df_merged['taux_transport_commun']) *
                    self.df_merged['population']
                ).sum() / total_pop
                return round(green_rate, 2)
        return 0

    def _count_underserved_zones(self) -> int:
        if 'a_acces_transport' in self.df_merged.columns:
            return len(self.df_merged[self.df_merged['a_acces_transport'] == False])
        return 0

    def filter_by_department(self, department: str) -> pd.DataFrame:
        if self.df_merged is None:
            return pd.DataFrame()

        if department and department != 'all':
            return self.df_merged[self.df_merged['departement'] == department].copy()
        return self.df_merged.copy()

    def filter_by_zone_type(self, zone_type: str) -> pd.DataFrame:
        if self.df_merged is None:
            return pd.DataFrame()

        if zone_type and zone_type != 'all':
            return self.df_merged[self.df_merged['type_zone'] == zone_type].copy()
        return self.df_merged.copy()

    def get_departments_list(self) -> List[str]:
        if self.df_merged is None:
            return []
        return sorted(self.df_merged['departement'].unique().tolist())

    def get_aggregated_by_department(self) -> pd.DataFrame:
        if self.df_merged is None:
            return pd.DataFrame()

        agg_dict = {
            'population': 'sum',
            'temps_moyen_trajet': 'mean',
            'taux_velo': 'mean',
            'taux_transport_commun': 'mean',
            'taux_voiture': 'mean'
        }

        agg_dict = {k: v for k, v in agg_dict.items() if k in self.df_merged.columns}

        df_agg = self.df_merged.groupby('departement').agg(agg_dict).round(2)
        df_agg = df_agg.reset_index()

        return df_agg

    def get_top_underserved(self, n: int = 10) -> pd.DataFrame:

        if self.df_merged is None:
            return pd.DataFrame()

        df_underserved = self.df_merged.copy()

        if 'a_acces_transport' in df_underserved.columns:
            df_underserved = df_underserved[
                (df_underserved['a_acces_transport'] == False) |
                (df_underserved['temps_moyen_trajet'] > df_underserved['temps_moyen_trajet'].median())
            ]

        df_underserved = df_underserved.sort_values('population', ascending=False)

        return df_underserved.head(n)
