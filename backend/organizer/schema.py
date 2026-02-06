import graphene
from . import models
from member.models import Member
from core.models import BdayaUser, Track
from graphene_django import DjangoObjectType
import graphene_django_optimizer as gql_optimizer


class TrackType(DjangoObjectType):
    class Meta:
        model = Track
        fields = '__all__'
        
class SettingsType(DjangoObjectType):
    class Meta:
        model = models.SiteSetting
        fields = '__all__'

class MemberType(DjangoObjectType):
    class Meta:
        model = Member
        fields = '__all__'

class Query(graphene.ObjectType):
    all_settings = graphene.Field(SettingsType)
    track = graphene.Field(TrackType, track=graphene.String())
    can_register = graphene.Boolean()
    member = graphene.Field(MemberType, code=graphene.String(), email=graphene.String())
    
    def resolve_all_settings(self, info):
        return gql_optimizer.query(models.SiteSetting.objects.filter(pk=1), info).first()
    
    def resolve_track(self, info, track = None):
        if info.context.user.is_anonymous:
            raise Exception("not authed")
        return gql_optimizer.query(models.Track.objects.filter(track=track), info).first()
    
    def resolve_can_register(self, info):
        return models.SiteSetting.objects.values_list("is_register_enabled", flat=True).first()
    
    def resolve_member(self, info, code = None, email = None):
        USER: BdayaUser = info.context.user
        if USER.is_anonymous:
            raise Exception("not authed")
        elif USER.is_member:
            return gql_optimizer.query(Member.objects.filter(email=USER.email), info).first()
        
        qs = Member.objects.all()
        if code:
            qs = qs.filter(code=code)
        
        if email:
            qs = qs.filter(email=email)
            
        return gql_optimizer.query(qs, info).first()
    
schema = graphene.Schema(Query)
