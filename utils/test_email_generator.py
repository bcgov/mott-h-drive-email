from unittest import TestCase
from email_generator import EmailGenerator
from utils.constants import TEST_RECORD
import os
import io
from typing import NamedTuple

class UploadedFileRec(NamedTuple):
    """Metadata and raw bytes for an uploaded file. Immutable."""

    file_id: str
    name: str
    type: str
    data: bytes

class UploadedFile(io.BytesIO):
    """A mutable uploaded file.

    This class extends BytesIO, which has copy-on-write semantics when
    initialized with `bytes`.
    """

    def __init__(self, record: UploadedFileRec, file_urls) -> None:
        # BytesIO's copy-on-write semantics doesn't seem to be mentioned in
        # the Python docs - possibly because it's a CPython-only optimization
        # and not guaranteed to be in other Python runtimes. But it's detailed
        # here: https://hg.python.org/cpython/rev/79a5fbe2c78f
        super().__init__(record.data)
        self.file_id = record.file_id
        self.name = record.name
        self.type = record.type
        self.size = len(record.data)
        self._file_urls = file_urls

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UploadedFile):
            return NotImplemented
        return self.file_id == other.file_id

    def __hash__(self) -> int:
        return hash(self.file_id)

    def __repr__(self) -> str:
        return util.repr_(self)


class TestEmailGenerator(TestCase):
    def test_initializes_successfully(self):
        try:
            f = UploadedFileRec(
                file_id="test_file",
                name="2025-02_SFP TRAN Usage.xlsx",
                type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                data=open('./data/2025-02_SFP TRAN Usage.xlsx', 'rb').read()
            )
            mock_file = UploadedFile(f, file_urls=None)
            gen = EmailGenerator(mock_file)
            self.assertTrue(True)
        except Exception as e:
            self.fail(e)
            
    def test_send_idir_email(self):
        f = UploadedFileRec(
                file_id="test_file",
                name="2025-02_SFP TRAN Usage.xlsx",
                type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                data=open('./data/2025-02_SFP TRAN Usage.xlsx', 'rb').read()
            )
        mock_file = UploadedFile(f, file_urls=None)
        
        
        try:
            # Initialize the EmailGenerator with our mock file
            gen = EmailGenerator(mock_file)
            
            # Send an actual email to the TEST_RECORD recipient
            gen.send_idir_email(TEST_RECORD)
            
            # If we got here without exceptions, the test passed
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to send email: {str(e)}")

    def test_send_multiple_idir_email(self):
        gen = EmailGenerator('../data/2024-11_SFP TRAN Usage.xlsx')
        gen.data = gen.data[gen.data['User ID'].isin([
            'LGODFREY',
            'MBRUNESK',
            'NAYUZIK',
            'AMACKINN',
            'MACOLE',
            'NGINOUX',
            'ATEPPER',
            'AMABELL',
            'SHCHIN',
            'CSCHETTE',
            'TRNELSON',
            'EHOUCHEN',
            'AMCKINNO',
            'DIAROBIN',
            'KBROOKER',
            'APOMPONI',
            'HDUBASOV',
            'DCATON',
            'STHIBAUL'
        ])]
        try:
            gen.send_all_emails()
        except Exception as e:
            self.fail(e)

