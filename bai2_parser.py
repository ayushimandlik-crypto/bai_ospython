"""
BAI2 (Bank Administration Institute) File Parser

This module provides functionality to parse BAI2 format files used for
electronic cash management balance reporting.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd


@dataclass
class BAI2Record:
    """Base class for BAI2 records"""
    record_type: str
    raw_data: str


@dataclass
class FileHeader(BAI2Record):
    """Record Type 01: File Header"""
    sender_id: str
    receiver_id: str
    file_id: str
    file_creation_date: str
    file_creation_time: str
    file_id_number: str
    physical_record_length: str
    block_size: str
    version_number: str


@dataclass
class GroupHeader(BAI2Record):
    """Record Type 02: Group Header"""
    group_id: str
    originator_id: str
    group_status: str
    as_of_date: str
    as_of_time: str
    currency_code: str
    as_of_date_modifier: str


@dataclass
class AccountIdentifier(BAI2Record):
    """Record Type 03: Account Identifier"""
    account_number: str
    currency_code: str


@dataclass
class TransactionDetail(BAI2Record):
    """Record Type 16: Transaction Detail"""
    type_code: str
    amount: str
    funds_type: str
    bank_reference: str
    customer_reference: str
    text: str


@dataclass
class AccountTrailer(BAI2Record):
    """Record Type 49: Account Trailer"""
    account_control_total: str
    number_of_records: str


@dataclass
class GroupTrailer(BAI2Record):
    """Record Type 98: Group Trailer"""
    group_control_total: str
    number_of_accounts: str
    number_of_records: str


@dataclass
class FileTrailer(BAI2Record):
    """Record Type 99: File Trailer"""
    file_control_total: str
    number_of_groups: str
    number_of_records: str


@dataclass
class ContinuationRecord(BAI2Record):
    """Record Type 88: Continuation Record"""
    continuation_indicator: str
    continuation_data: str


class BAI2Parser:
    """Parser for BAI2 format files"""
    
    def __init__(self):
        self.records = []
        self.file_header = None
        self.group_headers = []
        self.account_identifiers = []
        self.transaction_details = []
        self.account_trailers = []
        self.group_trailers = []
        self.file_trailer = None
        self.continuation_records = []
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a BAI2 file and return structured data
        
        Args:
            file_path: Path to the BAI2 file
            
        Returns:
            Dictionary containing parsed data organized by record type
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    record = self._parse_line(line, line_num)
                    if record:
                        self.records.append(record)
                        self._categorize_record(record)
                except Exception as e:
                    print(f"Error parsing line {line_num}: {e}")
                    print(f"Line content: {line}")
                    
            return self._get_parsed_data()
            
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return {}
    
    def _parse_line(self, line: str, line_num: int) -> Optional[BAI2Record]:
        """Parse a single line into appropriate BAI2 record type"""
        if not line or len(line) < 2:
            return None
            
        record_type = line[:2]
        fields = line.split(',')
        
        try:
            if record_type == '01':
                return self._parse_file_header(fields, line)
            elif record_type == '02':
                return self._parse_group_header(fields, line)
            elif record_type == '03':
                return self._parse_account_identifier(fields, line)
            elif record_type == '16':
                return self._parse_transaction_detail(fields, line)
            elif record_type == '49':
                return self._parse_account_trailer(fields, line)
            elif record_type == '88':
                return self._parse_continuation_record(fields, line)
            elif record_type == '98':
                return self._parse_group_trailer(fields, line)
            elif record_type == '99':
                return self._parse_file_trailer(fields, line)
            else:
                # Unknown record type, create generic record
                return BAI2Record(record_type=record_type, raw_data=line)
                
        except Exception as e:
            print(f"Error parsing record type {record_type} at line {line_num}: {e}")
            return BAI2Record(record_type=record_type, raw_data=line)
    
    def _parse_file_header(self, fields: List[str], line: str) -> FileHeader:
        """Parse File Header (Record Type 01)"""
        return FileHeader(
            record_type='01',
            raw_data=line,
            sender_id=fields[1] if len(fields) > 1 else '',
            receiver_id=fields[2] if len(fields) > 2 else '',
            file_id=fields[3] if len(fields) > 3 else '',
            file_creation_date=fields[4] if len(fields) > 4 else '',
            file_creation_time=fields[5] if len(fields) > 5 else '',
            file_id_number=fields[6] if len(fields) > 6 else '',
            physical_record_length=fields[7] if len(fields) > 7 else '',
            block_size=fields[8] if len(fields) > 8 else '',
            version_number=fields[9] if len(fields) > 9 else ''
        )
    
    def _parse_group_header(self, fields: List[str], line: str) -> GroupHeader:
        """Parse Group Header (Record Type 02)"""
        return GroupHeader(
            record_type='02',
            raw_data=line,
            group_id=fields[1] if len(fields) > 1 else '',
            originator_id=fields[2] if len(fields) > 2 else '',
            group_status=fields[3] if len(fields) > 3 else '',
            as_of_date=fields[4] if len(fields) > 4 else '',
            as_of_time=fields[5] if len(fields) > 5 else '',
            currency_code=fields[6] if len(fields) > 6 else '',
            as_of_date_modifier=fields[7] if len(fields) > 7 else ''
        )
    
    def _parse_account_identifier(self, fields: List[str], line: str) -> AccountIdentifier:
        """Parse Account Identifier (Record Type 03)"""
        return AccountIdentifier(
            record_type='03',
            raw_data=line,
            account_number=fields[1] if len(fields) > 1 else '',
            currency_code=fields[2] if len(fields) > 2 else ''
        )
    
    def _parse_transaction_detail(self, fields: List[str], line: str) -> TransactionDetail:
        """Parse Transaction Detail (Record Type 16)"""
        return TransactionDetail(
            record_type='16',
            raw_data=line,
            type_code=fields[1] if len(fields) > 1 else '',
            amount=fields[2] if len(fields) > 2 else '',
            funds_type=fields[3] if len(fields) > 3 else '',
            bank_reference=fields[4] if len(fields) > 4 else '',
            customer_reference=fields[5] if len(fields) > 5 else '',
            text=fields[6] if len(fields) > 6 else ''
        )
    
    def _parse_account_trailer(self, fields: List[str], line: str) -> AccountTrailer:
        """Parse Account Trailer (Record Type 49)"""
        return AccountTrailer(
            record_type='49',
            raw_data=line,
            account_control_total=fields[1] if len(fields) > 1 else '',
            number_of_records=fields[2] if len(fields) > 2 else ''
        )
    
    def _parse_group_trailer(self, fields: List[str], line: str) -> GroupTrailer:
        """Parse Group Trailer (Record Type 98)"""
        return GroupTrailer(
            record_type='98',
            raw_data=line,
            group_control_total=fields[1] if len(fields) > 1 else '',
            number_of_accounts=fields[2] if len(fields) > 2 else '',
            number_of_records=fields[3] if len(fields) > 3 else ''
        )
    
    def _parse_file_trailer(self, fields: List[str], line: str) -> FileTrailer:
        """Parse File Trailer (Record Type 99)"""
        return FileTrailer(
            record_type='99',
            raw_data=line,
            file_control_total=fields[1] if len(fields) > 1 else '',
            number_of_groups=fields[2] if len(fields) > 2 else '',
            number_of_records=fields[3] if len(fields) > 3 else ''
        )
    
    def _parse_continuation_record(self, fields: List[str], line: str) -> ContinuationRecord:
        """Parse Continuation Record (Record Type 88)"""
        return ContinuationRecord(
            record_type='88',
            raw_data=line,
            continuation_indicator=fields[1] if len(fields) > 1 else '',
            continuation_data=','.join(fields[2:]) if len(fields) > 2 else ''
        )
    
    def _categorize_record(self, record: BAI2Record):
        """Categorize parsed record into appropriate list"""
        if isinstance(record, FileHeader):
            self.file_header = record
        elif isinstance(record, GroupHeader):
            self.group_headers.append(record)
        elif isinstance(record, AccountIdentifier):
            self.account_identifiers.append(record)
        elif isinstance(record, TransactionDetail):
            self.transaction_details.append(record)
        elif isinstance(record, AccountTrailer):
            self.account_trailers.append(record)
        elif isinstance(record, GroupTrailer):
            self.group_trailers.append(record)
        elif isinstance(record, FileTrailer):
            self.file_trailer = record
        elif isinstance(record, ContinuationRecord):
            self.continuation_records.append(record)
    
    def _get_parsed_data(self) -> Dict[str, Any]:
        """Return organized parsed data"""
        return {
            'file_header': self.file_header,
            'group_headers': self.group_headers,
            'account_identifiers': self.account_identifiers,
            'transaction_details': self.transaction_details,
            'account_trailers': self.account_trailers,
            'group_trailers': self.group_trailers,
            'file_trailer': self.file_trailer,
            'continuation_records': self.continuation_records,
            'total_records': len(self.records)
        }
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics of parsed records"""
        return {
            'file_headers': 1 if self.file_header else 0,
            'group_headers': len(self.group_headers),
            'account_identifiers': len(self.account_identifiers),
            'transaction_details': len(self.transaction_details),
            'account_trailers': len(self.account_trailers),
            'group_trailers': len(self.group_trailers),
            'file_trailers': 1 if self.file_trailer else 0,
            'continuation_records': len(self.continuation_records),
            'total_records': len(self.records)
        }
    
    def to_dataframe(self, record_type: str = None) -> pd.DataFrame:
        """
        Convert parsed records to pandas DataFrame
        
        Args:
            record_type: Specific record type to convert ('01', '02', '03', etc.)
                        If None, returns all records
            
        Returns:
            pandas DataFrame with parsed data
        """
        if record_type:
            records = [r for r in self.records if r.record_type == record_type]
        else:
            records = self.records
            
        if not records:
            return pd.DataFrame()
            
        data = []
        for record in records:
            row = {'record_type': record.record_type}
            if hasattr(record, '__dict__'):
                for key, value in record.__dict__.items():
                    if key not in ['record_type', 'raw_data']:
                        row[key] = value
            data.append(row)
            
        return pd.DataFrame(data)


