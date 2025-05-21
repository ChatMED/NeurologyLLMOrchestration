from typing_extensions import List

from db_store import NeurologyReportRecord, PredictedNeurologyReportRecord


class ReportViewModel:
    def __init__(self, actual_report: NeurologyReportRecord, predicted_report: PredictedNeurologyReportRecord,
                 all_predicted_reports: List[PredictedNeurologyReportRecord]):
        self.actual_report = actual_report
        self.predicted_report = predicted_report
        self.all_predicted_reports = all_predicted_reports
