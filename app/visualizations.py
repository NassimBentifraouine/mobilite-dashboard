import folium
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
import math

class MobilityVisualizer:

    def __init__(self):
        sns.set_style("whitegrid")
        plt.rcParams.update({'figure.figsize': (10, 6), 'font.size': 10})

    def create_map(self, df: pd.DataFrame, center=[46.603354, 1.888334], zoom=6) -> str:
        m = folium.Map(location=center, zoom_start=zoom, tiles='OpenStreetMap')

        if df.empty or 'latitude' not in df.columns: return m._repr_html_()

        for _, row in df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']): continue
                
            green_score = row.get('taux_velo', 0) + row.get('taux_transport_commun', 0)
            
            if not row.get('a_acces_transport', True): color = '#e74c3c'
            elif green_score > 50: color = '#2ecc71' 
            elif green_score > 25: color = '#f39c12' 
            else: color = '#e74c3c'

            popup = f"""
            <div style="font-family: sans-serif; width: 200px;">
                <h5 style="margin: 0 0 5px 0;">{row['nom_commune']}</h5>
                <p style="margin:0; font-size:12px;">Pop: {int(row['population']):,}</p>
                <p style="margin:0; font-size:12px;">Type: {row.get('type_zone', '-')}</p>
                <p style="margin:0; font-size:12px;">Age: {row.get('classe_age_dominante', '-')}</p>
                <div style="margin-top:5px; font-weight:bold; color:{color}">Green Score: {green_score:.0f}%</div>
            </div>
            """
            
            radius = min(max(math.log(row['population'] + 1) * 1.5, 4), 15)

            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=radius,
                popup=folium.Popup(popup, max_width=250),
                color=color, fill=True, fillColor=color, fillOpacity=0.7, weight=1
            ).add_to(m)

        return m._repr_html_()

    def create_bar_chart(self, df, x, y, title, xlab, ylab):
        fig, ax = plt.subplots(figsize=(12, 6))
        if not df.empty:
            data = df.head(15)
            ax.bar(data[x], data[y], color='steelblue', alpha=0.7)
            ax.set(xlabel=xlab, ylabel=ylab, title=title)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_transport_distribution(self, df):
        fig, ax = plt.subplots()
        if not df.empty and df['population'].sum() > 0:
            tot = df['population'].sum()
            data = {
                'Vélo': (df['taux_velo'] * df['population']).sum() / tot,
                'Commun': (df['taux_transport_commun'] * df['population']).sum() / tot,
                'Voiture': (df['taux_voiture'] * df['population']).sum() / tot
            }
            colors = ['#2ecc71', '#3498db', '#e74c3c']
            bars = ax.bar(data.keys(), data.values(), color=colors, alpha=0.7)
            ax.set(ylabel='Usage (%)', title='Mode de transport', ylim=(0, 100))
            for r in bars: ax.text(r.get_x()+r.get_width()/2, r.get_height()+1, f'{r.get_height():.1f}%', ha='center')
        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_commute_time_histogram(self, df):
        fig, ax = plt.subplots()
        if not df.empty:
            vals = df[df['temps_moyen_trajet'] > 0]['temps_moyen_trajet']
            ax.hist(vals, bins=30, color='coral', alpha=0.7, edgecolor='black')
            ax.set(xlabel='Min', ylabel='Count', title='Temps de trajet')
            ax.axvline(vals.mean(), color='red', linestyle='--', label=f'Mean: {vals.mean():.1f}')
            ax.legend()
        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_zone_comparison(self, df):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        if not df.empty:
            stats = df.groupby('type_zone')[['temps_moyen_trajet', 'taux_velo', 'taux_transport_commun']].mean()
            stats['temps_moyen_trajet'].plot(kind='bar', ax=ax1, color=['#3498db', '#e67e22'], rot=0)
            ax1.set(title='Temps Trajet', xlabel='')
            stats[['taux_velo', 'taux_transport_commun']].plot(kind='bar', ax=ax2, color=['#2ecc71', '#9b59b6'], rot=0)
            ax2.set(title='Mobilité Verte', xlabel='')
        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig):
        img = io.BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        plt.close(fig)
        return base64.b64encode(img.getvalue()).decode()