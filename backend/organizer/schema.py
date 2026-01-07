import graphene
from . import models
from core.models import Track
from member.models import Member
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
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

class UpdateSettings(graphene.Mutation):
    class Arguments:
        site_image = Upload() 
        is_register_enabled = graphene.Boolean()
        organizer_can_edit = graphene.List(graphene.String)
        
    success = graphene.Boolean()
    
    def mutate(self, info, site_image=None, is_register_enabled=None, organizer_can_edit=None):
        if info.context.user.is_anonymous:
            raise Exception("not authed")

        settings = models.SiteSetting.get_solo()
        if site_image:
            settings.site_image = site_image
        
        if is_register_enabled != None:
            settings.is_register_enabled = is_register_enabled
            
        if organizer_can_edit:
            settings.organizer_can_edit = organizer_can_edit
            
        settings.save()
        return UpdateSettings(success=True) # type: ignore
            
            
            

class Mutation(graphene.ObjectType):
    update_settings = UpdateSettings.Field()

class Query(graphene.ObjectType):
    all_settings = graphene.Field(SettingsType)
    can_register = graphene.Boolean()
    member = graphene.Field(MemberType, code=graphene.String(), email=graphene.String())
    
    def resolve_all_settings(self, info):
        if info.context.user.is_anonymous:
            raise Exception("not authed")
        return gql_optimizer.query(models.SiteSetting.objects.filter(pk=1), info).first()
    
    def resolve_can_register(self, info):
        return models.SiteSetting.objects.values_list("is_register_enabled", flat=True).first()
    
    def resolve_member(self, info, code = None, email = None):
        if info.context.user.is_anonymous:
            raise Exception("not authed")
        qs = Member.objects.all()
        if code:
            qs = qs.filter(code=code)
        
        if email:
            qs = qs.filter(email=email)
            
        return gql_optimizer.query(qs, info).first()
    
schema = graphene.Schema(Query, Mutation)