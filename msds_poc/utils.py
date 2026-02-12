"""Utility functions for MSDS PoC."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pdfplumber
import pandas as pd

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def save_result(output_path: Path, data: Dict[str, Any]) -> None:
    """Save result to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract all text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Processing PDF: {pdf_path.name} ({len(pdf.pages)} pages)")
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num} ---\n{page_text}"
        logger.info(f"Extracted {len(text)} characters from {pdf_path.name}")
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        
    return text


def parse_msds_data(text: str) -> Dict[str, str]:
    """
    Parse MSDS information from extracted text.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        Dictionary with parsed MSDS data
    """
    # Common MSDS section headers and their parsers
    msds_sections = {
        "Product Name": [],
        "Supplier": [],
        "Chemical Name": [],
        "CAS Number": [],
        "Hazards": [],
        "Physical Properties": [],
        "Chemical Properties": [],
        "Safety Information": [],
        "Storage": [],
        "Disposal": [],
        "PPE": [],  # Personal Protective Equipment
        "First Aid": [],
    }
    
    # Simple parsing logic - extract lines containing common keywords
    lines = text.split('\n')
    current_section = None
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check for section headers
        if 'product name' in line_lower or 'product identifier' in line_lower:
            current_section = 'Product Name'
        elif 'supplier' in line_lower or 'manufacturer' in line_lower:
            current_section = 'Supplier'
        elif 'chemical name' in line_lower:
            current_section = 'Chemical Name'
        elif 'cas number' in line_lower or 'cas no' in line_lower:
            current_section = 'CAS Number'
        elif 'hazard' in line_lower or 'danger' in line_lower:
            current_section = 'Hazards'
        elif 'physical property' in line_lower or 'appearance' in line_lower:
            current_section = 'Physical Properties'
        elif 'chemical property' in line_lower:
            current_section = 'Chemical Properties'
        elif 'safety' in line_lower:
            current_section = 'Safety Information'
        elif 'storage' in line_lower:
            current_section = 'Storage'
        elif 'disposal' in line_lower:
            current_section = 'Disposal'
        elif 'ppe' in line_lower or 'protective equipment' in line_lower or 'precaution' in line_lower:
            current_section = 'PPE'
        elif 'first aid' in line_lower:
            current_section = 'First Aid'
        elif current_section and line.strip() and len(line.strip()) > 2:
            # Add non-empty lines to current section
            msds_sections[current_section].append(line.strip())
    
    # Convert lists to comma-separated strings
    parsed_data = {}
    for key, values in msds_sections.items():
        parsed_data[key] = " | ".join(values[:5]) if values else "N/A"  # Limit to first 5 lines
    
    return parsed_data


def create_excel_from_msds(msds_data: Dict[str, str], output_path: Path) -> None:
    """
    Create Excel workbook from parsed MSDS data.
    
    Args:
        msds_data: Dictionary with parsed MSDS data
        output_path: Path to save Excel file
    """
    try:
        # Create DataFrame
        df = pd.DataFrame(list(msds_data.items()), columns=['Field', 'Value'])
        
        # Create workbook with formatting
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='MSDS Data', index=False)
            
            # Format worksheet
            worksheet = writer.sheets['MSDS Data']
            worksheet.column_dimensions['A'].width = 25
            worksheet.column_dimensions['B'].width = 100
            
        logger.info(f"Excel file created: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating Excel file: {e}")


def process_pdf_files(input_dir: Path, output_dir: Path) -> List[Dict[str, Any]]:
    """
    Process all PDF files in input directory and create Excel outputs.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory to save Excel files
        
    Returns:
        List of processed file information
    """
    results = []
    
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return results
    
    logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
    
    for pdf_file in pdf_files:
        logger.info(f"Processing: {pdf_file.name}")
        
        # Extract text
        extracted_text = extract_text_from_pdf(pdf_file)
        
        if not extracted_text:
            logger.warning(f"No text extracted from {pdf_file.name}")
            continue
        
        # Parse MSDS data
        msds_data = parse_msds_data(extracted_text)
        
        # Save raw extracted text as backup
        text_output = output_dir / f"{pdf_file.stem}_extracted.txt"
        text_output.parent.mkdir(parents=True, exist_ok=True)
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        # Create Excel file
        excel_output = output_dir / f"{pdf_file.stem}.xlsx"
        create_excel_from_msds(msds_data, excel_output)
        
        results.append({
            "input_file": pdf_file.name,
            "output_excel": excel_output.name,
            "output_text": text_output.name,
            "status": "success"
        })
    
    return results

