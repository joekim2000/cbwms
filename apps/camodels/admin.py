from django.contrib import admin

# Register your models here.
from .modelsframe.personnel import Company, Department, Employee
from .modelsframe.policy import InFilesPolicy, InExternalServicePolicy, InApprovePolicy, InClipboardPolicy, InWebProxyPolicy, InSendMailPolicy, InReceivedMailPolicy, InReceptionPolicy, InTransmissionPolicy, InPolicy, OutFilesPolicy, OutExternalServicePolicy, OutApprovePolicy, OutClipboardPolicy, OutSendMailPolicy, OutReceivedMailPolicy, OutReceptionPolicy, OutTransmissionPolicy, OutPolicy, DataPolicy, URLPolicy, URLWhitePolicy, URLBlackPolicy, URLExceptionPolicy, DataPolicyforEmployee, URLPolicyforEmployee

admin.site.register(InFilesPolicy)
admin.site.register(InExternalServicePolicy)
admin.site.register(InApprovePolicy)
admin.site.register(InClipboardPolicy)
admin.site.register(InWebProxyPolicy)
admin.site.register(InSendMailPolicy)
admin.site.register(InReceivedMailPolicy)
admin.site.register(InReceptionPolicy)
admin.site.register(InTransmissionPolicy)
admin.site.register(InPolicy)

admin.site.register(OutFilesPolicy)
admin.site.register(OutExternalServicePolicy)
admin.site.register(OutApprovePolicy)
admin.site.register(OutClipboardPolicy)
admin.site.register(OutSendMailPolicy)
admin.site.register(OutReceivedMailPolicy)
admin.site.register(OutReceptionPolicy)
admin.site.register(OutTransmissionPolicy)
admin.site.register(OutPolicy)

admin.site.register(DataPolicy)

admin.site.register(Company)
admin.site.register(Department)
admin.site.register(Employee)
