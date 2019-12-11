# AWS Sample Lab:  AWS Config


## Lab Summary

The purpose of this repo is to provide a simple set fo AWS CloudFormation Template(s) and other dependant files so that someone with a 'sandbox' AWS account can learn simple functions of the AWS Config Service. 

### Learning Goals

Each exercise in this sample lab will focus on a learning goal.  The goals are:

_Learn How to_ ...

- (1) Automate deployment of AWS Config basic components
- (2) Track changes on a supported AWS resource
- (3) Track if changes to a resource are compliant or not (wip)
- (4) Remediate a change to a resource with a custom lambda function (wip)
- (5) Recieve a notification that a change event has occured on a resource (wip)
- (6) Debug Custom Rule Functions in Lambda (wip)


## Lab Exercises
### (1) Automate deployment of AWS Config

This should be the first exercise to complete in this sample lab.   This exercise will create the required AWS Config components for the rest of the exercises and provide a reference CloudFormation template for you to learn how to create your own automation for AWS Config.   See the image & table below for what will be created in this CloudFormation Stack:

![Config Objects to be Created](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/cf-designer-png-sample-lab-config.png)

Object Name                              | Object Type                          | Object Purpose                                                                                      |
-----------------------------------------|--------------------------------------|-----------------------------------------------------------------------------------------------------|
configbucket                             | AWS::S3::Bucket                      | Bucket that will hold AWS config snapshots & history                                                |
default                                  | AWS::Config::ConfigurationRecorder   | Service to record changes of in scope resource type for AWS Config                                  |
DeliveryChannel                          | AWS::Config::DeliveryChannel         | Destination for AWS Config to publish configuration item data                                       |
ConfigRole                               | AWS::IAM::Role                       | IAM Role that AWS Config will use to record events and pub to delivery channel                      |
LambdaExecutionRole                      | AWS::IAM::Role                       | IAM Role that AWS Config will assume when launching the function associated with custom ConfigRule  |
ConfigRuleForSecurityGroupValidation     | AWS::Config::ConfigRule              | Custom AWS Config Rule that checks SecurityGroup Ingress rules for compliance                       |
ConfigRemediationSecurityGroupValidation | AWS::Config::RemediationConfiguration| Remediation linking a SMS Automation Document to 'fix' non compliant resources from Custom Rule     |
SSMSecurityGroupRemediateDocument        | AWS::SSM::Document                   | SSM Document that will pass non compliant resource ID from config role to lambda function           |
SecurityGroupComplianceCheck             | AWS::Lambda::Function                | Function called by ConfigRule to report on security group compliance of a SecurityGroup             |
SecurityGroupComplianceRemediate         | AWS::Lambda::Function                | Function called by SSM document when a resource remediation is triggered                            |

#### (-) Required Lab Exercises to execute before this one:

- none

#### (-) AWS Account Requirements for This Exercise:

