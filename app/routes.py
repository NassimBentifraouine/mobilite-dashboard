from flask import render_template, request, jsonify, send_file, current_app
from app.analysis import MobilityAnalyzer
from app.visualizations import MobilityVisualizer
from app.utils import export_to_csv, export_to_pdf
import os
from datetime import datetime

analyzer = None
visualizer = MobilityVisualizer()


def register_routes(app):
    global analyzer

    analyzer = MobilityAnalyzer(app.config['DATA_FOLDER'])

    @app.before_request
    def load_data():
        if analyzer.df_merged is None:
            if analyzer.load_data():
                analyzer.clean_data()
                analyzer.merge_data()

    @app.route('/')
    def index():

        indicators = analyzer.calculate_indicators()

        departments = analyzer.get_departments_list()

        transport_chart = visualizer.create_transport_distribution(analyzer.df_merged)
        commute_chart = visualizer.create_commute_time_histogram(analyzer.df_merged)
        zone_chart = visualizer.create_zone_comparison(analyzer.df_merged)

        return render_template(
            'index.html',
            indicators=indicators,
            departments=departments,
            transport_chart=transport_chart,
            commute_chart=commute_chart,
            zone_chart=zone_chart
        )

    @app.route('/carte')
    def carte():

        department = request.args.get('department', 'all')
        zone_type = request.args.get('zone_type', 'all')

        df_filtered = analyzer.df_merged.copy()

        if department != 'all':
            df_filtered = analyzer.filter_by_department(department)

        if zone_type != 'all':
            df_filtered = analyzer.filter_by_zone_type(zone_type)

        map_html = visualizer.create_map(df_filtered)

        departments = analyzer.get_departments_list()

        return render_template(
            'carte.html',
            map_html=map_html,
            departments=departments,
            selected_department=department,
            selected_zone_type=zone_type
        )

    @app.route('/analyse')
    def analyse():

        df_agg = analyzer.get_aggregated_by_department()

        df_underserved = analyzer.get_top_underserved(10)

        chart = ""
        if not df_agg.empty:
            chart = visualizer.create_bar_chart(
                df_agg,
                'departement',
                'temps_moyen_trajet',
                'Temps moyen de trajet par département',
                'Département',
                'Temps (minutes)'
            )

        departments = analyzer.get_departments_list()

        return render_template(
            'analyse.html',
            df_agg=df_agg,
            df_underserved=df_underserved,
            chart=chart,
            departments=departments
        )

    @app.route('/export/csv')
    def export_csv_route():
        department = request.args.get('department', 'all')

        df_export = analyzer.df_merged.copy()
        if department != 'all':
            df_export = analyzer.filter_by_department(department)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mobilite_export_{timestamp}"

        filepath = export_to_csv(df_export, filename, current_app.config['EXPORTS_FOLDER'])

        return send_file(filepath, as_attachment=True)

    @app.route('/export/pdf')
    def export_pdf_route():
        department = request.args.get('department', 'all')

        df_filtered = analyzer.df_merged.copy()
        department_name = "Tous"

        if department != 'all':
            df_filtered = analyzer.filter_by_department(department)
            department_name = department

        temp_analyzer = MobilityAnalyzer(current_app.config['DATA_FOLDER'])
        temp_analyzer.df_merged = df_filtered

        indicators = temp_analyzer.calculate_indicators()

        df_summary = temp_analyzer.get_aggregated_by_department()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"rapport_mobilite_{timestamp}"

        filepath = export_to_pdf(
            indicators,
            df_summary,
            filename,
            current_app.config['EXPORTS_FOLDER'],
            department_name
        )

        return send_file(filepath, as_attachment=True)

    @app.route('/api/indicators')
    def api_indicators():
        department = request.args.get('department', 'all')

        df_filtered = analyzer.df_merged.copy()
        if department != 'all':
            df_filtered = analyzer.filter_by_department(department)

        temp_analyzer = MobilityAnalyzer(current_app.config['DATA_FOLDER'])
        temp_analyzer.df_merged = df_filtered

        indicators = temp_analyzer.calculate_indicators()

        return jsonify(indicators)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500
