from flask import Blueprint, render_template, current_app

import pandas as pd
import json
import plotly
import plotly.express as px


dashboard_blueprint = Blueprint('dashboard', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

@dashboard_blueprint.route('/')
def db_blueprint_dashboard():

    print(current_app.config['loggedin'])

    if current_app.config['loggedin'] == 'false':
        return render_template('login.html')

    else:
        sample_data = pd.DataFrame({
                "Vegetables": ["Lettuce", "Cauliflower", "Carrots", "Lettuce", "Cauliflower", "Carrots"],
                "Amount": [10, 15, 8, 5, 14, 25],
                "City": ["London", "London", "London", "Madrid", "Madrid", "Madrid"]
            })

        fig = px.bar(sample_data, x="Vegetables", y="Amount", color="City", barmode="stack")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('dashboard.html', graphJSON=graphJSON)
