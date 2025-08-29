#!/usr/bin/env python3
"""
Quick test script to verify the school branch creation fix.
"""
import os
import sys
import django

# Add the project directory to sys.path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from api.serializers.schools.branch_serializers import SchoolBranchSerializer
from schools.models.school import School, SchoolBranch
import uuid

def test_school_branch_creation():
    """Test creating a school branch with UUID string."""
    
    # First, create a test school or use an existing one
    try:
        school = School.objects.first()
        if not school:
            print("No schools found in database. Creating a test school...")
            school = School.objects.create(
                name="Test School",
                description="Test school for branch creation"
            )
            print(f"Created test school: {school.name} with UUID: {school.uuid}")
        else:
            print(f"Using existing school: {school.name} with UUID: {school.uuid}")
        
        # Test data for branch creation
        test_data = {
            'name': 'Test Branch',
            'address': '123 Test Street',
            'school': str(school.uuid),  # This is what frontend sends - UUID as string
            'description': 'Test branch created via API'
        }
        
        print(f"Testing branch creation with data: {test_data}")
        
        # Test the serializer
        serializer = SchoolBranchSerializer(data=test_data)
        
        if serializer.is_valid():
            # This should work now with our fix
            branch = serializer.save()
            print(f"✅ SUCCESS: Branch created successfully!")
            print(f"   Branch name: {branch.name}")
            print(f"   Branch UUID: {branch.uuid}")
            print(f"   School: {branch.school}")
            print(f"   School UUID: {branch.school.uuid}")
            
            # Clean up the test branch
            branch.delete()
            print("   Test branch cleaned up.")
            
            return True
        else:
            print(f"❌ FAILED: Serializer validation failed")
            print(f"   Errors: {serializer.errors}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing School Branch Creation Fix...")
    print("=" * 50)
    
    success = test_school_branch_creation()
    
    print("=" * 50)
    if success:
        print("✅ All tests passed! The fix should work.")
    else:
        print("❌ Tests failed. Need to investigate further.")
