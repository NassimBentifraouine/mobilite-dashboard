from flask import render_template, request, jsonify, send_file, current_app
from app.analysis import MobilityAnalyzer
from app.visualizations import MobilityVisualizer
from app.utils import export_to_csv, export_to_pdf
from datetime import datetime
import os

analyzer = None
visualizer = MobilityVisualizer()

def register_routes(app):
    global analyzer
    analyzer = MobilityAnalyzer(app.config['DATA_FOLDER'])

    @app.before_request
    def ensure_data_loaded():
        if analyzer.df_merged is None:
            if analyzer.load_data():
                analyzer.clean_data()
                analyzer.merge_data()

    @app.route('/')
    def index():
        return render_template(
            'index.html',
            indicators=analyzer.calculate_indicators(),
            departments=analyzer.get_departments_list(),
            transport_chart=visualizer.create_transport_distribution(analyzer.df_merged),
            commute_chart=visualizer.create_commute_time_histogram(analyzer.df_merged),
            zone_chart=visualizer.create_zone_comparison(analyzer.df_merged)
        )

    @app.route('/carte')
    def carte():
        dept = request.args.get('department', 'all')
        zone = request.args.get('zone_type', 'all')
        age = request.args.get('age_class', 'all')
        transport = request.args.get('transport_type', 'all')

        df = analyzer.filter_by_department(dept)
        df = analyzer.filter_by_zone_type(df, zone)
        df = analyzer.filter_by_age_class(df, age)
        df = analyzer.filter_by_transport_pref(df, transport)

        return render_template(
            'carte.html',
            map_html=visualizer.create_map(df),
            departments=analyzer.get_departments_list(),
            selected_department=dept,
            selected_zone_type=zone,
            selected_age_class=age,
            selected_transport_type=transport
        )

    @app.route('/analyse')
    def analyse():
        agg = analyzer.get_aggregated_by_department()
        chart = visualizer.create_bar_chart(agg, 'departement', 'temps_moyen_trajet', 'Temps Trajet par Dept', 'Dept', 'Min') if not agg.empty else ""
        return render_template(
            'analyse.html',
            df_agg=agg,
            df_underserved=analyzer.get_top_underserved(10),
            chart=chart,
            departments=analyzer.get_departments_list()
        )

    @app.route('/export/csv')
    def export_csv():
        dept = request.args.get('department', 'all')
        df = analyzer.filter_by_department(dept)
        fname = f"export_{datetime.now().strftime('%Y%m%d_%H%M')}"
        path = export_to_csv(df, fname, current_app.config['EXPORTS_FOLDER'])
        return send_file(path, as_attachment=True)

    @app.route('/export/pdf')
    def export_pdf():
        dept = request.args.get('department', 'all')
        df = analyzer.filter_by_department(dept)
        
        # Temp analyzer
        tmp_analyzer = MobilityAnalyzer(current_app.config['DATA_FOLDER'])
        tmp_analyzer.df_merged = df
        
        fname = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M')}"
        path = export_to_pdf(
            tmp_analyzer.calculate_indicators(),
            tmp_analyzer.get_aggregated_by_department(),
            fname,
            current_app.config['EXPORTS_FOLDER'],
            dept if dept != 'all' else "National"
        )
        return send_file(path, as_attachment=True)

    @app.errorhandler(404)
    def not_found(e): return render_template('404.html'), 404

    @app.errorhandler(500)
    def error(e): return render_template('500.html'), 500