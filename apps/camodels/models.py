from django.db import models
from .modelsframe.personnel import Company, Department, Employee
from .modelsframe.policy import InFilesPolicy, InExternalServicePolicy, InApprovePolicy, InClipboardPolicy, InWebProxyPolicy, InSendMailPolicy, InReceivedMailPolicy, InReceptionPolicy, InTransmissionPolicy, InPolicy, OutFilesPolicy, OutExternalServicePolicy, OutApprovePolicy, OutClipboardPolicy, OutSendMailPolicy, OutReceivedMailPolicy, OutReceptionPolicy, OutTransmissionPolicy, OutPolicy, DataPolicy, URLPolicy, URLWhitePolicy, URLBlackPolicy, URLExceptionPolicy, DataPolicyforEmployee, URLPolicyforEmployee
from .policySerializers import DataPolicySerializer
from .employeeSerializers import EmployeeSerializer
from rest_framework import generics

######################
##   Models  Main   ## 
######################
