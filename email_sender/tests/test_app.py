import os
import sys
import unittest
from flask import Flask
from src.main import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_templates_page(self):
        """Test that the templates page loads correctly"""
        response = self.app.get('/templates')
        self.assertEqual(response.status_code, 200)
        
    def test_send_page(self):
        """Test that the send page loads correctly"""
        response = self.app.get('/send')
        self.assertEqual(response.status_code, 200)
        
    def test_tracking_page(self):
        """Test that the tracking page loads correctly"""
        response = self.app.get('/tracking')
        self.assertEqual(response.status_code, 200)
        
    def test_csv_api_endpoint(self):
        """Test that the CSV API endpoint exists"""
        response = self.app.post('/api/csv/upload')
        # Should return 400 because no file was provided, but endpoint exists
        self.assertEqual(response.status_code, 400)
        
    def test_template_api_endpoint(self):
        """Test that the template API endpoint exists"""
        response = self.app.post('/api/template/save')
        # Should return 400 because no data was provided, but endpoint exists
        self.assertEqual(response.status_code, 400)
        
    def test_email_api_endpoint(self):
        """Test that the email API endpoint exists"""
        response = self.app.post('/api/email/send')
        # Should return 400 because no data was provided, but endpoint exists
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
