from db_store import NeurologyReportRecord, PredictedNeurologyReportRecord


class ReportViewModel:
    def __init__(self, actual_report: NeurologyReportRecord, predicted_report: PredictedNeurologyReportRecord):
        self.actual_report = actual_report
        self.predicted_report = predicted_report