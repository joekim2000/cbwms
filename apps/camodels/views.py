from .modelsframe.personnel import Company, Department, Team, Employee, ExternalApprover, Resources
from .modelsframe.policy import InFilesPolicy, InExternalServicePolicy, InApprovePolicy, InClipboardPolicy, InWebProxyPolicy, InSendMailPolicy, InReceivedMailPolicy, InReceptionPolicy, InTransmissionPolicy, InPolicy, OutFilesPolicy, OutExternalServicePolicy, OutApprovePolicy, OutClipboardPolicy, OutSendMailPolicy, OutReceivedMailPolicy, OutReceptionPolicy, OutTransmissionPolicy, OutPolicy, DataPolicy, URLPolicy, URLWhitePolicy, URLBlackPolicy, URLExceptionPolicy, DataPolicyforEmployee, URLPolicyforEmployee
from .policySerializers import DataPolicySerializer, InPolicySerializer, InTransmissionPolicySerializer, InFilesPolicySerializer, InExternalServicePolicySerializer, InApprovePolicySerializer, InClipboardPolicySerializer, InWebProxyPolicySerializer, InSendMailPolicySerializer, InReceivedMailPolicySerializer, InReceptionPolicySerializer, OutPolicySerializer, OutTransmissionPolicySerializer, OutFilesPolicySerializer, OutExternalServicePolicySerializer, OutApprovePolicySerializer, OutClipboardPolicySerializer, OutSendMailPolicySerializer, OutReceivedMailPolicySerializer, OutReceptionPolicySerializer
from .employeeSerializers import CompanySerializer, DepartmentSerializer, TeamSerializer, EmployeeSerializer, ExternalApproverSerializer, ResourcesSerializer
from rest_framework import generics

# 정책
class CbcasInFilesPolicyCreate(generics.ListCreateAPIView):
    queryset = InFilesPolicy.objects.all()
    serializer_class = InFilesPolicySerializer

class CbcasInExternalServicePolicyCreate(generics.ListCreateAPIView):
    queryset = InExternalServicePolicy.objects.all()
    serializer_class = InExternalServicePolicySerializer

class CbcasInApprovePolicyCreate(generics.ListCreateAPIView):
    queryset = InApprovePolicy.objects.all()
    serializer_class = InApprovePolicySerializer

class CbcasInClipboardPolicyCreate(generics.ListCreateAPIView):
    queryset = InClipboardPolicy.objects.all()
    serializer_class = InClipboardPolicySerializer

class CbcasInWebProxyPolicyCreate(generics.ListCreateAPIView):
    queryset = InWebProxyPolicy.objects.all()
    serializer_class = InWebProxyPolicySerializer

class CbcasInSendMailPolicyCreate(generics.ListCreateAPIView):
    queryset = InSendMailPolicy.objects.all()
    serializer_class = InSendMailPolicySerializer

class CbcasInReceivedMailPolicyCreate(generics.ListCreateAPIView):
    queryset = InReceivedMailPolicy.objects.all()
    serializer_class = InReceivedMailPolicySerializer

class CbcasInReceptionPolicyCreate(generics.ListCreateAPIView):
    queryset = InReceptionPolicy.objects.all()
    serializer_class = InReceptionPolicySerializer

class CbcasInTransmissionPolicyCreate(generics.ListCreateAPIView):
    queryset = InTransmissionPolicy.objects.all()
    serializer_class = InTransmissionPolicySerializer

class CbcasInPolicyCreate(generics.ListCreateAPIView):
    queryset = InPolicy.objects.all()
    serializer_class = InPolicySerializer

class CbcasOutFilesPolicyCreate(generics.ListCreateAPIView):
    queryset = OutFilesPolicy.objects.all()
    serializer_class = OutFilesPolicySerializer

class CbcasOutExternalServicePolicyCreate(generics.ListCreateAPIView):
    queryset = OutExternalServicePolicy.objects.all()
    serializer_class = OutExternalServicePolicySerializer

class CbcasOutApprovePolicyCreate(generics.ListCreateAPIView):
    queryset = OutApprovePolicy.objects.all()
    serializer_class = OutApprovePolicySerializer

class CbcasOutClipboardPolicyCreate(generics.ListCreateAPIView):
    queryset = OutClipboardPolicy.objects.all()
    serializer_class = OutClipboardPolicySerializer

class CbcasOutSendMailPolicyCreate(generics.ListCreateAPIView):
    queryset = OutSendMailPolicy.objects.all()
    serializer_class = OutSendMailPolicySerializer
    
class CbcasOutReceivedMailPolicyCreate(generics.ListCreateAPIView):
    queryset = OutReceivedMailPolicy.objects.all()
    serializer_class = OutReceivedMailPolicySerializer

class CbcasOutReceptionPolicyCreate(generics.ListCreateAPIView):
    queryset = OutReceptionPolicy.objects.all()
    serializer_class = OutReceptionPolicySerializer

class CbcasOutTransmissionPolicyCreate(generics.ListCreateAPIView):
    queryset = OutTransmissionPolicy.objects.all()
    serializer_class = OutTransmissionPolicySerializer

class CbcasOutPolicyCreate(generics.ListCreateAPIView):
    queryset = OutPolicy.objects.all()
    serializer_class = OutPolicySerializer

class CbcasDataPolicyCreate(generics.ListCreateAPIView):
    queryset = DataPolicy.objects.all()
    serializer_class = DataPolicySerializer
    '''
    def form_valid(self, form):
        comp = form.cleaned_data.get('company')
        #emails = form.cleaned_data.get("share_email_with")
        instance = DataPolicy.objects.create(company=comp)
        instance.company.save()

        return redirect("/")
    '''

# 인사정보
class CbcasCompanyCreate(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class CbcasDepartmentCreate(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class CbcasTeamCreate(generics.ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class CbcasEmployeeCreate(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class CbcasExternalApproverCreate(generics.ListCreateAPIView):
    queryset = ExternalApprover.objects.all()
    serializer_class = ExternalApproverSerializer

class CbcasResourcesCreate(generics.ListCreateAPIView):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer
