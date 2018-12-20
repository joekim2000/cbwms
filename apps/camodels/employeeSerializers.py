from rest_framework import serializers
from django.utils.translation import gettext as _
from .modelsframe.personnel import Company, Department, Team, Employee, ExternalApprover, Resources
from .modelsframe.policy import InFilesPolicy, InExternalServicePolicy, InApprovePolicy, InClipboardPolicy, InWebProxyPolicy, InSendMailPolicy, InReceivedMailPolicy, InReceptionPolicy, InTransmissionPolicy, InPolicy, OutFilesPolicy, OutExternalServicePolicy, OutApprovePolicy, OutClipboardPolicy, OutSendMailPolicy, OutReceivedMailPolicy, OutReceptionPolicy, OutTransmissionPolicy, OutPolicy, DataPolicy, URLPolicy, URLWhitePolicy, URLBlackPolicy, URLExceptionPolicy, DataPolicyforEmployee, URLPolicyforEmployee

class InFilesPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InFilesPolicy
        fields = '__all__'

class InExternalServicePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InExternalServicePolicy
        fields = '__all__'

class InApprovePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InApprovePolicy
        fields = '__all__'

class InClipboardPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InClipboardPolicy
        fields = '__all__'

class InWebProxyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InWebProxyPolicy
        fields = '__all__'

class InSendMailPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InSendMailPolicy
        fields = '__all__'

class InReceptionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InReceptionPolicy
        fields = '__all__'

class InReceivedMailPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InReceivedMailPolicy
        fields = '__all__'

class InReceptionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InReceptionPolicy
        fields = '__all__'

class InTransmissionPolicySerializer(serializers.ModelSerializer):
    '''
    infilespolicy = InFilesPolicySerializer(many=False, required=False)
    inexternalservicepolicy = InExternalServicePolicySerializer(many=False, required=False)
    inapprovepolicy = InApprovePolicySerializer(many=False, required=False)
    inclipboardpolicy = InClipboardPolicySerializer(many=False, required=False)
    inwebproxypolicy = InWebProxyPolicySerializer(many=False, required=False)
    insendmailpolicy = InSendMailPolicySerializer(many=False, required=False)
    inreceivemailpolicy = InReceivedMailPolicySerializer(many=False, required=False)
    '''

    class Meta:
        model = InTransmissionPolicy
        #fields = ['intransid','usetransmission','useexternalservice','useapprove','useclipboard','usecertifiate','usewebproxy','usemail']
        fields = '__all__'

class InPolicySerializer(serializers.ModelSerializer):
    '''
    intransmissionpolicy = InTransmissionPolicySerializer(many=False, required=False)
    inreceptionpolicy = InReceptionPolicySerializer(many=False, required=False)
    '''
    class Meta:
        model = InPolicy
        #fields = ['intransmissionpolicy','inreceptionpolicy']
        fields = '__all__'

class OutFilesPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OutFilesPolicy
        fields = '__all__'

class OutExternalServicePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OutExternalServicePolicy
        fields = '__all__'

class OutApprovePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OutApprovePolicy
        fields = '__all__'

class OutClipboardPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OutClipboardPolicy
        fields = '__all__'

class OutSendMailPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OutSendMailPolicy
        fields = '__all__'

class OutReceivedMailPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OutReceivedMailPolicy
        fields = '__all__'

class OutReceptionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = OutReceptionPolicy
        fields = '__all__'

class OutTransmissionPolicySerializer(serializers.ModelSerializer):
    '''
    outfilespolicy = OutFilesPolicySerializer(many=False, required=False)
    outexternalservicepolicy = OutExternalServicePolicySerializer(many=False, required=False)
    outapprovepolicy = OutApprovePolicySerializer(many=False, required=False)
    outclipboardpolicy = OutClipboardPolicySerializer(many=False, required=False)
    outsendmailpolicy = OutSendMailPolicySerializer(many=False, required=False)
    outreceivemailpolicy = OutReceivedMailPolicySerializer(many=False, required=False)
    '''
    class Meta:
        model = OutTransmissionPolicy
        #fields = ['outtransid','usetransmission','useexternalservice','useapprove','useclipboard','usecertifiate','usemail']
        fields = '__all__'

class OutPolicySerializer(serializers.ModelSerializer):
    '''
    outtransmissionpolicy = OutTransmissionPolicySerializer(many=False, required=False)
    outreceptionpolicy = OutReceptionPolicySerializer(many=False, required=False)
    '''
    class Meta:
        model = OutPolicy
        #fields = ['outtransmissionpolicy','outreceptionpolicy']
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class ExternalApproverSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalApprover
        fields = '__all__'

class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = '__all__'
