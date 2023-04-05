import unittest
import os

# these 3 should be verified
mock_public_key = "9c7d775851a98ceb09a80928c1f8ff56706a0f5d91d841c72850fcd92e065b8f"
mock_signature = "99c4903df0b00ac32ba158db956ee39586adf05fea6be714055ac79a80bfd9dff59399b7da01ced95d0a252daee6bdb07e5f59cc546322bb779fd749b04f170c"
mock_timestamp = "202204091535"
mock_body = "testmessage"

mock_signature_incorrect = "39c4903df0b00ac32ba158db956ee39586adf05fea6be714055ac79a80bfd9dff59399b7da01ced95d0a252daee6bdb07e5f59cc546322bb779fd749b04f170d"

os.environ['APPLICATION_PUBLIC_KEY'] = mock_public_key
os.environ['COMMANDS'] = '{}'
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"
os.environ['AWS_REGION'] = "eu-central-1"

from ..lambda_function import is_request_verified, signature_header_name, timestamp_header_name


class TestVerify(unittest.TestCase):

    def test_verify_headers_not_present(self):
        verified = is_request_verified({}, mock_body)
        self.assertFalse(verified)

    def test_verify_headers_incorrect(self):
        os.environ['APPLICATION_PUBLIC_KEY'] = mock_public_key
        verified = is_request_verified({
            signature_header_name: mock_signature_incorrect,
            timestamp_header_name: mock_timestamp
        }, mock_body)
        self.assertFalse(verified)

    def test_verify_valid_request(self):
        os.environ['APPLICATION_PUBLIC_KEY'] = mock_public_key
        verified = is_request_verified({
            signature_header_name: mock_signature,
            timestamp_header_name: mock_timestamp
        }, mock_body)
        self.assertTrue(verified)


if __name__ == '__main__':
    unittest.main()
