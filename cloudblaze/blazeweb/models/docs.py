import cloudblaze.blazeweb.models as models

class Doc(models.ServerModel):
    typename = 'doc'
    idfield = 'docid'
    
    def __init__(self, docid, title, rw_users, r_users):
        self.docid = docid
        self.title = title
        self.rw_users = rw_users
        self.r_users = r_users
    
    def to_json(self):
        return {'docid' : self.docid,
                'title' : self.title,
                'rw_users' : self.rw_users,
                'r_users' : self.r_users}
    
    @staticmethod
    def from_json(obj):
        return Doc(obj['docid'], obj['title'],
                   obj['r_users'], obj['rw_users'])
    

