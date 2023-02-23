from dash import dcc, html
from dash.dependencies import Input, Output, State
from ..error import ZeroEnergyFlowError
from ..log import getLogger

from .widgets import get_analysis_and_field, OpgeePane, horiz_space

_logger = getLogger(__name__)

barchart_style = {"width": "440px", 'display': 'inline-block'}

_zero_flow_at_boundary_msg = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No figure",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 20
                }
            }
        ]
    }
}


class ResultsPane(OpgeePane):

    def get_layout(self, field, **kwargs):
        layout = html.Div([
            html.H3('Results'),
            html.Div('', id='ci-text',
                     className="row",
                     # style={'textAlign': "center"},
                     ),
            html.Center([
                dcc.Graph(id="ci-barchart",     style=barchart_style),
                horiz_space,
                dcc.Graph(id="energy-barchart", style=barchart_style)
                ]
            ),
        ], className="row",
            style={  # 'display': 'flex',
                'align-items': 'center',
                'textAlign': "center",
                'justify-content': 'center'
            }
        )
        return layout


    def add_callbacks(self):
        app = self.app
        model = self.model

        @app.callback(
            Output('ci-text', 'children'),
            Input('run-button', 'n_clicks'),
            Input('analysis-and-field', 'data'))
        def ci_text(n_clicks, analysis_and_field):
            analysis, field = get_analysis_and_field(model, analysis_and_field)

            try:
                ci = field.compute_carbon_intensity(analysis)
            except ZeroEnergyFlowError:
                return dcc.Markdown("**Cannot compute CI: zero energy flow at system boundary**")
                # from .. import ureg
                # _logger.warning(f"ci_text: {e}")
                # ci = ureg.Quantity(0, "grams/MJ")

            return f"CI: {ci.m:0.2f} g CO2e/MJ LHV of {analysis.fn_unit}"

        @app.callback(
            Output('ci-barchart', 'figure'),
            Input('ci-text', 'children'),           # ensures that we run after ci_text
            State('analysis-and-field', 'data'))
        def ci_barchart(ci_text, analysis_and_field):
            import pandas as pd
            import plotly.graph_objs as go

            analysis, field = get_analysis_and_field(model, analysis_and_field)

            # Show results for top-level aggregators and procs for the selected field
            top_level = model.partial_ci_values(analysis, field, field.children())

            if top_level is None:
                return _zero_flow_at_boundary_msg

            fn_unit = analysis.fn_unit.title()

            df = pd.DataFrame({"category": [pair[0] for pair in top_level],
                               "value": [pair[1] for pair in top_level],
                               "unit": [fn_unit] * len(top_level)})

            fig = go.Figure(data=[go.Bar(name=row.category,
                                         x=[row.unit],
                                         y=[row.value], width=[0.7]) for idx, row in df.iterrows()],
                            layout=go.Layout(barmode='stack'))

            fig.update_layout(yaxis_title=f"g CO2 per MJ of {fn_unit}",  # doesn't render in latex: r'g CO$_2$ MJ$^{-1}$',
                              xaxis_title='Carbon Intensity')

            return fig

        @app.callback(
            Output('energy-barchart', 'figure'),
            Input('run-button', 'n_clicks'),
            Input('ci-barchart', 'figure'),         # run this after CI barchart
            Input('analysis-and-field', 'data'))
        def energy_barchart(n_clicks, ci_figure, analysis_and_field):
            import pandas as pd
            import plotly.graph_objs as go

            analysis, field = get_analysis_and_field(model, analysis_and_field)

            # Identify procs / aggs outside the boundary of interest and subtract their energy use from total.
            try:
               energy = field.boundary_energy_flow_rate(analysis)
            except ZeroEnergyFlowError:
                return _zero_flow_at_boundary_msg

            fn_unit = analysis.fn_unit.title()
            boundary_proc = field.boundary_process(analysis)
            beyond = boundary_proc.beyond_boundary()

            # Show results for top-level aggregators and procs for the selected field that are within the boundary
            top_level = [(obj.name, obj.energy.data.sum()/energy) for obj in field.children() if obj not in beyond]

            df = pd.DataFrame({"category": [pair[0] for pair in top_level],
                               "value": [pair[1] for pair in top_level],
                               "unit": [fn_unit] * len(top_level)})

            fig = go.Figure(data=[go.Bar(name=row.category, x=[row.unit], y=[row.value.m], width=[0.7]) for idx, row in df.iterrows()],
                            layout=go.Layout(barmode='stack'))

            fig.update_layout(yaxis_title=f"MJ per MJ of {fn_unit}",
                              xaxis_title='Energy consumption')

            return fig
