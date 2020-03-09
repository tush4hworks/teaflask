from flask_login import UserMixin

class User(UserMixin):
	user_dict = {}
	"""Inherited from UserMixin class of flask_login"""
	def __init__(self, uid, *args, **kwargs):
		self.id = uid
		super().__init__(*args, **kwargs)
		User.user_dict[self.id] = self

	def get_id(self):
	    try:
	        return (self.id)
	    except AttributeError:
	        raise NotImplementedError('No `id` attribute - override `get_id`')

	@classmethod
	def get(cls, user_id):
		return cls.user_dict.get(user_id, None)