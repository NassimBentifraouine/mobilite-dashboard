from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os

class PDFReport(FPDF):
    
    def _clean(self, txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1') if txt else ""

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self._clean('Rapport Analyse Mobilité'), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, self._clean(title), 0, 1, 'L', 1)
        self.ln(2)

    def add_kpi(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.cell(70, 8, self._clean(f"{label}:"), 0, 0)
        self.set_font('Arial', '', 10)
        self.cell(0, 8, self._clean(str(value)), 0, 1)

def export_to_csv(df, filename, output_path):
    path = os.path.join(output_path, f"{filename}.csv")
    df.to_csv(path, index=False, encoding='utf-8-sig', sep=';')
    return path

def export_to_pdf(kpis, df_agg, filename, output_path, scope="Tous"):
    pdf = PDFReport()
    pdf.add_page()

    pdf.section_title('Infos Générales')
    pdf.add_kpi('Date', datetime.now().strftime('%d/%m/%Y'))
    pdf.add_kpi('Périmètre', scope)
    pdf.ln(5)

    pdf.section_title('Indicateurs Clés')
    if 'population_totale' in kpis: pdf.add_kpi('Population', f"{kpis['population_totale']:,}")
    if 'taux_couverture_transport' in kpis: pdf.add_kpi('Couverture Trans.', f"{kpis['taux_couverture_transport']}%")
    if 'taux_mobilite_verte' in kpis: pdf.add_kpi('Mobilité Verte', f"{kpis['taux_mobilite_verte']}%")
    pdf.ln(5)

    if not df_agg.empty:
        pdf.section_title('Top Départements')
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(50, 8, 'Dept', 1)
        pdf.cell(40, 8, 'Pop', 1)
        pdf.cell(40, 8, 'Temps (min)', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        for _, row in df_agg.head(15).iterrows():
            pdf.cell(50, 7, pdf._clean(str(row['departement'])), 1)
            pdf.cell(40, 7, f"{int(row['population']):,}", 1)
            pdf.cell(40, 7, f"{row['temps_moyen_trajet']:.1f}", 1)
            pdf.ln()

    path = os.path.join(output_path, f"{filename}.pdf")
    pdf.output(path)
    return path