"""Data source connectors for Grayline.

Each connector implements:
- fetch(): pull fresh data from the source
- normalize(): convert to standard schema
- load_sample(): return realistic sample data for offline use
"""
