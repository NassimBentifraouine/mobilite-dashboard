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
            print(f"Data loading error: {e}")
            return False

    def clean_data(self):
        if self.df_communes is not None:
            self.df_communes = self.df_communes.drop_duplicates(subset=['code_commune'])
            self.df_communes['population'] = self.df_communes['population'].fillna(0)

        if self.df_transport is not None:
            self.df_transport = self.df_transport.drop_duplicates()
            cols = ['temps_moyen_trajet', 'taux_velo', 'taux_transport_commun', 'taux_voiture']
            for col in cols:
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
            
            # Mocking age data (manque dans les fichiers csv actuels)
            # TODO: replace with real INSEE data later
            np.random.seed(42) 
            self.df_merged['classe_age_dominante'] = np.random.choice(
                ['Jeunes', 'Actifs', 'Seniors'], 
                size=len(self.df_merged), 
                p=[0.3, 0.5, 0.2]
            )

    def calculate_indicators(self) -> Dict:
        if self.df_merged is None or self.df_merged.empty:
            return {}

        return {
            'taux_couverture_transport': self._calc_coverage(),
            'temps_moyen_domicile_travail': self._calc_avg_time(),
            'taux_mobilite_verte': self._calc_green_rate(),
            'nb_zones_mal_desservies': self._count_underserved(),
            'population_totale': int(self.df_merged['population'].sum()),
            'nb_communes': len(self.df_merged)
        }

    def _calc_coverage(self) -> float:
        if 'a_acces_transport' not in self.df_merged.columns: return 0
        total = self.df_merged['population'].sum()
        access = self.df_merged[self.df_merged['a_acces_transport'] == True]['population'].sum()
        return round((access / total * 100), 2) if total > 0 else 0

    def _calc_avg_time(self) -> float:
        if 'temps_moyen_trajet' not in self.df_merged.columns: return 0
        total = self.df_merged['population'].sum()
        if total == 0: return 0
        weighted = (self.df_merged['temps_moyen_trajet'] * self.df_merged['population']).sum() / total
        return round(weighted, 1)

    def _calc_green_rate(self) -> float:
        cols = ['taux_velo', 'taux_transport_commun']
        if not all(col in self.df_merged.columns for col in cols): return 0
        total = self.df_merged['population'].sum()
        if total == 0: return 0
        rate = ((self.df_merged['taux_velo'] + self.df_merged['taux_transport_commun']) * self.df_merged['population']).sum() / total
        return round(rate, 2)

    def _count_underserved(self) -> int:
        if 'a_acces_transport' in self.df_merged.columns:
            return len(self.df_merged[self.df_merged['a_acces_transport'] == False])
        return 0

    def filter_by_department(self, dept: str) -> pd.DataFrame:
        if self.df_merged is None: return pd.DataFrame()
        return self.df_merged[self.df_merged['departement'] == dept].copy() if dept and dept != 'all' else self.df_merged.copy()

    def filter_by_zone_type(self, df: pd.DataFrame, zone: str) -> pd.DataFrame:
        if df is None or df.empty or not zone or zone == 'all': return df
        return df[df['type_zone'] == zone].copy()

    def filter_by_age_class(self, df: pd.DataFrame, age: str) -> pd.DataFrame:
        if df is None or df.empty or not age or age == 'all': return df
        return df[df['classe_age_dominante'] == age].copy()
    
    def filter_by_transport_pref(self, df: pd.DataFrame, transport: str) -> pd.DataFrame:
        if df is None or df.empty or not transport or transport == 'all': return df
        thresholds = {'velo': ('taux_velo', 10), 'commun': ('taux_transport_commun', 40), 'voiture': ('taux_voiture', 60)}
        if transport in thresholds:
            col, val = thresholds[transport]
            return df[df[col] > val].copy()
        return df

    def get_departments_list(self) -> List[str]:
        return sorted(self.df_merged['departement'].unique().tolist()) if self.df_merged is not None else []

    def get_aggregated_by_department(self) -> pd.DataFrame:
        if self.df_merged is None: return pd.DataFrame()
        aggs = {'population': 'sum', 'temps_moyen_trajet': 'mean', 'taux_velo': 'mean', 'taux_transport_commun': 'mean'}
        return self.df_merged.groupby('departement').agg({k:v for k,v in aggs.items() if k in self.df_merged.columns}).round(2).reset_index()

    def get_top_underserved(self, n: int = 10) -> pd.DataFrame:
        if self.df_merged is None: return pd.DataFrame()
        df = self.df_merged.copy()
        median_time = df['temps_moyen_trajet'].median()
        bad_zones = df[(df['a_acces_transport'] == False) | (df['temps_moyen_trajet'] > median_time)]
        return bad_zones.sort_values('population', ascending=False).head(n)