import folium
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from typing import Optional


class MobilityVisualizer:

    def __init__(self):

        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10

    def create_map(self, df: pd.DataFrame, center_lat: float = 46.603354,
                   center_lon: float = 1.888334, zoom_start: int = 6) -> str:
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )

        if df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
            return m._repr_html_()

        for idx, row in df.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                color = 'red' if not row.get('a_acces_transport', True) else 'green'

                taux_vert = row.get('taux_velo', 0) + row.get('taux_transport_commun', 0)

                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4>{row['nom_commune']}</h4>
                    <p><b>Population:</b> {int(row['population']):,}</p>
                    <p><b>Type:</b> {row.get('type_zone', 'N/A')}</p>
                    <p><b>Temps moyen trajet:</b> {row.get('temps_moyen_trajet', 0):.1f} min</p>
                    <p><b>Mobilité verte:</b> {taux_vert:.1f}%</p>
                </div>
                """

                radius = min(max(row['population'] / 100, 5), 20)

                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=250),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.6,
                    tooltip=row['nom_commune']
                ).add_to(m)

        return m._repr_html_()

    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str,
                        title: str, xlabel: str, ylabel: str) -> str:

        fig, ax = plt.subplots(figsize=(12, 6))

        if not df.empty and x_col in df.columns and y_col in df.columns:
            df_plot = df.head(15)

            ax.bar(df_plot[x_col], df_plot[y_col], color='steelblue', alpha=0.7)
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

        return self._fig_to_base64(fig)

    def create_transport_distribution(self, df: pd.DataFrame) -> str:

        fig, ax = plt.subplots(figsize=(10, 6))

        if not df.empty:
            total_pop = df['population'].sum()

            if total_pop > 0:
                transport_data = {
                    'Vélo': (df['taux_velo'] * df['population']).sum() / total_pop,
                    'Transport en commun': (df['taux_transport_commun'] * df['population']).sum() / total_pop,
                    'Voiture': (df['taux_voiture'] * df['population']).sum() / total_pop
                }

                colors = ['#2ecc71', '#3498db', '#e74c3c']
                ax.bar(transport_data.keys(), transport_data.values(), color=colors, alpha=0.7)
                ax.set_ylabel('Taux d\'utilisation (%)', fontsize=12)
                ax.set_title('Distribution des modes de transport', fontsize=14, fontweight='bold')
                ax.set_ylim(0, 100)

                for i, (k, v) in enumerate(transport_data.items()):
                    ax.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_commute_time_histogram(self, df: pd.DataFrame) -> str:

        fig, ax = plt.subplots(figsize=(10, 6))

        if not df.empty and 'temps_moyen_trajet' in df.columns:
            temps_data = df['temps_moyen_trajet'].dropna()
            temps_data = temps_data[temps_data > 0]

            if not temps_data.empty:
                ax.hist(temps_data, bins=30, color='coral', alpha=0.7, edgecolor='black')
                ax.set_xlabel('Temps de trajet (minutes)', fontsize=12)
                ax.set_ylabel('Nombre de communes', fontsize=12)
                ax.set_title('Distribution des temps de trajet domicile-travail',
                           fontsize=14, fontweight='bold')

                mean_time = temps_data.mean()
                ax.axvline(mean_time, color='red', linestyle='--', linewidth=2,
                          label=f'Moyenne: {mean_time:.1f} min')
                ax.legend()

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_zone_comparison(self, df: pd.DataFrame) -> str:

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        if not df.empty and 'type_zone' in df.columns:
            zone_stats = df.groupby('type_zone').agg({
                'temps_moyen_trajet': 'mean',
                'taux_velo': 'mean',
                'taux_transport_commun': 'mean'
            }).round(2)

            if not zone_stats.empty:
                zone_stats['temps_moyen_trajet'].plot(kind='bar', ax=axes[0],
                                                       color=['#3498db', '#e67e22'])
                axes[0].set_title('Temps moyen de trajet par type de zone',
                                fontweight='bold')
                axes[0].set_ylabel('Minutes')
                axes[0].set_xlabel('')
                axes[0].tick_params(axis='x', rotation=0)

                mobility_data = zone_stats[['taux_velo', 'taux_transport_commun']]
                mobility_data.plot(kind='bar', ax=axes[1], color=['#2ecc71', '#9b59b6'])
                axes[1].set_title('Mobilité verte par type de zone', fontweight='bold')
                axes[1].set_ylabel('Taux (%)')
                axes[1].set_xlabel('')
                axes[1].legend(['Vélo', 'Transport en commun'])
                axes[1].tick_params(axis='x', rotation=0)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig) -> str:

        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        plt.close(fig)

        return base64.b64encode(img.getvalue()).decode()
