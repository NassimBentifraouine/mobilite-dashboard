from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os


class PDFReport(FPDF):

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Rapport d\'analyse de mobilité', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_indicator(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.cell(80, 8, label + ':', 0, 0)
        self.set_font('Arial', '', 10)
        self.cell(0, 8, str(value), 0, 1)


def export_to_csv(df: pd.DataFrame, filename: str, output_path: str) -> str:

    filepath = os.path.join(output_path, f"{filename}.csv")
    df.to_csv(filepath, index=False, encoding='utf-8')
    return filepath


def export_to_pdf(indicators: dict, df_summary: pd.DataFrame,
                  filename: str, output_path: str, department: str = "Tous") -> str:

    pdf = PDFReport()
    pdf.add_page()

    pdf.chapter_title('Informations générales')
    pdf.add_indicator('Date du rapport', datetime.now().strftime('%d/%m/%Y %H:%M'))
    pdf.add_indicator('Département', department)
    pdf.ln(5)

    pdf.chapter_title('Indicateurs clés')

    if 'population_totale' in indicators:
        pdf.add_indicator('Population totale', f"{indicators['population_totale']:,}")

    if 'nb_communes' in indicators:
        pdf.add_indicator('Nombre de communes', indicators['nb_communes'])

    if 'taux_couverture_transport' in indicators:
        pdf.add_indicator('Taux de couverture transport',
                         f"{indicators['taux_couverture_transport']}%")

    if 'temps_moyen_domicile_travail' in indicators:
        pdf.add_indicator('Temps moyen domicile-travail',
                         f"{indicators['temps_moyen_domicile_travail']} minutes")

    if 'taux_mobilite_verte' in indicators:
        pdf.add_indicator('Taux de mobilité verte',
                         f"{indicators['taux_mobilite_verte']}%")

    if 'nb_zones_mal_desservies' in indicators:
        pdf.add_indicator('Zones mal desservies',
                         indicators['nb_zones_mal_desservies'])

    pdf.ln(5)

    if not df_summary.empty:
        pdf.chapter_title('Récapitulatif par département')

        pdf.set_font('Arial', 'B', 9)
        col_width = 35
        pdf.cell(col_width, 8, 'Département', 1, 0, 'C')
        pdf.cell(col_width, 8, 'Population', 1, 0, 'C')
        pdf.cell(col_width, 8, 'Temps trajet', 1, 0, 'C')
        pdf.cell(col_width, 8, 'Taux vélo', 1, 1, 'C')

        pdf.set_font('Arial', '', 8)
        for idx, row in df_summary.head(10).iterrows():
            pdf.cell(col_width, 7, str(row.get('departement', '')), 1, 0, 'L')
            pdf.cell(col_width, 7, f"{int(row.get('population', 0)):,}", 1, 0, 'R')
            pdf.cell(col_width, 7, f"{row.get('temps_moyen_trajet', 0):.1f} min", 1, 0, 'R')
            pdf.cell(col_width, 7, f"{row.get('taux_velo', 0):.1f}%", 1, 1, 'R')

    pdf.ln(10)
    pdf.chapter_title('Notes')
    pdf.chapter_body(
        'Ce rapport présente une analyse des inégalités de mobilité basée sur les données '
        'disponibles. Les indicateurs permettent d\'identifier les zones nécessitant '
        'des améliorations en matière d\'infrastructures de transport.'
    )

    filepath = os.path.join(output_path, f"{filename}.pdf")
    pdf.output(filepath)

    return filepath


def format_number(value, decimals=0):

    if pd.isna(value):
        return "N/A"

    if decimals == 0:
        return f"{int(value):,}".replace(',', ' ')
    else:
        return f"{value:,.{decimals}f}".replace(',', ' ')
