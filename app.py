import json
from idlelib.query import Query
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from db_store import SessionLocal, PredictedNeurologyReportRecord, ReportSummary, get_db, NeurologyReportRecord
from history_retrieval import generate_neurology_report

from fastapi import FastAPI, Depends, Request

from view_models import ReportViewModel

app = FastAPI(title="Neurology Report API")

templates = Jinja2Templates(directory="templates")


@app.get("/reports/add", summary="Submit a neurology report", status_code=201)
def create_neurology_report():
    db = SessionLocal()
    try:
        anamnesa = """
        A 16-year-old girl was reviewed for two seizures that had
occurred 5!days apart. She had a history of mild learning difficulties
related to foetal valproate syndrome, and there was
a strong family history of epilepsy, with her mother, father,
and two cousins all suffering from epilepsy. The patient had
experienced febrile convulsions in childhood.
The recent two seizures had occurred within 48! hours in
the context of a severe viral infection, accompanied by symptoms
of nausea, vomiting, and high fever. She was reviewed
more than 24!hours after the second seizure. At that time she
had been afebrile for 24!hours and had subjectively felt much
better. Patient had very poor recollection of the events surrounding
the seizures, and according to her mother, she had
been found unconscious in bed with some evidence of seizure
activity (for about 1!min). There had been no evidence of bitten
tongue or incontinence, and the patient had seemed tired
and had wanted to rest after regaining consciousness. The
mother had not reported any significant post-ictal phase.
Blood tests at the time of admission were normal.
On objective examination, all findings had been normal.
The patient had expressed some reluctance to initiate antiepileptic
drug (AED) therapy and had requested neurology
opinion.
"""
        report = generate_neurology_report(anamnesa)
        report_record = PredictedNeurologyReportRecord(
            id=2,
            name="Chapter 19 Two Seizures and!Strong Family History of!Epilepsy",
            summary=report.compressed_summary,
            full_report=json.loads(report.model_dump_json()),
            real_report_id=1
        )

        db.add(report_record)
        db.commit()
        db.refresh(report_record)
        return {"id": report_record.id, "message": "Report saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    reports = db.query(NeurologyReportRecord).order_by(NeurologyReportRecord.created_at.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "reports": reports})


@app.get("/report/create", response_class=HTMLResponse)
def create_report_form(request: Request):
    return templates.TemplateResponse("create_report.html", {"request": request})


@app.post("/report/create")
def create_report(
        request: Request,
        case_name: str = Form(...),
        anamnesis: str = Form(...),
        db: Session = Depends(get_db)
):
    from db_store import PredictedNeurologyReportRecord
    import json

    report = generate_neurology_report(anamnesis)
    report = PredictedNeurologyReportRecord(
        name=case_name,
        summary=report.compressed_summary,
        full_report=json.loads(report.model_dump_json())
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return RedirectResponse(url=f"/report/{report.id}", status_code=303)


@app.get("/reports", response_model=List[ReportSummary])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(NeurologyReportRecord).order_by(NeurologyReportRecord.created_at.desc()).all()
    return reports


@app.get("/reports/{report_id}", response_class=JSONResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(NeurologyReportRecord).filter(NeurologyReportRecord.id == report_id).first()
    if report:
        return report.full_report
    return JSONResponse(status_code=404, content={"error": "Report not found"})


@app.get("/report/{report_id}", response_class=HTMLResponse)
def view_report(report_id: int, request: Request, db: Session = Depends(get_db),
                predicted_report_id: Optional[int] = None):
    actual_report = db.query(NeurologyReportRecord).filter(
        NeurologyReportRecord.id == report_id
    ).first()

    if not actual_report:
        return HTMLResponse(content="Report not found", status_code=404)

    # Fetch all predicted records for this report ID once
    all_predicted_records = db.query(PredictedNeurologyReportRecord).filter(
        PredictedNeurologyReportRecord.real_report_id == report_id
    ).all()

    # Select the predicted report from the fetched list
    if predicted_report_id:
        predicted_report = next(
            (r for r in all_predicted_records if r.id == predicted_report_id), None
        )
    else:
        predicted_report = all_predicted_records[0] if all_predicted_records else None

    if not predicted_report:
        return HTMLResponse(content="Report not found", status_code=404)

    view_model = ReportViewModel(
        actual_report=actual_report,
        predicted_report=predicted_report,
        all_predicted_reports=all_predicted_records
    )

    return templates.TemplateResponse("report_detail.html", {
        "request": request,
        "report": view_model
    })

# @app.get("/report/{actual_report_id}", response_class=HTMLResponse)
# def view_report(
#     actual_report_id: int,
#     request: Request,
#     predicted_report_id: Optional[int] = Query,
#     db: Session = Depends(get_db)
# ):
#     # Get the actual report
#     actual_report = db.query(NeurologyReportRecord).filter(
#         NeurologyReportRecord.id == actual_report_id
#     ).first()
#
#     if not actual_report:
#         raise HTTPException(status_code=404, detail="Actual report not found")
#
#     # Get the predicted report
#     if predicted_report_id is not None:
#         predicted_report = db.query(PredictedNeurologyReportRecord).filter(
#             PredictedNeurologyReportRecord.id == predicted_report_id,
#             PredictedNeurologyReportRecord.actual_report_id == actual_report_id
#         ).first()
#     else:
#         predicted_report = db.query(PredictedNeurologyReportRecord).filter(
#             PredictedNeurologyReportRecord.actual_report_id == actual_report_id
#         ).order_by(PredictedNeurologyReportRecord.id).first()
#
#     if not predicted_report:
#         raise HTTPException(status_code=404, detail="Predicted report not found")
#
#     view_model = ReportViewModel(actual_report, predicted_report)
#
#     return templates.TemplateResponse("report_detail.html", {
#         "request": request,
#         "view_model": view_model
#     })

@app.post("/report/{report_id}/delete")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(NeurologyReportRecord).filter(NeurologyReportRecord.id == report_id).first()
    if not report:
        return HTMLResponse(content="Report not found", status_code=404)

    db.delete(report)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
