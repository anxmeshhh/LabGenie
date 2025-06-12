from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import re
import logging
from database import init_db, save_experiment, get_all_experiments, get_experiment_by_id
from gemini_api import generate_lab_record
from export_utils import export_to_docx, export_to_pdf
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for Matplotlib
import matplotlib.pyplot as plt
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
app.config['UPLOAD_FOLDER'] = 'records'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit request size to 16MB

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        experiment_description = request.form.get('experiment_description', '').strip()
        # Validate experiment description
        if not experiment_description:
            flash("Experiment description cannot be empty.", 'error')
            raise ValueError("Experiment description is required")

        readings = request.form.get('readings', '').strip()
        # Parse readings (format: x1,y1;x2,y2;...)
        readings_data = []
        if not readings:
            flash("Readings cannot be empty.", 'error')
            raise ValueError("Readings are required")
        
        for r in readings.split(';'):
            if not r:
                continue
            try:
                x, y = map(float, r.split(','))
                if x < -1e6 or x > 1e6 or y < -1e6 or y > 1e6:
                    flash(f"Reading values too large or too small: {r}", 'error')
                    raise ValueError("Reading values must be within reasonable bounds")
                readings_data.append((x, y))
            except ValueError:
                flash(f"Invalid readings format: {r}. Use format x,y;x,y;...", 'error')
                raise ValueError(f"Invalid readings format: {r}")
        
        if not readings_data:
            flash("No valid readings provided.", 'error')
            raise ValueError("At least one valid reading pair is required")
        
        logger.info(f"Processing experiment: {experiment_description} with readings: {readings}")
        
        # Generate lab record using Gemini
        try:
            lab_record = generate_lab_record(experiment_description, readings_data)
            logger.info("Lab record generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate lab record: {str(e)}")
            flash(f"Error generating lab record: {str(e)}", 'error')
            raise
        
        # Generate graph
        try:
            graph_path = generate_graph(readings_data, experiment_description, lab_record.get('x_label', 'X'), lab_record.get('y_label', 'Y'))
            logger.info("Graph generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate graph: {str(e)}")
            flash(f"Error generating graph: {str(e)}", 'error')
            raise
        
        # Save to database
        try:
            experiment_id = save_experiment(experiment_description, readings, lab_record, graph_path)
            logger.info(f"Experiment saved with ID: {experiment_id}")
        except Exception as e:
            logger.error(f"Failed to save experiment to database: {str(e)}")
            flash(f"Error saving experiment: {str(e)}", 'error')
            raise
        
        flash('Experiment record generated and saved successfully!', 'success')
        return redirect(url_for('view_record', experiment_id=experiment_id))
    
    except Exception as e:
        logger.error(f"Error in submit route: {str(e)}")
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    try:
        experiments = get_all_experiments()
        logger.info(f"Retrieved {len(experiments)} experiments for dashboard")
        return render_template('dashboard.html', experiments=experiments)
    except Exception as e:
        logger.error(f"Error fetching experiments: {str(e)}")
        flash(f"Error loading dashboard: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/record/<int:experiment_id>')
def view_record(experiment_id):
    try:
        experiment = get_experiment_by_id(experiment_id)
        if not experiment:
            logger.warning(f"Experiment ID {experiment_id} not found")
            flash('Experiment not found!', 'error')
            return redirect(url_for('dashboard'))
        logger.info(f"Displaying record for experiment ID: {experiment_id}")
        return render_template('record.html', experiment=experiment)
    except Exception as e:
        logger.error(f"Error viewing record {experiment_id}: {str(e)}")
        flash(f"Error viewing record: {str(e)}", 'error')
        return redirect(url_for('dashboard'))

@app.route('/export/<int:experiment_id>/<format>')
def export(experiment_id, format):
    try:
        experiment = get_experiment_by_id(experiment_id)
        if not experiment:
            logger.warning(f"Experiment ID {experiment_id} not found for export")
            flash('Experiment not found!', 'error')
            return redirect(url_for('dashboard'))
        
        if format not in ['docx', 'pdf']:
            logger.warning(f"Invalid export format: {format}")
            flash('Unsupported export format!', 'error')
            return redirect(url_for('view_record', experiment_id=experiment_id))
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'experiment_{experiment_id}.{format}')
        
        logger.info(f"Exporting experiment ID {experiment_id} to {format}")
        if format == 'docx':
            export_to_docx(experiment, file_path)
        elif format == 'pdf':
            export_to_pdf(experiment, file_path)
        
        return send_file(file_path, as_attachment=True, download_name=f'experiment_{experiment_id}.{format}')
    except Exception as e:
        logger.error(f"Error exporting experiment {experiment_id} to {format}: {str(e)}")
        flash(f"Error exporting file: {str(e)}", 'error')
        return redirect(url_for('view_record', experiment_id=experiment_id))

def generate_graph(readings_data, experiment_description, x_label, y_label):
    try:
        if not readings_data:
            raise ValueError("No data provided for graph")
        
        x, y = zip(*readings_data)
        plt.figure(figsize=(8, 6))
        plt.plot(x, y, 'o-', markersize=5, linewidth=2)
        plt.title(f'{experiment_description} - Readings', fontsize=14)
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True)
        
        # Save to bytes buffer and encode to base64 for HTML display
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        graph_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        return graph_data
    except Exception as e:
        logger.error(f"Graph generation failed: {str(e)}")
        raise Exception(f"Failed to generate graph: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)