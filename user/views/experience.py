from user.models import Experience
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

class ExperienceObject:
    def __init__(self, user=None, experience_request=None):
        self.experience_model = Experience
        self.experience_input = experience_request
        self.user = user

    def create(self):
        """
        This method is used to create a new experience for a user.
        """
        logger.debug("Creating new experience for user: %s", self.user)
        if not self.experience_input:
            logger.error("No experience data provided.")
            return None
        
        # Add the user to the input data, as it's a foreign key
        self.experience_input['user'] = self.user

        # Create a new experience record and return it
        experience = self.experience_model.objects.create(**self.experience_input)
        return experience
    
    def get_all(self):
        """
        This method is used to get all experiences of a user.
        """
        return self.experience_model.objects.filter(user=self.user)
    
    def get_by_id(self, experience_id):
        """
        This method is used to get an experience by its id.
        """
        try:
            return self.experience_model.objects.get(id=experience_id)
        except self.experience_model.DoesNotExist:
            return None
    
    def get_by_user(self, user=None, user_id=None):
        """
        This method is used to get all experiences of the current user.
        Either the user object or user_id should be provided.
        """
        user_to_filter = user or user_id or self.user
        return self.experience_model.objects.filter(user=user_to_filter)
    
    def update(self, experience_id):
        """
        This method is used to update an existing experience for a user.
        """
        try:
            experience = self.experience_model.objects.get(id=experience_id)
            for key, value in self.experience_input.items():
                if hasattr(experience, key):
                    setattr(experience, key, value)
            experience.save()
            return experience
        except self.experience_model.DoesNotExist:
            return None
    
    def delete(self, experience_id):
        """
        This method is used to delete an experience for a user.
        """
        try:
            experience = self.experience_model.objects.get(id=experience_id)
            experience.delete()
            return True
        except self.experience_model.DoesNotExist:
            return False
