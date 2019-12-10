# AWS Sample Lab:  AWS Config


## Lab Summary

The purpose of this repo is to provide a simple set fo AWS CloudFormation Template(s) and other dependant files so that someone with a 'sandbox' AWS account can learn simple functions of the AWS Config Service. 

### Learning Goals

Learn How to ...

- Automate deployment of AWS Config basic components
- Track changes on a supported AWS Resource
- Track if changes to a resource are compliant or not
- Remediate a change
- Recieve a notification that a change event has occured on tracked resource


## Lab Exercises
### (1) Automate deployment of AWS Config

This should be the first exercise to complete in this sample lab.   This exercise will create the required AWS Config components for the rest of the exercises and provide a refernce CloudFormation template for you to learn how to create automation for AWS Config.   See the image & table below for what will be created:

![Config Objects to be Created](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/cf-designer-png-sample-lab-config.png)

Object Name                              | Object Type                          | Object Purpose                                                                                  |
-----------------------------------------|--------------------------------------|-------------------------------------------------------------------------------------------------|
configbucket                             | AWS::S3::Bucket                      | Bucket that will hold AWS config Snapshots & History                                            |
default                                  | AWS::Config::ConfigurationRecorder   | Service to record changes to in scope items for AWS Config                                      |
DeliveryChannel                          | AWS::Config::DeliveryChannel         | Destination for AWS Config to pub configuration item data                                       |
ConfigRole                               | AWS::IAM::Role                       | Role that AWS Config will use to record events and pub to delivery channel                      |
LambdaExecutionRole                      | AWS::IAM::Role                       | Role that AWS Config will reffer to to launch the provided function in the CF template          |
ConfigRuleForSecurityGroupValidation     | AWS::Config::ConfigRule              | Custom AWS Config Rule that checks SecurityGroup Ingress Rules for compliance                   |
ConfigRemediationSecurityGroupValidation | AWS::Config::RemediationConfiguration| Remediation linking a SMS Automation Document to 'fix' non compliant resources from Custom Rule |
SSMSecurityGroupRemediateDocument        | AWS::SSM::Document                   | SSM Document that will pass non compliant resource ID from config role to lambda function       |
SecurityGroupComplianceCheck             | AWS::Lambda::Function                | Function called by ConfigRule to report on security group compliance of a SecurityGroup         |
SecurityGroupComplianceRemediate         | AWS::Lambda::Function                | Function called by SSM document when a resource remediation is triggered                        |

#### (-) Required Lab Exercises

- none

#### (-) AWS Account Requirements for This Exercise

- An AWS Account.  <<<< It is highly suggested to use a test/sandbox account
- A Mulit-Region CloudTrail Trail enabled and outputting to a s3 bucket [link](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/receive-cloudtrail-log-files-from-multiple-regions.html)
- An IAM user with permissions to create the following AWS resources:

  - AWS::CloudFormation::Stack
  - AWS::Config::ConfigRule
  - AWS::Config::ConfigurationRecorder
  - AWS::Config::DeliveryChannel
  - AWS::Config::RemediationConfiguration
  - AWS::IAM::Role
  - AWS::Lambda::Function
  - AWS::Lambda::Permission
  - AWS::S3::Bucket
  - AWS::SSM::Document

[![Launch AWS CONFIG Lab in us-east-1](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=mg-awsconfig-lab&templateURL=https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/AWSConfig-SecurityGroupCompliance.template)



