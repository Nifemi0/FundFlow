"""
Test script for verifying the new PDF report format.
"""
import os
import sys

# Setup environment
os.environ['DATABASE_URL'] = 'postgresql://fundflow:fundflow@localhost:5432/fundflow'
os.environ['PYTHONPATH'] = '.'

from database.queries import get_db, get_project_full_info, search_projects
from utils.report_gen import PDFReportGenerator

def test_generate_report(project_name):
    db = get_db()
    try:
        projects = search_projects(db, project_name, limit=1)
        if not projects:
            print(f"Project {project_name} not found.")
            return
        
        project = projects[0]
        print(f"Generating report for {project.name} (ID: {project.id})...")
        
        project_info = get_project_full_info(db, project.id)
        generator = PDFReportGenerator()
        dossier = generator.map_project_to_dossier(project_info)
        pdf_buffer = generator.generate_project_report(dossier)
        
        filename = f"{project.slug}_test_report.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"Success! Report saved to {filename}")
        
    finally:
        db.close()

def test_emerging_report():
    from database.models import Project
    from unittest.mock import MagicMock
    
    mock_project = MagicMock(spec=Project)
    mock_project.name = "Stealth Protocol"
    mock_project.slug = "stealth_protocol"
    mock_project.category = "Privacy / Zero Knowledge"
    mock_project.sector = "Infrastructure"
    mock_project.description = None
    mock_project.github_url = None
    mock_project.github_stars = 0
    mock_project.github_contributors = None
    mock_project.stage = None
    mock_project.website = None
    mock_project.founded_date = None
    mock_project.tvl = None
    mock_project.dau = None
    mock_project.verification_source = "Web Research Mesh"
    
    project_info = {
        "project": mock_project,
        "funding_rounds": [],
        "team_members": [],
        "total_raised": 0
    }
    
    print("Generating report for Stealth Protocol (EMERGING MOCK)...")
    generator = PDFReportGenerator()
    dossier = generator.map_project_to_dossier(project_info)
    pdf_buffer = generator.generate_project_report(dossier)
    
    filename = "stealth_test_report.pdf"
    with open(filename, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    print(f"Success! Emerging report saved to {filename}")

if __name__ == "__main__":
    test_generate_report("Drosera")
    test_generate_report("Uniswap")
    test_emerging_report()
