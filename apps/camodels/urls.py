from django.conf.urls import include, url
from django.urls import path
from . import views
# When use Development server
from django.conf.urls.static import static

urlpatterns = [
	path('infiles', views.CbcasInFilesPolicyCreate.as_view() ),
	path('inexternalservice', views.CbcasInExternalServicePolicyCreate.as_view() ),
	path('inapprove', views.CbcasInApprovePolicyCreate.as_view() ),
	path('inclipboard', views.CbcasInClipboardPolicyCreate.as_view() ),
	path('inwebproxy', views.CbcasInWebProxyPolicyCreate.as_view() ),
	path('insendmail', views.CbcasInSendMailPolicyCreate.as_view() ),
	path('inreceivedmail', views.CbcasInReceivedMailPolicyCreate.as_view() ),
	path('inreception', views.CbcasInReceptionPolicyCreate.as_view() ),
	path('intrans', views.CbcasInTransmissionPolicyCreate.as_view() ),
	path('in', views.CbcasInPolicyCreate.as_view() ),
	path('outtrans', views.CbcasOutTransmissionPolicyCreate.as_view() ),
	path('outfiles', views.CbcasOutFilesPolicyCreate.as_view() ),
	path('outexternalservice', views.CbcasOutExternalServicePolicyCreate.as_view() ),
	path('outapprove', views.CbcasOutApprovePolicyCreate.as_view() ),
	path('outclipboard', views.CbcasOutClipboardPolicyCreate.as_view() ),
	path('outsendmail', views.CbcasOutSendMailPolicyCreate.as_view() ),
	path('outreceivedmail', views.CbcasOutReceivedMailPolicyCreate.as_view() ),
	path('outreception', views.CbcasOutReceptionPolicyCreate.as_view() ),
	path('outtrans', views.CbcasOutTransmissionPolicyCreate.as_view() ),
	path('out', views.CbcasOutPolicyCreate.as_view() ),
	path('data', views.CbcasDataPolicyCreate.as_view() ),

	path('company', views.CbcasCompanyCreate.as_view() ),
	path('department', views.CbcasDepartmentCreate.as_view() ),
	path('team', views.CbcasTeamCreate.as_view() ),
	path('employee', views.CbcasEmployeeCreate.as_view() ),
	path('externalapprover', views.CbcasExternalApproverCreate.as_view() ),
	path('resources', views.CbcasResourcesCreate.as_view() ),
]