- An AWS Account.  <<<< It is highly suggested to use a test/sandbox account as the lab assumes AWS Config is not currently deployed in the AWS account.
  - If AWS Condfig was previously deployed but not in use, the account must **NOT** have a pre-existing ConfigurationRecorder or DeliveryChannel in the target region as the CF Template will be creating new/default ones.  See this bash [script](https://github.com/virtmerlin/aws-sample-lab-config/blob/master/scripts/remove-config-default-recorders.sh) to determine if your account has existing recorders/channels and how to delete them. 
- A Multi-Region CloudTrail 'Trail' enabled and outputting to a s3 bucket. See this [link](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/receive-cloudtrail-log-files-from-multiple-regions.html) to see how to deploy.
- An IAM user with permissions to create the following AWS resources in the region:

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


#### (-) Exercise Steps:

Create AWS Config Stack.   This stack will deploy AWS Config in such a way that it will only record changes to AWS EC2 Security Groups so that we reduce cost impact in the sandbox account and focus only on a small subset of objects to learn the function of AWS Config

**A**. Launch the CF Template by clicking on the `Launch Stack` button:    [![Launch AWS CONFIG Lab in us-east-1](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=mg-awsconfig-lab&templateURL=https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/AWSConfig-SecurityGroupCompliance.template) 
  
  _Note(s):_ 
  
  - _The embedded url is using us-east-1 as the region,  simply copy the URL from the icon & modify to the desired region you wish to use instead.  All console related links in this repo reffer to us-east-1._
  - _Use an AWS account with the required permisssions to log into the AWS console._
  - _The CF Template takes no input, but you will be required to accept IAM capabilites ... see image below._
  ![IAM Capabilities](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/1-iam-capabilities.png)
  
**B**. Verify AWS Config after the stack is created ...
  ![AWS Config Settings](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/1-settings.png)
  
     - Check your Settings via this [link](https://console.aws.amazon.com/config/home?region=us-east-1#/configure) ...
         - Recording Should be 'ON'
         - Recorder should only be tracking `EC2:SecurityGroup` & `Config:ResourceCompliance` for minimal cost & lab function.   What should you be able to record?  See this [link](https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html) to learn more. 

**C**. Verify That you are tracking SecurityGroup resources ...
  ![Recorded Resources](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/1-resources-recorded.png)
  
  - Check if you have SecurityGroups listed via this [link](https://console.aws.amazon.com/config/home?region=us-east-1#/resources/listing?filter=%7B%22filterType%22:%22resource%22,%22resource%22:%7B%22includeDeletedResources%22:false,%22resourceTypes%22:%5B%22AWS::EC2::SecurityGroup%22%5D,%22resourceIdentifier%22:%22%22%7D,%22tag%22:%7B%22tagKey%22:%22%22,%22tagValue%22:%22%22%7D,%22compliance%22:%7B%22value%22:%22%22,%22text%22:%22Compliance%20status%22%7D%7D) ...
  - If you dont see any SecurityGroups, verify at least 1 exists in your region in any vpc.  If not then create one.   You may see differing compliance states from the image above.
  - If you create a group,  it doesnt matter at this time what the Ingress rules are as you will modify them in following exercises.

### (2) Track changes on a supported AWS resource

In this exercise you will make changes to an EC2:SecurityGroup and track what the changes were and who made them.  We will look at a few conceptual items in AWS Config to do this:

AWS Config Concept/Object | Object Purpose                                                                                                                                                                      |
--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
ConfigRule                | A defined set of conditions to be compared against a resource's Configuration Item to determine if the resource is compliant or not.  Can be AWS provided or Custom.                |
Configuration Item        | A point in time snapshot of the state of a resource after it has been changed.  It will show many things, among them the state before & after the change.                           |
Configuration Timeline    | A linear presentation of all Configuration Items recorded for a given resource sorted in timestamped order.                                                                         |
Compliance Timeline       | A linear presentation of the compliance state of the resource ina red/green format.  Its based on if the state of the resource complied to the ConfigRules it was evaulated against.|
Related CloudTrail Event  | A related CloudTrail Logging event to the recorded Change Item on a resource showing data about who, how, & when the change was made.                                               |

The deployed stack created a single custom ConfigRule `ConfigRuleForSecurityGroupValidation`.  AWS provides managed rules that do not require advanced programming skills,  but this sample lab will reference a custom rule in a effort to demonstrate how to ensure compliance for secnarios not covered in the AWS managed rules.

Custom Compliance Scenario:

- In this lab compliance scenario, the custom ConfigRule compliance is based on a python lambda function using the boto3 python libs.   The rule uses a hardcoded set of SecurityGroup Ingress Rules embedded in the function:
	-  REQUIRED_PERMISSIONS: A set of Ingress Rules that must exist in each security group the rule applies to (In this case SSH TCP 22 from Anywhere)
	-  DENIED_PERMISSIONS: A set of Ingress Rules the must not exist in each security group the rule applies to (In this case HTTP TCP 80 from Anywhere)
![Embedded Ingress Rules](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-rule-embedded-compliance.png)
If a SecurityGroup has any DENIED || _or_ || does NOT have any REQUIRED Ingress rules,  when the resource is evaluated by the rule, it will report as NonCompliant

#### (-) Required Lab Exercises to execute before this one:

- (1) Automate deployment of AWS Config

#### (-) AWS Account Requirements for This Exercise:

- Same as: (1) Automate deployment of AWS Config

#### (-) Exercise Steps:
**A**. Determine How the Rule evaluation is triggered ...
  
  - Open this [link](https://console.aws.amazon.com/config/home?region=us-east-1#/rules/rule-details/ConfigRuleForSecurityGroupValidation) to review what triggers the evaluation of the custom ConfigRule ...
  ![Rule Settings](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-rule-settings.png)
    - The evaluation should be set to _Configuration Changes_ meaning any time an in-scope resource is changed, it will be evaluated.
    - Scope of changes is set to resources only of Type _Ec2:SecurityGroup_ meaning the rule will only evaluate if a SecurityGroup is changed.
    - Make note of the last successful evaluation timestamp, you will want to see that it has triggered once you make a change to a SecurityGroup.
  
**B**. Make a change to a Security Group ...
  
  - Navigate to your EC2 Service and add the following _Allow HTTP from Anywhere_ ingress rule to your SecurityGroup:
  ![Add HTTP to Rule](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-add-http.png)
  
**C**. Check that the Evaluation Triggered ...

  - Navigate back to this [link](https://console.aws.amazon.com/config/home?region=us-east-1#/rules/rule-details/ConfigRuleForSecurityGroupValidation) showing your ConfigRule status to verify that the _Last Successful Evalution_ has triggered again.  It may take ~1-5 minutes to trigger, so refresh the screen to check status timestamp until it does (Or Alternaitvely you can look at the CloudWatch Log Group for the SecurityGroupComplianceCheck Lambda function) 
  
**D**. Look at the Configuration Item ...

  - Once you see that the evaluation has triggered, you should also see the SecurityGroup you just edited report as _NonCompliant_ like the example SecurityGroup (sg-03658ef4ee6463aad) in the image below ...
  ![NonCompliant](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-non-compliant.png)
  - Click on the _Resource ID_ Hyperlink & then click on the _Configuration Timeline_ button in the upper right corner of the console...
  ![ConfigTimeLine](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-config-timeline.png)
  - Click the _Now_ button on the Timeline to view the latest recorded change which should match your recent update timestamp, if not refresh the page until it shows (1-3 minutes) ...
  ![LatestCI](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-now.png)
  - Expand the _Changes_ diamond to see what change was recorded, it should be the HTTP Ingress rule addition.
  ![LatestCI](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-added.png)

**E**. Look at the CloudTrail Event ...
  
  - Expand the _CloudTrail Events_ diamond to see who made the change,  This requires that a CloudTrail multi-region trail is enabled in the account.  IT WILL TAKE UP TO 15 MINUTES AFTER the change was recorded for the event to appear.  Refresh the web page after 15 minutes to see the related CloudTrail Event to see who performed the change (in this case root).
  ![LatestCI](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-ctrail-event.png) 
  
**F**. Look at the Compliance Timeline ...

  - Navigate back to the _Resource ID_ & then click on the _Compliance Timeline_ button in the upper right corner of the console...
  ![ConfigTimeLine](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-config-timeline.png)
  - Notice the current compliance is RED since you have added HTTP to the Ingress Rules ...
  ![ConfigTimeLine](https://mglab-aws-samples.s3.amazonaws.com/aws-sample-lab-config/images/2-compliance-timeline.png)
  
  
**G**.  Use what you have learned to change your secuerity Group state back to _Compliant_