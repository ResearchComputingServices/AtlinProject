import json
from uuid import UUID, uuid4
from .youtube import YoutubeJobDetails
from . import atlin_schemas as schemas

class Job:
    _required_fields = dict(
        job_uid = str,
        user_uid = str,
        token_uid = str,
        job_name = str,
        job_tag = str,
        job_status = str,
        social_platform = str,
        create_date = str,
        modify_date = str,
        complete_date = str,
        output_path = str,
        job_message = str,
        job_detail = str,
    )
    
    def __init__(self, data: dict = None) -> None:
        if data is not None:
            self.from_json(data)
    
    def _validate_string(self, varname, value):
        if not isinstance(value, str):
            raise TypeError(f"value of {varname} should be of type string")
    
    def _validate_uid(self, value):
        UUID(value)
    
    def _get_date(self):
        #TODO
        return ""

    @property
    def job_uid(self):
        return getattr(self, '_job_uid', str(uuid4()))
    
    @job_uid.setter
    def job_uid(self, value):
        self._validate_uid(value)
        setattr(self, '_job_uid', value)
    
    @property
    def user_uid(self):
        return getattr(self, '_user_uid', str(uuid4()))
    
    @user_uid.setter
    def user_uid(self, value):
        self._validate_uid(value)
        setattr(self, '_user_uid', value)
        
    @property
    def token_uid(self):
        return getattr(self, '_token_uid', str(uuid4))

    @token_uid.setter
    def token_uid(self, value):
        self._validate_uid(value)
        setattr(self, '_token_uid', value)
    
    @property
    def job_name(self):
        return getattr(self, '_job_name', '')

    @job_name.setter
    def job_name(self, value):
        if value is None: value = ''
        self._validate_string('job_name', value)
        setattr(self, '_job_name', value)

    @property
    def job_tag(self):
        return getattr(self, '_job_tag', '')

    @job_tag.setter
    def job_tag(self, value: str):
        if isinstance(value, list):
            value = ','.join(value)
        setattr(self, '_job_tag', value)
    
    @property
    def job_status(self):
        return getattr(self, '_job_status', "CREATED")

    @job_status.setter
    def job_status(self, value):
        if value not in schemas._valid_job_status:
            raise ValueError(f"'{value}' is not a valid job status. Valid status are: {', '.join(schemas._valid_job_status)}")
        setattr(self, '_job_status', value )
    
    @property
    def social_platform(self):
        return getattr(self, '_social_platform', 'YOUTUBE')

    @social_platform.setter
    def social_platform(self, value):
        if value not in schemas._valid_social_platforms:
            raise ValueError(f"'{value}' is not a valid social_platform. Valid values are: {', '.join(schemas._valid_social_platforms) }")
        setattr(self, '_social_platform', value)
    
    @property    
    def create_date(self):
        return getattr(self, '_create_date', self._get_date())

    @create_date.setter
    def create_date(self, value):
        setattr(self, '_create_date', value)
        
    @property
    def modify_date(self):
        return getattr(self, '_modify_date', self._get_date())

    @modify_date.setter
    def modify_date(self, value):
        setattr(self, '_modify_date', value)
    
    @property
    def complete_date(self):
        return getattr(self, '_complete_date', "")

    @complete_date.setter
    def complete_date(self, value):
        #TODO validate date
        setattr(self, '_complete_date', value)
    
    @property
    def output_path(self):
        return getattr(self, '_output_path', '')

    @output_path.setter
    def output_path(self, value):
        #TODO validate path
        setattr(self, '_output_path', value)
        
    @property
    def job_message(self):
        return getattr(self, '_job_message', '')

    @job_message.setter
    def job_message(self, value):
        self._validate_string('job_message', value)
        setattr(self, '_job_message', value)
    
    @property
    def job_detail(self):
        return getattr(self, '_job_detail', {})

    @job_detail.setter
    def job_detail(self, value):
        if isinstance(value,str):
            try:
                value = json.loads(value)
            except Exception as e:
                raise TypeError("job_detail should be an object or dictionary")
        elif isinstance(value,dict):
            pass
        else:
            try:
                value = value.to_dict()
            except Exception as e:
                raise TypeError("job_detail should be an object or dictionary")
        
        if self.social_platform == "YOUTUBE":
            value = YoutubeJobDetails(data = value)
        
        setattr(self, '_job_detail', value)

    def to_dict(self):
        if isinstance(self.job_detail, dict):
            job_detail = self.job_detail
        else:
            try:
                job_detail = self.job_detail.to_dict()
            except Exception as e:
                ValueError("Invalid job_detail")
        return dict(
            job_uid = getattr(self, 'job_uid'),
            user_uid = getattr(self, 'user_uid'),
            token_uid = getattr(self, 'token_uid'),
            job_name = getattr(self, 'job_name'),
            job_tag = getattr(self, 'job_tag'),
            job_status = getattr(self, 'job_status'),
            social_platform = getattr(self, 'social_platform'),
            create_date = getattr(self, 'create_date'),
            modify_date = getattr(self, 'modify_date'),
            complete_date = getattr(self, 'complete_date'),
            output_path = getattr(self, 'output_path'),
            job_message = getattr(self, 'job_message'),
            job_detail = job_detail,
        )
        
    def to_json(self):
        return json.dumps(self.to_dict())
        
    def from_json(self, data):
        if not all ( key in data.keys() for key in self._required_fields.keys()):
            raise ValueError("Missing Key!")
        
        if isinstance(data, str):
            data = json.loads(data)
            
        for key in data.keys():
            setattr(self, key, data[key])
            
