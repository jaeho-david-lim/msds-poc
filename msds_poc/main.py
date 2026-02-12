"""Main module for MSDS PoC."""

import json
import logging
from pathlib import Path

from .utils import process_pdf_files, save_result

logger = logging.getLogger(__name__)


def run_poc():
    """Run the MSDS PoC workflow."""
    logger.info("Starting MSDS PoC execution...")
    
    # Define input/output paths
    input_dir = Path(__file__).parent.parent / "input"
    output_dir = Path(__file__).parent.parent / "output"
    
    # Ensure directories exist
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    # Process PDF files
    logger.info("Processing PDF files...")
    results = process_pdf_files(input_dir, output_dir)
    
    # Save processing results
    result_summary = {
        "status": "success",
        "processed_files": len(results),
        "output_dir": str(output_dir),
        "results": results
    }
    
    # Save summary as JSON
    summary_path = output_dir / "processing_summary.json"
    save_result(summary_path, result_summary)
    
    logger.info(f"PoC execution completed! Processed {len(results)} file(s)")
    logger.info(f"Results saved to: {output_dir}")
    
    return result_summary


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    run_poc()