def main():
    """Example usage of BAI2Parser"""
    parser = BAI2Parser()
    
    # Parse the file
    file_path = '/home/ayushi/segmentation/llm_sample.da'
    print(f"Parsing BAI2 file: {file_path}")
    
    parsed_data = parser.parse_file(file_path)
    
    if parsed_data:
        print("\n=== PARSING SUMMARY ===")
        summary = parser.get_summary()
        for record_type, count in summary.items():
            print(f"{record_type}: {count}")
        
        print("\n=== FILE HEADER ===")
        if parsed_data['file_header']:
            header = parsed_data['file_header']
            print(f"Sender ID: {header.sender_id}")
            print(f"Receiver ID: {header.receiver_id}")
            print(f"File ID: {header.file_id}")
            print(f"Creation Date: {header.file_creation_date}")
            print(f"Creation Time: {header.file_creation_time}")
        
        print("\n=== ACCOUNT IDENTIFIERS ===")
        for i, account in enumerate(parsed_data['account_identifiers'][:5]):  # Show first 5
            print(f"Account {i+1}: {account.account_number} ({account.currency_code})")
        
        print(f"\nTotal accounts found: {len(parsed_data['account_identifiers'])}")
        
        # Create DataFrame for analysis
        df = parser.to_dataframe()
        print(f"\nDataFrame shape: {df.shape}")
        print("\nFirst few records:")
        print(df.head())
        
    else:
        print("Failed to parse the file")


if __name__ == "__main__":
    main()
