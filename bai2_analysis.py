"""
Detailed BAI2 File Analysis Script

This script provides comprehensive analysis of the parsed BAI2 file data.
"""

import pandas as pd
from bai2_parser import BAI2Parser
import matplotlib.pyplot as plt
import seaborn as sns


def analyze_bai2_file(file_path: str):
    """Perform detailed analysis of BAI2 file"""
    
    print("=" * 60)
    print("BAI2 FILE ANALYSIS REPORT")
    print("=" * 60)
    
    # Parse the file
    parser = BAI2Parser()
    parsed_data = parser.parse_file(file_path)
    
    if not parsed_data:
        print("Failed to parse the file!")
        return
    
    # Basic statistics
    print("\n1. BASIC FILE STATISTICS")
    print("-" * 30)
    summary = parser.get_summary()
    for record_type, count in summary.items():
        print(f"{record_type.replace('_', ' ').title()}: {count:,}")
    
    # File header details
    print("\n2. FILE HEADER INFORMATION")
    print("-" * 30)
    if parsed_data['file_header']:
        header = parsed_data['file_header']
        print(f"Sender ID: {header.sender_id}")
        print(f"Receiver ID: {header.receiver_id}")
        print(f"File ID: {header.file_id}")
        print(f"Creation Date: {header.file_creation_date}")
        print(f"Creation Time: {header.file_creation_time}")
        print(f"File ID Number: {header.file_id_number}")
        print(f"Physical Record Length: {header.physical_record_length}")
        print(f"Block Size: {header.block_size}")
        print(f"Version Number: {header.version_number}")
    
    # Group information
    print("\n3. GROUP INFORMATION")
    print("-" * 30)
    print(f"Number of Groups: {len(parsed_data['group_headers'])}")
    for i, group in enumerate(parsed_data['group_headers'][:3]):  # Show first 3 groups
        print(f"Group {i+1}:")
        print(f"  Group ID: {group.group_id}")
        print(f"  Originator ID: {group.originator_id}")
        print(f"  Status: {group.group_status}")
        print(f"  As of Date: {group.as_of_date}")
        print(f"  Currency: {group.currency_code}")
    
    # Account analysis
    print("\n4. ACCOUNT ANALYSIS")
    print("-" * 30)
    accounts = parsed_data['account_identifiers']
    print(f"Total Accounts: {len(accounts)}")
    
    # Currency distribution
    currencies = {}
    for account in accounts:
        currency = account.currency_code.strip('/')
        currencies[currency] = currencies.get(currency, 0) + 1
    
    print("\nCurrency Distribution:")
    for currency, count in currencies.items():
        print(f"  {currency}: {count} accounts")
    
    # Transaction analysis
    print("\n5. TRANSACTION ANALYSIS")
    print("-" * 30)
    transactions = parsed_data['transaction_details']
    print(f"Total Transactions: {len(transactions)}")
    
    if transactions:
        # Transaction type analysis
        type_codes = {}
        for trans in transactions:
            type_code = trans.type_code
            type_codes[type_code] = type_codes.get(type_code, 0) + 1
        
        print("\nTransaction Type Distribution (Top 10):")
        sorted_types = sorted(type_codes.items(), key=lambda x: x[1], reverse=True)
        for type_code, count in sorted_types[:10]:
            print(f"  Type {type_code}: {count} transactions")
        
        # Amount analysis
        amounts = []
        for trans in transactions:
            try:
                amount = float(trans.amount) if trans.amount else 0
                amounts.append(amount)
            except ValueError:
                continue
        
        if amounts:
            print(f"\nAmount Statistics:")
            print(f"  Total Amount: ${sum(amounts):,.2f}")
            print(f"  Average Amount: ${sum(amounts)/len(amounts):,.2f}")
            print(f"  Min Amount: ${min(amounts):,.2f}")
            print(f"  Max Amount: ${max(amounts):,.2f}")
    
    # Continuation records analysis
    print("\n6. CONTINUATION RECORDS ANALYSIS")
    print("-" * 30)
    continuation_records = parsed_data['continuation_records']
    print(f"Total Continuation Records: {len(continuation_records)}")
    
    if continuation_records:
        # Analyze continuation indicators
        indicators = {}
        for record in continuation_records:
            indicator = record.continuation_indicator
            indicators[indicator] = indicators.get(indicator, 0) + 1
        
        print("\nContinuation Indicator Distribution:")
        for indicator, count in indicators.items():
            print(f"  Indicator {indicator}: {count} records")
    
    # Data quality check
    print("\n7. DATA QUALITY CHECK")
    print("-" * 30)
    
    # Check for missing data
    df = parser.to_dataframe()
    
    print("Missing Data Analysis:")
    missing_data = df.isnull().sum()
    for column, missing_count in missing_data.items():
        if missing_count > 0:
            percentage = (missing_count / len(df)) * 100
            print(f"  {column}: {missing_count:,} ({percentage:.1f}%)")
    
    # File trailer validation
    print("\n8. FILE VALIDATION")
    print("-" * 30)
    if parsed_data['file_trailer']:
        trailer = parsed_data['file_trailer']
        print(f"File Control Total: {trailer.file_control_total}")
        print(f"Number of Groups: {trailer.number_of_groups}")
        print(f"Number of Records: {trailer.number_of_records}")
        
        # Validate counts
        actual_groups = len(parsed_data['group_headers'])
        actual_records = parser.get_summary()['total_records']
        
        print(f"\nValidation:")
        print(f"  Expected Groups: {trailer.number_of_groups}, Actual: {actual_groups}")
        print(f"  Expected Records: {trailer.number_of_records}, Actual: {actual_records}")
        
        if str(actual_groups) == trailer.number_of_groups:
            print("  ✓ Group count matches")
        else:
            print("  ✗ Group count mismatch")
            
        if str(actual_records) == trailer.number_of_records:
            print("  ✓ Record count matches")
        else:
            print("  ✗ Record count mismatch")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


def export_to_excel(file_path: str, output_path: str = None):
    """Export parsed BAI2 data to Excel file"""
    
    if output_path is None:
        output_path = file_path.replace('.da', '_parsed.xlsx')
    
    parser = BAI2Parser()
    parsed_data = parser.parse_file(file_path)
    
    if not parsed_data:
        print("Failed to parse the file!")
        return
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Export each record type to separate sheets
        record_types = ['01', '02', '03', '16', '49', '88', '98', '99']
        
        for record_type in record_types:
            df = parser.to_dataframe(record_type)
            if not df.empty:
                sheet_name = f'Record_{record_type}'
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Export summary
        summary_df = pd.DataFrame([parser.get_summary()])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"Data exported to: {output_path}")


def main():
    """Main function to run the analysis"""
    file_path = '/home/ayushi/segmentation/llm_sample.da'
    
    # Run detailed analysis
    analyze_bai2_file(file_path)
    
    # Export to Excel
    print("\nExporting data to Excel...")
    export_to_excel(file_path)
    
    print("\nAnalysis complete! Check the generated Excel file for detailed data.")


if __name__ == "__main__":
    main()
