from rest_framework import serializers
from .models import *
from bs4 import BeautifulSoup as BS


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('name',)


class DepartmentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('name',)

class ProfileInfoSerializer(serializers.ModelSerializer):
    department = DepartmentNameSerializer()
    class Meta:
        model = Profile
        fields = '__all__'


class UserInfoSerializer(serializers.ModelSerializer):
    profile = ProfileInfoSerializer()
    class Meta:
        model = User
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ServiceNoteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = ServiceNote
        fields = ('title', 'date', 'user', 'id', 'fast', 'status', 'number')


class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk','first_name','last_name')

class UserNoteSerializer(serializers.ModelSerializer):
    user = UserIdSerializer()
    class Meta:
        model = NoteUsers
        fields = ('index', 'status', 'user', 'comment', 'date_create')

class UserMyNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteUsers
        fields = ('index', 'user', 'status', )

class ServiceMyNoteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    users = UserMyNoteSerializer(many=True)
    class Meta:
        model = ServiceNote
        fields = ('title', 'date', 'user', 'id', 'fast', 'status','number','users', 'user_index')

class NoteFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteFiles
        fields = ('file',)

class ServiceMyNoteDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    users = UserNoteSerializer(many=True)
    files = NoteFilesSerializer(many=True)
    buh = UserSerializer()
    tags = TagSerializer(many=True)
    class Meta:
        model = ServiceNote
        fields = '__all__'

class UserNoteDetailSerializer(serializers.ModelSerializer):
    note = ServiceMyNoteDetailSerializer()
    class Meta:
        model = NoteUsers
        fields = '__all__'

#class MovieDetailSerializer(serializers.ModelSerializer):
#    genres = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)
#    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
#    countries = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)
#    reviews = ReviewSerializer(many=True)
#    class Meta:
#        model = Movie
#        exclude = ('draft', )
